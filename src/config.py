"""
Shared settings for the Cut Off project.

Every notebook and script imports its numbers from here, so the whole team
uses the same values. Change a value here, not inside a notebook, and note
the change in NOTES.md.
"""

# ---------------------------------------------------------------------------
# Study area: Upper Assam
# ---------------------------------------------------------------------------
# District names as OpenStreetMap knows them. The bounding boxes are rough
# fallbacks (left, bottom, right, top in degrees) used only if OSM cannot
# find the district boundary by name.
DISTRICTS = {
    "Sivasagar": {
        "place": "Sivasagar district, Assam, India",
        "bbox": (94.40, 26.75, 95.00, 27.20),
        "town": (26.984, 94.637),   # lat, lon of the district town
    },
    "Charaideo": {
        "place": "Charaideo district, Assam, India",
        "bbox": (94.75, 26.75, 95.30, 27.10),
        "town": (26.946, 94.860),   # Sonari
    },
    "Jorhat": {
        "place": "Jorhat district, Assam, India",
        "bbox": (93.90, 26.40, 94.60, 27.00),
        "town": (26.757, 94.203),
    },
}

# One box that covers all three districts, used for satellite searches.
STUDY_BBOX = (93.90, 26.40, 95.30, 27.30)

# Expansion: the other two districts hit by the same July 2026 flood.
# Planned for Week 5, after the pipeline works on the core three, and only if
# one Sentinel-1 image pair covers them (Nagaon is about 200 km west).
EXPANSION_DISTRICTS = {
    "Golaghat": {
        "place": "Golaghat district, Assam, India",
        "bbox": (93.40, 25.80, 94.40, 26.80),
        "town": (26.515, 93.960),
    },
    "Nagaon": {
        "place": "Nagaon district, Assam, India",
        "bbox": (92.30, 25.90, 93.40, 26.60),
        "town": (26.348, 92.684),
    },
}

# All five districts affected by the July 2026 flood.
ALL_AFFECTED_DISTRICTS = {**DISTRICTS, **EXPANSION_DISTRICTS}
ALL_AFFECTED_BBOX = (92.30, 25.80, 95.30, 27.30)

# Backup study area if Upper Assam fails the data checks.
BACKUP_DISTRICT = {
    "Barpeta": {
        "place": "Barpeta district, Assam, India",
        "bbox": (90.75, 26.20, 91.30, 26.80),
        "town": (26.323, 91.006),
    },
}

# ---------------------------------------------------------------------------
# Dates
# ---------------------------------------------------------------------------
PRE_FLOOD_WINDOW = ("2026-06-01", "2026-07-01")    # "before" image
FLOOD_WINDOW = ("2026-07-18", "2026-08-06")        # "during" image
SEARCH_WINDOW = ("2026-06-01", "2026-08-10")       # everything we list

# Chosen Sentinel-1 images (Check 2, 2026-10-26). Same track: orbit 4, DESCENDING,
# both cover about 99% of the core study area. Notebooks look up the exact image
# by date + orbit + pass (taking the one that covers most of the area).
# The "before" image is 17 July, NOT June: in July farmers flood paddy fields for
# transplanting, so a June baseline can mistake planted rice fields for flood.
# 17 July is two days before the heavy rain began (19 July).
TRACK = {"orbit": 4, "pass": "DESCENDING"}
PRE_DATE = "2026-07-17"
POST_DATE = "2026-07-29"
JUNE_DATE = "2026-06-04"   # older baseline on the same track, kept for comparison
PRE_ID_KNOWN = "S1D_IW_GRDH_1SDV_20260717T233756_20260717T233821_003720_006A9E_7B2A"
POST_ID_KNOWN = "S1D_IW_GRDH_1SDV_20260729T233756_20260729T233821_003895_0070A3_D90B"
JUNE_ID_KNOWN = "S1A_IW_GRDH_1SDV_20260604T233843_20260604T233908_064826_082B1B_663A"
# Alternative closer to the flood peak: orbit 143 ASCENDING, 2026-07-15 -> 2026-07-27 (88% cover).

# ---------------------------------------------------------------------------
# Radar preprocessing (must be identical for training and Assam images)
# ---------------------------------------------------------------------------
# Sentinel-1 values are in decibels (dB). We clip each band to a fixed range
# and scale it to 0..1. These ranges cover almost all land and water values.
VV_RANGE = (-30.0, 0.0)
VH_RANGE = (-35.0, -5.0)

TILE_SIZE = 512          # pixels per side (Sen1Floods11 chip size, 10 m pixels)
LABEL_IGNORE = -1        # Sen1Floods11 "no data" label value

# ---------------------------------------------------------------------------
# Model and uncertainty
# ---------------------------------------------------------------------------
ENCODER = "resnet34"
ENSEMBLE_SIZE = 5
SEEDS = [0, 1, 2, 3, 4]

# ---------------------------------------------------------------------------
# Flood map and road analysis
# ---------------------------------------------------------------------------
HAND_MAX_M = 15            # higher than this above the nearest stream = cannot flood
JRC_PERMANENT_PCT = 80     # JRC water occurrence above this = permanent water
ROAD_BUFFER_M = 20         # buffer around each road segment
ROAD_BLOCKED_SHARE = 0.20  # blocked if more than this share of buffer is flooded
ROAD_BLOCKED_SENSITIVITY = [0.10, 0.20, 0.40]
SETTLEMENT_CLUSTER_M = 100 # buildings closer than this form one settlement
SNAP_MAX_M = 500           # max distance from a settlement/hospital to a road

# Road types (OSM "highway" tag) we treat as minor / village roads.
MINOR_ROAD_TYPES = {
    "residential", "unclassified", "track", "service", "living_street", "road",
}
MAJOR_ROAD_TYPES = {
    "motorway", "motorway_link", "trunk", "trunk_link", "primary", "primary_link",
    "secondary", "secondary_link", "tertiary", "tertiary_link",
}
