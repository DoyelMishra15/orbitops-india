#!/usr/bin/env bash
# End-to-end smoke test against a RUNNING backend (default http://localhost:8000).
# Unit and API tests live in backend/tests/ (run via `pytest`); this script
# is an extra manual/CI sanity check that hits the real HTTP server.
set -euo pipefail

BASE_URL="${1:-http://localhost:8000}/api/v1"

echo "==> Health check"
curl -sf "$BASE_URL/health" | grep -q '"status":"ok"' && echo "OK"

echo "==> Data source status"
curl -sf "$BASE_URL/data-source/status" | grep -q '"mode"' && echo "OK"

echo "==> Ground station presets"
curl -sf "$BASE_URL/ground-stations/presets" | grep -q 'latitude_deg' && echo "OK"

echo "==> Satellite catalogue"
curl -sf "$BASE_URL/satellites" | grep -q 'norad_id' && echo "OK"

echo "==> Pass prediction (NORAD 5, demo fixture)"
START=$(python3 -c "import datetime;print((datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(minutes=1)).isoformat())")
curl -sf -X POST "$BASE_URL/passes/predict" \
  -H "Content-Type: application/json" \
  -d "{\"norad_id\":5,\"ground_station\":{\"name\":\"Test\",\"latitude_deg\":20.29,\"longitude_deg\":85.82,\"altitude_m\":45,\"min_elevation_deg\":10},\"start_time_utc\":\"$START\",\"duration_hours\":48}" \
  | grep -q 'pass_count' && echo "OK"

echo ""
echo "All smoke tests passed against $BASE_URL"
