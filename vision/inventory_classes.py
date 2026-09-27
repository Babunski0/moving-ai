# ============================================================
# MOVING AI - MASTER INVENTORY CATALOG
# ============================================================
#
# Exactly 200 supported moving-inventory categories.
#
# INVENTORY_CLASSES:
#   Final master catalog.
#
# DETECTION_GROUPS:
#   Smaller semantic groups sent to YOLOE.
#   EVERY group scans EVERY frame.
#
# CONFLICT_FAMILIES:
#   Similar labels that may describe the same physical object.
#   Example:
#       sofa / loveseat / sectional sofa
#
# ============================================================


INVENTORY_CLASSES = [
    "bed",
    "mattress",
    "box spring",
    "nightstand",
    "dresser",
    "sofa",
    "chair",
    "dining table",
    "dining chair",
    "coffee table",
    "tv",
    "tv stand",
    "desk",
    "office chair",
    "wardrobe",
    "bookshelf",
    "lamp",
    "floor lamp",
    "table lamp",
    "mirror",
    "rug",
    "ottoman",
    "bench",
    "recliner",
    "loveseat",
    "sectional sofa",
    "end table",
    "side table",
    "console table",
    "chest of drawers",
    "headboard",
    "bed frame",
    "crib",
    "changing table",
    "rocking chair",
    "bar stool",
    "kitchen stool",
    "kitchen table",
    "kitchen chair",
    "buffet",
    "sideboard",
    "china cabinet",
    "display cabinet",
    "cabinet",
    "storage cabinet",
    "filing cabinet",
    "storage shelf",
    "wall shelf",
    "bookcase",
    "shoe rack",
    "coat rack",
    "entryway bench",
    "hall tree",
    "vanity",
    "vanity stool",
    "makeup table",
    "computer desk",
    "writing desk",
    "standing desk",
    "desk drawer unit",
    "printer stand",
    "computer monitor",
    "desktop computer",
    "laptop",
    "printer",
    "speaker",
    "soundbar",
    "subwoofer",
    "stereo system",
    "record player",
    "gaming console",
    "gaming chair",
    "entertainment center",
    "media cabinet",
    "fireplace console",
    "armchair",
    "accent chair",
    "lounge chair",
    "chaise lounge",
    "futon",
    "sofa bed",
    "daybed",
    "bunk bed",
    "trundle bed",
    "platform bed",
    "adjustable bed",
    "king mattress",
    "queen mattress",
    "full mattress",
    "twin mattress",
    "california king mattress",
    "mattress topper",
    "bedroom bench",
    "chest",
    "storage chest",
    "trunk",
    "armoire",
    "jewelry armoire",
    "tall dresser",
    "low dresser",
    "dining bench",
    "bar table",
    "bar cart",
    "kitchen island",
    "kitchen cart",
    "pantry cabinet",
    "microwave cart",
    "baker's rack",
    "wine rack",
    "wine cabinet",
    "refrigerator",
    "mini refrigerator",
    "freezer",
    "microwave",
    "oven",
    "stove",
    "dishwasher",
    "washing machine",
    "dryer",
    "washer-dryer combo",
    "chest freezer",
    "water cooler",
    "portable air conditioner",
    "window air conditioner",
    "fan",
    "ceiling fan",
    "space heater",
    "air purifier",
    "dehumidifier",
    "humidifier",
    "vacuum cleaner",
    "robot vacuum",
    "ironing board",
    "laundry hamper",
    "laundry basket",
    "clothes rack",
    "garment rack",
    "folding table",
    "folding chair",
    "card table",
    "workbench",
    "tool cabinet",
    "tool chest",
    "storage rack",
    "garage shelf",
    "bicycle",
    "exercise bike",
    "treadmill",
    "elliptical machine",
    "rowing machine",
    "weight bench",
    "dumbbell rack",
    "home gym machine",
    "yoga equipment rack",
    "piano",
    "upright piano",
    "grand piano",
    "keyboard piano",
    "guitar",
    "guitar stand",
    "drum set",
    "pool table",
    "foosball table",
    "ping pong table",
    "air hockey table",
    "arcade machine",
    "patio table",
    "patio chair",
    "outdoor sofa",
    "outdoor bench",
    "outdoor lounge chair",
    "adirondack chair",
    "patio umbrella",
    "umbrella stand",
    "outdoor storage box",
    "grill",
    "fire pit",
    "porch swing",
    "hammock",
    "garden bench",
    "flower stand",
    "plant stand",
    "large planter",
    "floor mirror",
    "wall mirror",
    "artwork",
    "large painting",
    "picture frame",
    "clock",
    "grandfather clock",
    "safe",
    "gun safe",
    "storage bin",
    "plastic drawer unit",
    "toy chest",
    "playpen",
    "high chair",
    "baby bassinet",
    "baby stroller",
    "wheelchair",
]


INVENTORY_CLASS_SET = frozenset(
    INVENTORY_CLASSES
)


# ============================================================
# DETECTION GROUPS
# ============================================================
#
# Every frame is scanned by EVERY group.
#
# These are NOT room types.
#
# They exist only so YOLOE does not have to compare
# one region against all 200 labels simultaneously.
# ============================================================


DETECTION_GROUPS = {

    "sleep_bedroom": [
        "bed",
        "mattress",
        "box spring",
        "nightstand",
        "dresser",
        "wardrobe",
        "chest of drawers",
        "headboard",
        "bed frame",
        "crib",
        "changing table",
        "vanity",
        "vanity stool",
        "makeup table",
        "daybed",
        "bunk bed",
        "trundle bed",
        "platform bed",
        "adjustable bed",
        "king mattress",
        "queen mattress",
        "full mattress",
        "twin mattress",
        "california king mattress",
        "mattress topper",
        "bedroom bench",
        "armoire",
        "jewelry armoire",
        "tall dresser",
        "low dresser",
        "baby bassinet",
        "playpen",
    ],

    "seating": [
        "sofa",
        "chair",
        "dining chair",
        "office chair",
        "ottoman",
        "bench",
        "recliner",
        "loveseat",
        "sectional sofa",
        "rocking chair",
        "bar stool",
        "kitchen stool",
        "kitchen chair",
        "entryway bench",
        "armchair",
        "accent chair",
        "lounge chair",
        "chaise lounge",
        "futon",
        "sofa bed",
        "dining bench",
        "folding chair",
        "gaming chair",
        "patio chair",
        "outdoor sofa",
        "outdoor bench",
        "outdoor lounge chair",
        "adirondack chair",
        "porch swing",
        "garden bench",
        "high chair",
        "wheelchair",
    ],

    "tables_desks": [
        "dining table",
        "coffee table",
        "tv stand",
        "desk",
        "end table",
        "side table",
        "console table",
        "kitchen table",
        "buffet",
        "sideboard",
        "hall tree",
        "computer desk",
        "writing desk",
        "standing desk",
        "desk drawer unit",
        "printer stand",
        "bar table",
        "bar cart",
        "kitchen island",
        "kitchen cart",
        "microwave cart",
        "folding table",
        "card table",
        "workbench",
        "patio table",
    ],

    "storage_shelving": [
        "bookshelf",
        "china cabinet",
        "display cabinet",
        "cabinet",
        "storage cabinet",
        "filing cabinet",
        "storage shelf",
        "wall shelf",
        "bookcase",
        "shoe rack",
        "coat rack",
        "chest",
        "storage chest",
        "trunk",
        "pantry cabinet",
        "baker's rack",
        "wine rack",
        "wine cabinet",
        "tool cabinet",
        "tool chest",
        "storage rack",
        "garage shelf",
        "umbrella stand",
        "outdoor storage box",
        "safe",
        "gun safe",
        "storage bin",
        "plastic drawer unit",
        "toy chest",
        "clothes rack",
        "garment rack",
    ],

    "electronics_media": [
        "tv",
        "computer monitor",
        "desktop computer",
        "laptop",
        "printer",
        "speaker",
        "soundbar",
        "subwoofer",
        "stereo system",
        "record player",
        "gaming console",
        "entertainment center",
        "media cabinet",
        "fireplace console",
        "clock",
        "grandfather clock",
    ],

    "appliances_laundry_climate": [
        "refrigerator",
        "mini refrigerator",
        "freezer",
        "microwave",
        "oven",
        "stove",
        "dishwasher",
        "washing machine",
        "dryer",
        "washer-dryer combo",
        "chest freezer",
        "water cooler",
        "portable air conditioner",
        "window air conditioner",
        "fan",
        "ceiling fan",
        "space heater",
        "air purifier",
        "dehumidifier",
        "humidifier",
        "vacuum cleaner",
        "robot vacuum",
        "ironing board",
        "laundry hamper",
        "laundry basket",
    ],

    "fitness_music_games": [
        "bicycle",
        "exercise bike",
        "treadmill",
        "elliptical machine",
        "rowing machine",
        "weight bench",
        "dumbbell rack",
        "home gym machine",
        "yoga equipment rack",
        "piano",
        "upright piano",
        "grand piano",
        "keyboard piano",
        "guitar",
        "guitar stand",
        "drum set",
        "pool table",
        "foosball table",
        "ping pong table",
        "air hockey table",
        "arcade machine",
    ],

    "decor_outdoor_misc": [
        "lamp",
        "floor lamp",
        "table lamp",
        "mirror",
        "rug",
        "patio umbrella",
        "grill",
        "fire pit",
        "hammock",
        "flower stand",
        "plant stand",
        "large planter",
        "floor mirror",
        "wall mirror",
        "artwork",
        "large painting",
        "picture frame",
        "baby stroller",
    ],
}


# ============================================================
# CONFLICT FAMILIES
# ============================================================
#
# Different labels that may describe the SAME object.
#
# If their bounding boxes heavily overlap,
# only the strongest label survives.
#
# Important:
# mattress / headboard / bed frame are NOT all merged,
# because movers may actually move them separately.
# ============================================================


CONFLICT_FAMILIES = {

    "bed_type": {
        "bed",
        "daybed",
        "bunk bed",
        "trundle bed",
        "platform bed",
        "adjustable bed",
    },

    "mattress_type": {
        "mattress",
        "king mattress",
        "queen mattress",
        "full mattress",
        "twin mattress",
        "california king mattress",
    },

    "dresser_type": {
        "dresser",
        "chest of drawers",
        "tall dresser",
        "low dresser",
    },

    "sofa_type": {
        "sofa",
        "loveseat",
        "sectional sofa",
        "futon",
        "sofa bed",
        "outdoor sofa",
    },

    "chair_type": {
        "chair",
        "dining chair",
        "office chair",
        "rocking chair",
        "kitchen chair",
        "armchair",
        "accent chair",
        "lounge chair",
        "chaise lounge",
        "gaming chair",
        "folding chair",
        "patio chair",
        "outdoor lounge chair",
        "adirondack chair",
    },

    "bench_type": {
        "bench",
        "entryway bench",
        "bedroom bench",
        "dining bench",
        "outdoor bench",
        "garden bench",
    },

    "table_type": {
        "dining table",
        "coffee table",
        "end table",
        "side table",
        "console table",
        "kitchen table",
        "bar table",
        "folding table",
        "card table",
        "patio table",
    },

    "desk_type": {
        "desk",
        "computer desk",
        "writing desk",
        "standing desk",
    },

    "cabinet_type": {
        "cabinet",
        "storage cabinet",
        "filing cabinet",
        "china cabinet",
        "display cabinet",
        "pantry cabinet",
        "wine cabinet",
        "tool cabinet",
        "media cabinet",
    },

    "shelf_type": {
        "bookshelf",
        "bookcase",
        "storage shelf",
        "wall shelf",
        "garage shelf",
    },

    "mirror_type": {
        "mirror",
        "floor mirror",
        "wall mirror",
    },

    "lamp_type": {
        "lamp",
        "floor lamp",
        "table lamp",
    },

    "screen_type": {
        "tv",
        "computer monitor",
    },

    "refrigerator_type": {
        "refrigerator",
        "mini refrigerator",
    },

    "freezer_type": {
        "freezer",
        "chest freezer",
    },

    "air_conditioner_type": {
        "portable air conditioner",
        "window air conditioner",
    },

    "vacuum_type": {
        "vacuum cleaner",
        "robot vacuum",
    },

    "piano_type": {
        "piano",
        "upright piano",
        "grand piano",
        "keyboard piano",
    },

    "safe_type": {
        "safe",
        "gun safe",
    },
}


# ============================================================
# LOOKUP: CLASS -> CONFLICT FAMILY
# ============================================================


CLASS_TO_CONFLICT_FAMILY = {}

for family_name, names in CONFLICT_FAMILIES.items():

    for name in names:

        CLASS_TO_CONFLICT_FAMILY[
            name
        ] = family_name


def conflict_family_for(name):

    return CLASS_TO_CONFLICT_FAMILY.get(
        name,
        name
    )


# ============================================================
# VALIDATION
# ============================================================
#
# Program will refuse to start if:
#
# - master catalog is not exactly 200
# - master catalog has duplicates
# - a detection group misses an item
# - an item appears in two detection groups
#
# This prevents us from accidentally excluding inventory items.
# ============================================================


def validate_inventory():

    if len(INVENTORY_CLASSES) != 200:

        raise RuntimeError(
            "Inventory must contain exactly 200 items. "
            f"Current count: {len(INVENTORY_CLASSES)}"
        )

    if len(INVENTORY_CLASS_SET) != 200:

        raise RuntimeError(
            "Duplicate items exist in INVENTORY_CLASSES."
        )

    grouped_items = []

    for group_items in DETECTION_GROUPS.values():

        grouped_items.extend(
            group_items
        )

    grouped_set = set(
        grouped_items
    )

    missing = (
        INVENTORY_CLASS_SET -
        grouped_set
    )

    unknown = (
        grouped_set -
        INVENTORY_CLASS_SET
    )

    if missing:

        raise RuntimeError(
            "Items missing from DETECTION_GROUPS: "
            f"{sorted(missing)}"
        )

    if unknown:

        raise RuntimeError(
            "Unknown items in DETECTION_GROUPS: "
            f"{sorted(unknown)}"
        )

    if len(grouped_items) != len(
        grouped_set
    ):

        duplicates = sorted({
            name
            for name in grouped_items
            if grouped_items.count(name) > 1
        })

        raise RuntimeError(
            "Items appear in multiple detection groups: "
            f"{duplicates}"
        )


validate_inventory()