"""
Core constants for OrbitOps India.

IMPORTANT — GROUND STATION DISCLAIMER:
The preset locations below are illustrative campus / city coordinates provided
for demonstration purposes only. None of them are claimed to be operational
ISRO facilities, licensed satellite ground stations, or affiliated with any
government body. Users should always verify coordinates and licensing status
before any real-world RF operation.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Demonstration ground-station presets (India-focused).
# These are approximate city/campus coordinates, NOT verified official
# ground-station sites. Labelled clearly as "demo presets" in the API.
# ---------------------------------------------------------------------------
PRESET_GROUND_STATIONS = [
    {
        "id": "iist-thiruvananthapuram",
        "name": "Thiruvananthapuram (Demo Campus Site)",
        "latitude_deg": 8.5241,
        "longitude_deg": 76.9366,
        "altitude_m": 15.0,
        "note": "Illustrative coordinate for southern-India demo station. Not a verified facility.",
    },
    {
        "id": "iitb-mumbai",
        "name": "Mumbai (Demo Campus Site)",
        "latitude_deg": 19.1334,
        "longitude_deg": 72.9133,
        "altitude_m": 10.0,
        "note": "Illustrative coordinate for western-India demo station. Not a verified facility.",
    },
    {
        "id": "iitkgp-kharagpur",
        "name": "Kharagpur (Demo Campus Site)",
        "latitude_deg": 22.3149,
        "longitude_deg": 87.3105,
        "altitude_m": 30.0,
        "note": "Illustrative coordinate for eastern-India demo station. Not a verified facility.",
    },
    {
        "id": "iitd-delhi",
        "name": "New Delhi (Demo Campus Site)",
        "latitude_deg": 28.5449,
        "longitude_deg": 77.1926,
        "altitude_m": 216.0,
        "note": "Illustrative coordinate for northern-India demo station. Not a verified facility.",
    },
    {
        "id": "nith-hyderabad",
        "name": "Hyderabad (Demo Campus Site)",
        "latitude_deg": 17.3850,
        "longitude_deg": 78.4867,
        "altitude_m": 542.0,
        "note": "Illustrative coordinate for central/southern-India demo station. Not a verified facility.",
    },
    {
        "id": "iitg-guwahati",
        "name": "Guwahati (Demo Campus Site)",
        "latitude_deg": 26.1445,
        "longitude_deg": 91.7362,
        "altitude_m": 55.0,
        "note": "Illustrative coordinate for north-eastern-India demo station. Not a verified facility.",
    },
    {
        "id": "bhubaneswar",
        "name": "Bhubaneswar (Demo Campus Site)",
        "latitude_deg": 20.2961,
        "longitude_deg": 85.8245,
        "altitude_m": 45.0,
        "note": "Illustrative coordinate for eastern-India demo station. Not a verified facility.",
    },
]

# ---------------------------------------------------------------------------
# Operational limits — keep the free-tier deployment lightweight & responsive.
# ---------------------------------------------------------------------------
MAX_PREDICTION_DAYS = 7          # longest single pass-prediction window
MIN_PREDICTION_HOURS = 0.5       # shortest sensible window
MAX_SATELLITES_PER_TLE_LOAD = 200  # cap on catalogue size held/served at once
MAX_SCHEDULE_REQUESTS = 50       # cap on communication requests per schedule run
MIN_ELEVATION_MASK_DEG = 0.0
MAX_ELEVATION_MASK_DEG = 45.0
DEFAULT_ELEVATION_MASK_DEG = 10.0
DEFAULT_MIN_CONTACT_SECONDS = 60      # ignore passes shorter than this
TIME_STEP_SECONDS = 15           # propagation sampling step (coarse pass search)
REFINEMENT_STEP_SECONDS = 1      # fine step used near AOS/LOS/max-elevation

PRIORITY_LEVELS = ("LOW", "MEDIUM", "HIGH", "CRITICAL")
PRIORITY_WEIGHT = {"LOW": 1.0, "MEDIUM": 2.0, "HIGH": 3.0, "CRITICAL": 4.0}

EARTH_RADIUS_KM = 6371.0
