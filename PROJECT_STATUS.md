# Project Status

_Last verified: this pass, against a sandbox with real PyPI/npm network access._

## Summary

OrbitOps India is **feature-complete for the MVP scope**: satellite pass
prediction (Skyfield/SGP4), an explainable weighted-interval-scheduling
conflict-free scheduler, a full React/TS frontend consuming a real FastAPI
backend, live + offline-demo orbital data modes, export, and full
documentation. Unlike the build pass that produced this archive, this
verification pass **had outbound access to PyPI and npm**, so the backend
test suite, the frontend production build, and a live running server were
all actually executed rather than only syntax-checked.

## What was actually run this pass

| Check | Result |
|---|---|
| Backend test suite (`pytest -v`, 44 tests: validation, scheduler, pass predictor, API) | ✅ **44/44 passed** |
| Frontend production build (`tsc -b && vite build`) | ✅ Built cleanly, zero TypeScript errors |
| Backend server boot (`uvicorn app.main:app`) + `/health` and `/` | ✅ Responding correctly |
| Root-level HTTP smoke test (`tests/smoke_test.sh`) against the live server | ✅ All checks passed |
| Live Celestrak fetch | ⏳ Still not exercised — this sandbox's network allowlist covers package registries (PyPI, npm) but not `celestrak.org`. Code path is unchanged from the original build; run it yourself in Codespaces or any unrestricted environment to confirm live-mode fetch, with `FORCE_DEMO_MODE=false` (the default). |

## Bug found and fixed this pass

The original build's global validation-error handler
(`backend/app/main.py::validation_exception_handler`) returned
`exc.errors()` directly in the JSON response. Pydantic v2 includes the raw
Python exception object under each error's `"ctx"` key when a custom
validator raises `ValueError` (e.g. the `duration_hours` bound check) —
and raw exception objects aren't JSON-serializable. This meant **any
request that failed a custom-validator check crashed with a 500 instead of
returning the intended 422**, silently swallowing the real error message.
It was only caught because `test_predict_passes_rejects_excessive_duration`
exercises exactly that path.

Fix: stringify the contents of `"ctx"` before serializing. Covered by the
existing test — no new test needed, it just now passes for the right
reason. Also fixed a stray `datetime.utcnow()` deprecation warning in
`test_validation.py` (harmless, but noisy under Python 3.12).

## What was verified in the original build (still holds)

1. All 24 backend Python files compile cleanly (`py_compile`).
2. All config/JSON files (`devcontainer.json`, `package.json`, three
   `tsconfig*.json`) are valid.
3. The scheduling algorithm (weighted interval scheduling DP) was
   independently cross-checked against a brute-force optimality proof over
   200 randomized instances.
4. The demo/offline TLE fixture is a real, independently published SGP4
   reference vector (Vanguard 1 / NORAD 5), not an invented one — see
   `docs/DATA_SOURCES.md`.
5. Frontend API types (`src/types/index.ts`) mirror the backend Pydantic
   schemas (`app/models/schemas.py`) field-for-field.

## Reproduce this verification yourself

```bash
# Backend
cd backend
pip install -r requirements.txt        # add --break-system-packages if needed
pytest -v                              # expect 44 passed

# Frontend
cd ../frontend
npm install
npm run build                          # expect dist/ with no TS errors

# Run both services and smoke-test
cd ../backend && uvicorn app.main:app --reload --port 8000 &
cd ../frontend && npm run dev -- --host 0.0.0.0 &
bash ../tests/smoke_test.sh http://localhost:8000
```

## Feature checklist against the brief

- [x] Select a satellite from public orbital-element data (live Celestrak
      or labelled demo fixture)
- [x] Choose a preset or custom Indian ground-station location
- [x] Choose a prediction time window (bounded to ≤7 days)
- [x] Calculate upcoming passes (AOS, max-elevation, LOS, duration, max
      elevation angle, azimuth)
- [x] Visualize passes (timeline + elevation profile chart)
- [x] Submit multiple communication requests
- [x] Detect overlapping opportunities
- [x] Automatically build a conflict-free schedule (weighted interval
      scheduling, provably optimal for the stated objective)
- [x] Explain why requests were scheduled or rejected
- [x] Export the schedule (JSON/CSV)
- [x] India-focused presets, no ISRO impersonation, no fabricated data
- [x] Runs in GitHub Codespaces (`.devcontainer/`)
- [x] Free-tier deployable architecture (`docs/DEPLOYMENT.md`)
- [x] Full documentation set (README, ARCHITECTURE, METHODOLOGY,
      DATA_SOURCES, API, DEPLOYMENT)

## Known limitations

- SGP4/TLE staleness affects accuracy over time since epoch.
- No atmospheric refraction / ionospheric / local-terrain RF modelling.
- No solar-illumination ("sunlit") computation in the MVP.
- Scheduler considers each request's single best candidate pass (highest
  elevation), not all feasible passes.
- No persistence layer — schedules exist for the browser session unless
  exported (stateless MVP by design).
- Live Celestrak fetch has not been exercised end-to-end in any sandbox
  used so far; confirm it in an environment with unrestricted network
  access before relying on live mode.

Full detail in `docs/METHODOLOGY.md`.
