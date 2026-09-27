import sys
import json
from pathlib import Path
from collections import Counter

import torch
from PIL import Image
from torchvision.models.detection import (
    fasterrcnn_resnet50_fpn_v2,
    FasterRCNN_ResNet50_FPN_V2_Weights,
)

CONFIDENCE_THRESHOLD = 0.65

FURNITURE_CLASSES = {
    "chair": "chair",
    "couch": "sofa",
    "bed": "bed",
    "dining table": "dining table",
    "tv": "tv",
    "refrigerator": "refrigerator",
    "microwave": "microwave",
    "oven": "oven",
    "sink": "sink",
}


def load_model():
    weights = FasterRCNN_ResNet50_FPN_V2_Weights.DEFAULT

    model = fasterrcnn_resnet50_fpn_v2(
        weights=weights
    )

    model.eval()

    return model, weights


def detect_frame(image_path, model, weights):
    image = Image.open(image_path).convert("RGB")

    transform = weights.transforms()
    image_tensor = transform(image)

    with torch.no_grad():
        prediction = model([image_tensor])[0]

    categories = weights.meta["categories"]

    detections = []

    for label_id, score in zip(
        prediction["labels"],
        prediction["scores"]
    ):
        confidence = float(score)

        if confidence < CONFIDENCE_THRESHOLD:
            continue

        category = categories[int(label_id)]

        if category not in FURNITURE_CLASSES:
            continue

        detections.append(
            FURNITURE_CLASSES[category]
        )

    return detections


def analyze_frames(frames_directory):
    frames_path = Path(frames_directory)

    if not frames_path.exists():
        raise FileNotFoundError(
            f"Frames directory does not exist: {frames_directory}"
        )

    frame_files = sorted(
        frames_path.glob("*.jpg")
    )

    if not frame_files:
        raise RuntimeError(
            "No JPG frames found."
        )

    model, weights = load_model()

    final_counts = Counter()
    frame_results = []

    for frame_file in frame_files:

        detections = detect_frame(
            frame_file,
            model,
            weights
        )

        frame_counts = Counter(detections)

        frame_results.append({
            "frame": frame_file.name,
            "detections": dict(frame_counts)
        })

        # Ne sabiramo isti predmet preko svih frameova.
        # Za sada uzimamo najveći broj viđen u jednom frame-u.
        for name, quantity in frame_counts.items():
            final_counts[name] = max(
                final_counts[name],
                quantity
            )

    items = []

    for name, quantity in sorted(
        final_counts.items()
    ):
        items.append({
            "name": name,
            "quantity": quantity
        })

    return {
        "framesProcessed": len(frame_files),
        "confidenceThreshold": CONFIDENCE_THRESHOLD,
        "items": items,
        "frames": frame_results
    }


def main():
    if len(sys.argv) != 2:
        print(json.dumps({
            "error":
            "Usage: python detect_furniture.py <frames_directory>"
        }))
        sys.exit(1)

    frames_directory = sys.argv[1]

    try:
        result = analyze_frames(
            frames_directory
        )

        print(
            json.dumps(
                result,
                ensure_ascii=False
            )
        )

    except Exception as exception:
        print(json.dumps({
            "error": str(exception)
        }))
        sys.exit(1)


if __name__ == "__main__":
    main()