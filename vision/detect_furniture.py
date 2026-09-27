import sys
import json
import os
import math
from pathlib import Path
from collections import Counter
from contextlib import redirect_stdout

import cv2
import torch

from ultralytics import YOLOE

from inventory_classes import (
    INVENTORY_CLASS_SET,
    DETECTION_GROUPS,
    conflict_family_for,
)


# ============================================================
# PATHS
# ============================================================


SCRIPT_DIR = (
    Path(__file__)
    .resolve()
    .parent
)

DEBUG_DIR = (
    SCRIPT_DIR /
    "debug"
)

DEBUG_DIR.mkdir(
    exist_ok=True
)

os.chdir(
    SCRIPT_DIR
)


# ============================================================
# MODEL CONFIG
# ============================================================


MODEL_NAME = "yoloe-26n-seg.pt"

#
# 0.20 gave us too many false positives.
# 0.25 missed some small objects.
#
# 0.22 is our current compromise.
#

CONFIDENCE_THRESHOLD = 0.22

IOU_THRESHOLD = 0.45

IMAGE_SIZE = 768

MAX_DETECTIONS_PER_GROUP = 75


# ============================================================
# CROSS-CLASS DEDUP
# ============================================================


CONFLICT_IOU_THRESHOLD = 0.55


# ============================================================
# OBJECT MEMORY / TRACKING
# ============================================================
#
# Frames currently come every 2 seconds.
#
# TRACK_MAX_GAP_FRAMES = 2 means:
#
# same physical object can temporarily disappear
# for roughly 4 seconds and still be considered
# the same object.
#
# After that the ACTIVE track is forgotten,
# allowing another bed/chair/etc. later in the
# house to be counted as a new physical item.
#
# We forget the OBJECT TRACK.
# We NEVER forget the CLASS.
# ============================================================


TRACK_MAX_GAP_FRAMES = 2

TRACK_MIN_IOU = 0.08

TRACK_MAX_CENTER_DISTANCE = 0.30

TRACK_MIN_AREA_SIMILARITY = 0.35


# ============================================================
# SINGLE-FRAME FALSE POSITIVE FILTER
# ============================================================
#
# If an object only appears once in the entire
# tracking episode, we require a slightly stronger
# confidence.
#
# Objects seen multiple times are trusted more.
# ============================================================


SINGLE_FRAME_MIN_CONFIDENCE = 0.32


# ============================================================
# DEVICE
# ============================================================


DEVICE = (
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)


# ============================================================
# HELPERS
# ============================================================


def clear_debug_directory():

    for file_path in DEBUG_DIR.glob(
        "*.jpg"
    ):

        try:

            file_path.unlink()

        except OSError:

            pass


def box_area(box):

    width = max(
        0.0,
        box[2] - box[0]
    )

    height = max(
        0.0,
        box[3] - box[1]
    )

    return (
        width *
        height
    )


def calculate_iou(
    first,
    second
):

    x1 = max(
        first[0],
        second[0]
    )

    y1 = max(
        first[1],
        second[1]
    )

    x2 = min(
        first[2],
        second[2]
    )

    y2 = min(
        first[3],
        second[3]
    )

    intersection_width = max(
        0.0,
        x2 - x1
    )

    intersection_height = max(
        0.0,
        y2 - y1
    )

    intersection = (
        intersection_width *
        intersection_height
    )

    first_area = box_area(
        first
    )

    second_area = box_area(
        second
    )

    union = (
        first_area +
        second_area -
        intersection
    )

    if union <= 0:

        return 0.0

    return (
        intersection /
        union
    )


def center_distance(
    first,
    second,
    frame_width,
    frame_height
):

    first_x = (
        first[0] +
        first[2]
    ) / 2.0

    first_y = (
        first[1] +
        first[3]
    ) / 2.0

    second_x = (
        second[0] +
        second[2]
    ) / 2.0

    second_y = (
        second[1] +
        second[3]
    ) / 2.0

    distance = math.sqrt(
        (
            first_x -
            second_x
        ) ** 2
        +
        (
            first_y -
            second_y
        ) ** 2
    )

    diagonal = math.sqrt(
        frame_width ** 2 +
        frame_height ** 2
    )

    if diagonal <= 0:

        return 1.0

    return (
        distance /
        diagonal
    )


def area_similarity(
    first,
    second
):

    first_area = box_area(
        first
    )

    second_area = box_area(
        second
    )

    maximum = max(
        first_area,
        second_area
    )

    if maximum <= 0:

        return 0.0

    return (
        min(
            first_area,
            second_area
        )
        /
        maximum
    )


# ============================================================
# MODEL
# ============================================================


def load_model():

    print(
        f"Loading {MODEL_NAME} on {DEVICE}...",
        file=sys.stderr
    )

    with redirect_stdout(
        sys.stderr
    ):

        model = YOLOE(
            MODEL_NAME
        )

    print(
        "YOLOE model loaded.",
        file=sys.stderr
    )

    return model


# ============================================================
# READ ONE YOLO RESULT
# ============================================================


def parse_result(
    result,
    group_name
):

    detections = []

    if result.boxes is None:

        return detections

    for box in result.boxes:

        class_id = int(
            box.cls.item()
        )

        confidence = float(
            box.conf.item()
        )

        name = (
            str(
                result.names[
                    class_id
                ]
            )
            .lower()
            .strip()
        )

        if name not in INVENTORY_CLASS_SET:

            continue

        coordinates = (
            box.xyxy[0]
            .detach()
            .cpu()
            .tolist()
        )

        detections.append({
            "name":
                name,

            "confidence":
                confidence,

            "box":
                coordinates,

            "group":
                group_name,
        })

    return detections


# ============================================================
# RUN EVERY GROUP ACROSS EVERY FRAME
# ============================================================
#
# Important efficiency detail:
#
# BAD:
#
# frame 1 -> set_classes
# frame 2 -> set_classes
# frame 3 -> set_classes
#
# GOOD:
#
# set_classes(group)
# -> scan ALL frames
#
# Then move to the next group.
#
# We only calculate text prompts once per group.
# ============================================================


def detect_all_groups(
    model,
    frame_files
):

    raw_by_frame = {
        frame_file.name: []
        for frame_file
        in frame_files
    }

    frame_sizes = {}

    total_groups = len(
        DETECTION_GROUPS
    )

    for group_index, (
        group_name,
        classes
    ) in enumerate(
        DETECTION_GROUPS.items(),
        start=1
    ):

        print(
            f"Group {group_index}/{total_groups}: "
            f"{group_name} "
            f"({len(classes)} classes)",
            file=sys.stderr
        )

        with redirect_stdout(
            sys.stderr
        ):

            model.set_classes(
                classes
            )

            results = model.predict(
                source=[
                    str(frame_file)
                    for frame_file
                    in frame_files
                ],

                conf=CONFIDENCE_THRESHOLD,

                iou=IOU_THRESHOLD,

                imgsz=IMAGE_SIZE,

                device=DEVICE,

                verbose=False,

                agnostic_nms=True,

                max_det=MAX_DETECTIONS_PER_GROUP,
            )

        if len(results) != len(
            frame_files
        ):

            raise RuntimeError(
                "YOLOE result count does not match "
                "frame count."
            )

        for frame_file, result in zip(
            frame_files,
            results
        ):

            height, width = (
                result.orig_shape
            )

            frame_sizes[
                frame_file.name
            ] = (
                width,
                height
            )

            raw_by_frame[
                frame_file.name
            ].extend(
                parse_result(
                    result,
                    group_name
                )
            )

    return (
        raw_by_frame,
        frame_sizes
    )


# ============================================================
# PER-FRAME DEDUPLICATION
# ============================================================


def same_conflict_family(
    first_name,
    second_name
):

    return (
        conflict_family_for(
            first_name
        )
        ==
        conflict_family_for(
            second_name
        )
    )


def deduplicate_frame(
    detections
):

    if not detections:

        return []

    detections = sorted(
        detections,
        key=lambda item:
            item[
                "confidence"
            ],
        reverse=True
    )

    accepted = []

    for candidate in detections:

        duplicate = False

        for existing in accepted:

            overlap = calculate_iou(
                candidate["box"],
                existing["box"]
            )

            #
            # Exact same label + same physical area.
            #

            if (
                candidate["name"]
                ==
                existing["name"]
                and
                overlap >= 0.50
            ):

                duplicate = True
                break

            #
            # Semantic competitors.
            #
            # Example:
            #
            # sofa 0.61
            # loveseat 0.40
            #
            # on essentially the same object.
            #

            if (
                same_conflict_family(
                    candidate["name"],
                    existing["name"]
                )
                and
                overlap >=
                CONFLICT_IOU_THRESHOLD
            ):

                duplicate = True
                break

        if not duplicate:

            accepted.append(
                candidate
            )

    return accepted


# ============================================================
# TRACKING
# ============================================================


def can_match_track(
    detection,
    track,
    frame_width,
    frame_height
):

    #
    # Same exact label OR same semantic family.
    #

    if (
        conflict_family_for(
            detection["name"]
        )
        !=
        track[
            "family"
        ]
    ):

        return False

    overlap = calculate_iou(
        detection["box"],
        track["last_box"]
    )

    if overlap >= TRACK_MIN_IOU:

        return True

    distance = center_distance(
        detection["box"],
        track["last_box"],
        frame_width,
        frame_height
    )

    size_similarity = (
        area_similarity(
            detection["box"],
            track["last_box"]
        )
    )

    if (
        distance <=
        TRACK_MAX_CENTER_DISTANCE
        and
        size_similarity >=
        TRACK_MIN_AREA_SIMILARITY
    ):

        return True

    return False


def track_objects(
    frame_files,
    frame_detections,
    frame_sizes
):

    active_tracks = []

    all_tracks = []

    next_object_id = 1

    for frame_index, frame_file in enumerate(
        frame_files
    ):

        frame_name = (
            frame_file.name
        )

        frame_width, frame_height = (
            frame_sizes[
                frame_name
            ]
        )

        detections = (
            frame_detections[
                frame_name
            ]
        )

        #
        # Forget old ACTIVE tracks.
        #
        # This is important:
        #
        # We forget the physical object's tracking
        # state once it has disappeared long enough.
        #
        # That allows a SECOND bed/chair/etc. later
        # in the house to be counted.
        #

        active_tracks = [
            track
            for track
            in active_tracks
            if (
                frame_index -
                track[
                    "last_seen_frame"
                ]
            )
            <=
            TRACK_MAX_GAP_FRAMES
        ]

        matched_track_ids = set()

        detections = sorted(
            detections,
            key=lambda item:
                item[
                    "confidence"
                ],
            reverse=True
        )

        for detection in detections:

            best_track = None

            best_score = -1.0

            for track in active_tracks:

                if (
                    track["object_id"]
                    in
                    matched_track_ids
                ):

                    continue

                if not can_match_track(
                    detection,
                    track,
                    frame_width,
                    frame_height
                ):

                    continue

                overlap = calculate_iou(
                    detection["box"],
                    track["last_box"]
                )

                distance = center_distance(
                    detection["box"],
                    track["last_box"],
                    frame_width,
                    frame_height
                )

                similarity = (
                    area_similarity(
                        detection["box"],
                        track["last_box"]
                    )
                )

                match_score = (
                    overlap * 3.0
                    +
                    (
                        1.0 -
                        distance
                    )
                    +
                    similarity
                )

                if match_score > best_score:

                    best_score = (
                        match_score
                    )

                    best_track = (
                        track
                    )

            #
            # Existing physical object.
            #
            # Do NOT increase quantity.
            #

            if best_track is not None:

                best_track[
                    "last_box"
                ] = detection[
                    "box"
                ]

                best_track[
                    "last_seen_frame"
                ] = frame_index

                best_track[
                    "hits"
                ] += 1

                best_track[
                    "confidence_sum"
                ] += detection[
                    "confidence"
                ]

                #
                # Allow a more confident subtype to win.
                #
                # Example:
                #
                # first:
                # chair 0.31
                #
                # later:
                # office chair 0.63
                #

                if (
                    detection[
                        "confidence"
                    ]
                    >
                    best_track[
                        "best_confidence"
                    ]
                ):

                    best_track[
                        "best_confidence"
                    ] = detection[
                        "confidence"
                    ]

                    best_track[
                        "best_name"
                    ] = detection[
                        "name"
                    ]

                matched_track_ids.add(
                    best_track[
                        "object_id"
                    ]
                )

                continue

            #
            # NEW physical object.
            #

            new_track = {
                "object_id":
                    next_object_id,

                "family":
                    conflict_family_for(
                        detection[
                            "name"
                        ]
                    ),

                "best_name":
                    detection[
                        "name"
                    ],

                "best_confidence":
                    detection[
                        "confidence"
                    ],

                "confidence_sum":
                    detection[
                        "confidence"
                    ],

                "hits":
                    1,

                "first_seen_frame":
                    frame_index,

                "last_seen_frame":
                    frame_index,

                "last_box":
                    detection[
                        "box"
                    ],
            }

            next_object_id += 1

            active_tracks.append(
                new_track
            )

            all_tracks.append(
                new_track
            )

            matched_track_ids.add(
                new_track[
                    "object_id"
                ]
            )

    return all_tracks


# ============================================================
# FILTER WEAK SINGLE-FRAME OBJECTS
# ============================================================


def filter_tracks(
    tracks
):

    valid = []

    for track in tracks:

        #
        # Seen multiple times:
        # strong temporal confirmation.
        #

        if track["hits"] >= 2:

            valid.append(
                track
            )

            continue

        #
        # Seen only once:
        # require stronger confidence.
        #

        if (
            track[
                "best_confidence"
            ]
            >=
            SINGLE_FRAME_MIN_CONFIDENCE
        ):

            valid.append(
                track
            )

    return valid


# ============================================================
# DEBUG IMAGE
# ============================================================


def save_debug_frame(
    frame_file,
    detections
):

    image = cv2.imread(
        str(
            frame_file
        )
    )

    if image is None:

        return

    for detection in detections:

        x1, y1, x2, y2 = [
            int(value)
            for value
            in detection[
                "box"
            ]
        ]

        name = detection[
            "name"
        ]

        confidence = detection[
            "confidence"
        ]

        cv2.rectangle(
            image,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),
            2
        )

        label = (
            f"{name} "
            f"{confidence:.2f}"
        )

        cv2.putText(
            image,
            label,
            (
                x1,
                max(
                    20,
                    y1 - 8
                )
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 255, 0),
            2,
            cv2.LINE_AA
        )

    output_path = (
        DEBUG_DIR /
        frame_file.name
    )

    cv2.imwrite(
        str(
            output_path
        ),
        image
    )


# ============================================================
# MAIN ANALYSIS
# ============================================================


def analyze_frames(
    frames_directory
):

    frames_path = Path(
        frames_directory
    )

    if not frames_path.exists():

        raise FileNotFoundError(
            "Frames directory does not exist: "
            f"{frames_directory}"
        )

    frame_files = sorted(
        frames_path.glob(
            "*.jpg"
        )
    )

    if not frame_files:

        raise RuntimeError(
            "No JPG frames found."
        )

    clear_debug_directory()

    model = load_model()

    #
    # Step 1:
    # scan every frame with every semantic group.
    #

    raw_by_frame, frame_sizes = (
        detect_all_groups(
            model,
            frame_files
        )
    )

    #
    # Step 2:
    # merge/suppress conflicting detections.
    #

    frame_detections = {}

    frame_results = []

    for frame_file in frame_files:

        cleaned = deduplicate_frame(
            raw_by_frame[
                frame_file.name
            ]
        )

        frame_detections[
            frame_file.name
        ] = cleaned

        save_debug_frame(
            frame_file,
            cleaned
        )

        counts = Counter(
            detection[
                "name"
            ]
            for detection
            in cleaned
        )

        frame_results.append({
            "frame":
                frame_file.name,

            "detections":
                dict(
                    sorted(
                        counts.items()
                    )
                )
        })

    #
    # Step 3:
    # physical-object tracking.
    #
    # Same bed in multiple nearby frames
    # becomes ONE object.
    #

    tracks = track_objects(
        frame_files,
        frame_detections,
        frame_sizes
    )

    #
    # Step 4:
    # remove weak one-frame hallucinations.
    #

    tracks = filter_tracks(
        tracks
    )

    #
    # Step 5:
    # final moving inventory.
    #

    final_counts = Counter(
        track[
            "best_name"
        ]
        for track
        in tracks
    )

    items = [
        {
            "name":
                name,

            "quantity":
                quantity,
        }

        for name, quantity
        in sorted(
            final_counts.items()
        )
    ]

    return {
        "framesProcessed":
            len(frame_files),

        "confidenceThreshold":
            CONFIDENCE_THRESHOLD,

        "items":
            items,

        "frames":
            frame_results,
    }


# ============================================================
# CLI
# ============================================================


def main():

    if len(sys.argv) != 2:

        print(
            json.dumps({
                "error":
                    "Usage: "
                    "python detect_furniture.py "
                    "<frames_directory>"
            })
        )

        sys.exit(1)

    frames_directory = (
        sys.argv[1]
    )

    try:

        result = analyze_frames(
            frames_directory
        )

        #
        # ONLY JSON goes to stdout.
        #
        # Spring Boot reads this.
        #

        print(
            json.dumps(
                result,
                ensure_ascii=False
            )
        )

    except Exception as exception:

        print(
            json.dumps({
                "error":
                    str(exception)
            })
        )

        sys.exit(1)


if __name__ == "__main__":
    main()