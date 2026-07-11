import os

os.environ["FORCE_DEMO_MODE"] = "true"  # keep API tests network-independent & deterministic

from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["service"] == "OrbitOps India"


def test_root_endpoint():
    resp = client.get("/")
    assert resp.status_code == 200
    assert "OrbitOps India" in resp.json()["service"]


def test_data_source_status():
    resp = client.get("/api/v1/data-source/status")
    assert resp.status_code == 200
    body = resp.json()
    assert body["mode"] in ("live", "demo_archive")
    assert body["satellite_count"] >= 1


def test_ground_station_presets():
    resp = client.get("/api/v1/ground-stations/presets")
    assert resp.status_code == 200
    presets = resp.json()
    assert len(presets) >= 1
    assert all("latitude_deg" in p for p in presets)


def test_list_satellites_demo_mode():
    resp = client.get("/api/v1/satellites")
    assert resp.status_code == 200
    sats = resp.json()
    assert len(sats) >= 1
    assert any(s["norad_id"] == 5 for s in sats)


def test_predict_passes_valid_request():
    start = (datetime.now(timezone.utc) + timedelta(minutes=1)).isoformat()
    payload = {
        "norad_id": 5,
        "ground_station": {
            "name": "Bhubaneswar Demo",
            "latitude_deg": 20.2961,
            "longitude_deg": 85.8245,
            "altitude_m": 45.0,
            "min_elevation_deg": 10.0,
        },
        "start_time_utc": start,
        "duration_hours": 48.0,
    }
    resp = client.post("/api/v1/passes/predict", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["norad_id"] == 5
    assert "passes" in body
    assert body["pass_count"] == len(body["passes"])


def test_predict_passes_unknown_satellite():
    start = datetime.now(timezone.utc).isoformat()
    payload = {
        "norad_id": 999999,
        "ground_station": {
            "name": "X",
            "latitude_deg": 20.0,
            "longitude_deg": 85.0,
            "altitude_m": 0.0,
            "min_elevation_deg": 10.0,
        },
        "start_time_utc": start,
        "duration_hours": 24.0,
    }
    resp = client.post("/api/v1/passes/predict", json=payload)
    assert resp.status_code == 404


def test_predict_passes_rejects_excessive_duration():
    start = datetime.now(timezone.utc).isoformat()
    payload = {
        "norad_id": 5,
        "ground_station": {
            "name": "X",
            "latitude_deg": 20.0,
            "longitude_deg": 85.0,
            "altitude_m": 0.0,
            "min_elevation_deg": 10.0,
        },
        "start_time_utc": start,
        "duration_hours": 24 * 30,  # 30 days > MAX_PREDICTION_DAYS
    }
    resp = client.post("/api/v1/passes/predict", json=payload)
    assert resp.status_code == 422


def test_predict_passes_rejects_invalid_latitude():
    start = datetime.now(timezone.utc).isoformat()
    payload = {
        "norad_id": 5,
        "ground_station": {
            "name": "X",
            "latitude_deg": 200.0,
            "longitude_deg": 85.0,
            "altitude_m": 0.0,
            "min_elevation_deg": 10.0,
        },
        "start_time_utc": start,
        "duration_hours": 24.0,
    }
    resp = client.post("/api/v1/passes/predict", json=payload)
    assert resp.status_code == 422


def test_schedule_generation_end_to_end():
    base = datetime.now(timezone.utc) + timedelta(minutes=1)
    payload = {
        "ground_station": {
            "name": "Bhubaneswar Demo",
            "latitude_deg": 20.2961,
            "longitude_deg": 85.8245,
            "altitude_m": 45.0,
            "min_elevation_deg": 10.0,
        },
        "requests": [
            {
                "request_id": "REQ-1",
                "norad_id": 5,
                "satellite_name": "VANGUARD 1",
                "priority": "HIGH",
                "earliest_start_utc": base.isoformat(),
                "latest_end_utc": (base + timedelta(hours=72)).isoformat(),
                "min_elevation_deg": 10.0,
                "min_contact_seconds": 30,
            },
            {
                "request_id": "REQ-2",
                "norad_id": 999999,  # unknown satellite -> should be rejected
                "priority": "LOW",
                "earliest_start_utc": base.isoformat(),
                "latest_end_utc": (base + timedelta(hours=72)).isoformat(),
                "min_elevation_deg": 10.0,
                "min_contact_seconds": 30,
            },
        ],
    }
    resp = client.post("/api/v1/schedule/generate", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["total_requests"] == 2
    assert body["scheduled_count"] + body["rejected_count"] == 2
    # REQ-2 must be rejected (unknown NORAD id) with an explanatory reason
    rejected_ids = [r["request_id"] for r in body["rejected"]]
    assert "REQ-2" in rejected_ids


def test_schedule_generation_requires_at_least_one_request():
    payload = {
        "ground_station": {
            "name": "X",
            "latitude_deg": 20.0,
            "longitude_deg": 85.0,
            "altitude_m": 0.0,
            "min_elevation_deg": 10.0,
        },
        "requests": [],
    }
    resp = client.post("/api/v1/schedule/generate", json=payload)
    assert resp.status_code == 422
