# Project Status

_Last updated as part of the build pipeline that produced this archive._

## Summary

OrbitOps India is **feature-complete for the MVP scope** described in the
build brief: satellite pass prediction (Skyfield/SGP4), an explainable
weighted-interval-scheduling conflict-free scheduler, a full React/TS
frontend consuming a real FastAPI backend, live + offline-demo orbital
data modes, export, and full documentation.

## Build environment constraint (please read)

The sandbox this project was built in has **no outbound network
access** (`pip install`, `npm install`, and direct HTTP all confirmed
blocked — see commands below). That means the `fastapi`, `pydantic`,
`skyfield`, `sgp4`, and Node/`react`/`vite` toolchains could not be
installed *in this sandbox* to run a live `pytest` or `npm run build`.
**GitHub Codespaces has normal network access**, so `postCreate.sh` will
install everything and the full stack will run there exactly as
designed.

What this means concretely for verification honesty:

| Check | Status here | How to complete it |
|---|---|---|
| Python syntax, all 24 backend files | ✅ Done (`python3 -m py_compile`, zero errors) | — |
| JSON/config validity (devcontainer, package.json, tsconfig×3) | ✅ Done | — |
| Domain validation logic (lat/lon/alt/elevation/time-window rules) | ✅ **Actually executed**, 14/14 cases pass | `pytest backend/tests/test_validation.py` in Codespaces for the full pytest-formatted version |
| Scheduling algorithm (weighted interval scheduling DP) | ✅ **Actually executed**: 3 targeted cases + **200 randomized brute-force cross-checks**, all passing | `pytest backend/tests/test_scheduler.py` |
| Pass prediction (Skyfield/SGP4) | ⏳ Written, not executable here (no `skyfield`/`sgp4` install) | `pytest backend/tests/test_pass_predictor.py` |
| FastAPI endpoints (TestClient) | ⏳ Written, not executable here (no `fastapi` install) | `pytest backend/tests/test_api.py` |
| Frontend TypeScript build | ⏳ Written, not executable here (no `npm install`) | `cd frontend && npm install && npm run build` |
| Live Celestrak fetch | ⏳ Code written and reviewed; requires network to exercise | Run the app in Codespaces; `FORCE_DEMO_MODE=false` is the default |

### Proof of the constraint (reproducible)

```
$ pip install --break-system-packages fastapi
ERROR: Could not find a version that satisfies the requirement fastapi (from versions: none)

$ npm ping
npm error code E403
npm error 403 Forbidden ... x-deny-reason: host_not_allowed
```

### What was done to compensate

Rather than just asserting the untestable parts are "probably fine":

1. **The highest-risk logic — the scheduling algorithm — was extracted
   into a dependency-free standalone script and executed for real**,
   including a brute-force optimality proof over 200 randomized
   interval-scheduling instances (all matched the DP's answer exactly).
   This is the same algorithm shipped in `app/services/scheduler.py`.
2. **All domain validation rules were executed for real** (14/14 cases),
   using the actual `app/core/validation.py` module (it has zero
   framework dependencies by design, specifically so it could be tested
   without FastAPI/Pydantic installed).
3. Every backend Python file was compiled (`py_compile`) to catch syntax
   errors, import-path typos, and structural mistakes.
4. The demo/offline TLE fixture uses a **real, independently-published**
   reference vector (Vanguard 1 / NORAD 5, from the canonical SGP4
   validation paper) rather than an invented one — see
   `docs/DATA_SOURCES.md` for why and its provenance.
5. All API request/response shapes in the frontend (`src/types/index.ts`)
   were written to mirror the backend Pydantic schemas
   (`app/models/schemas.py`) field-for-field to minimize integration risk.

## Exact commands to complete verification in Codespaces

```bash
# 1. Open in Codespaces (or run .devcontainer/postCreate.sh manually)
bash .devcontainer/postCreate.sh

# 2. Backend tests
cd backend
pytest -v
# Expect: test_validation.py, test_scheduler.py, test_pass_predictor.py,
# test_api.py all passing (33 tests total across the four files).

# 3. Frontend build
cd ../frontend
npm run build
# Expect: `dist/` produced with no TypeScript errors.

# 4. Run both services and do a manual end-to-end pass
cd ../backend && uvicorn app.main:app --reload --port 8000 &
cd ../frontend && npm run dev -- --host 0.0.0.0 &

# 5. HTTP smoke test against the live server
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

## Known limitations (also documented in README / docs/METHODOLOGY.md)

- SGP4/TLE staleness affects accuracy over time.
- No atmospheric refraction / ionospheric / terrain modelling.
- No solar-illumination computation in the MVP.
- Scheduler considers each request's single best candidate pass, not all
  feasible passes.
- No persistence layer (stateless MVP by design).
- Live-mode network fetch, full pytest run, and frontend production build
  were written and reviewed but not executed inside this build sandbox
  due to the network restriction described above — they are expected to
  pass in Codespaces based on the syntax verification and the algorithmic
  correctness testing that *was* performed, but you should run the exact
  commands above yourself before treating this as fully verified.
