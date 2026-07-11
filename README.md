# OrbitOps India

**Intelligent Satellite Pass Planning and Ground-Station Scheduling Platform**

OrbitOps India helps Indian university CubeSat teams, small-satellite
projects, and academic ground-station teams answer two practical
questions: *"When can we talk to our satellite?"* and *"Given several
competing communication requests, what's the best conflict-free
schedule for our ground station?"*

> **Not affiliated with ISRO or any government body.** Ground-station
> location presets are illustrative demo coordinates, not verified
> operational facilities. All orbital data is either live public data
> from Celestrak or a clearly labelled offline demo fixture — nothing is
> fabricated. See `docs/DATA_SOURCES.md`.

---

## The problem

Small satellite and university mission teams need to know when their
satellite will be visible from their ground station, and — because a
single station can only talk to one satellite at a time — how to turn
several teams' overlapping requests into a single, fair, conflict-free
schedule, with a clear explanation of why each request was accepted or
rejected.

## Who this is for

- Indian university CubeSat/small-satellite teams
- Engineering colleges running satellite/ground-station courses or clubs
- Student mission-operations teams
- Anyone learning satellite communications planning

## Features

- Search a live public satellite catalogue (Celestrak) or use an offline
  demo/archive fixture
- Configure a ground station via demo presets or custom lat/lon/altitude
  and elevation mask
- Predict upcoming passes: AOS, max-elevation time & angle, LOS, duration,
  azimuth
- Visual timeline of passes across the prediction window + elevation
  profile chart
- Submit multiple communication requests with priority levels
- Automatic conflict-free scheduling via a **provably optimal, fully
  explainable** algorithm (weighted interval scheduling — see
  `docs/METHODOLOGY.md`)
- Human-readable explanations for every scheduled *and* every rejected
  request
- Export the generated schedule as JSON or CSV
- Clear "Live Data" vs "Demo/Archive Mode" indicator at all times

## Architecture

```
React + Vite + TypeScript  ──HTTP/JSON──▶  FastAPI + Pydantic
                                                │
                                     Skyfield/SGP4 propagation
                                                │
                              Weighted interval scheduling (DP)
```

Full detail: `docs/ARCHITECTURE.md`.

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, TypeScript, Recharts |
| Backend | Python 3.12, FastAPI, Pydantic v2 |
| Orbital mechanics | Skyfield (SGP4), NumPy |
| Data | Celestrak (live) / local verified fixture (offline demo) |
| Scheduling | Weighted interval scheduling (classical DP) |
| Dev environment | GitHub Codespaces / VS Code Dev Containers |

## Data sources & prediction methodology

See `docs/DATA_SOURCES.md` and `docs/METHODOLOGY.md` for full detail on
where orbital data comes from, how passes are predicted, how scheduling
decisions are made, and documented limitations.

---

## Getting started in GitHub Codespaces

1. Click **Code → Create codespace on main** on the GitHub repo (or open
   this folder in VS Code with the Dev Containers extension).
2. Wait for `postCreate.sh` to finish (installs backend + frontend deps,
   copies `.env.example` → `.env`).
3. Start the backend:
   ```bash
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
4. In a second terminal, start the frontend:
   ```bash
   cd frontend
   npm run dev -- --host 0.0.0.0
   ```
5. Open the forwarded port `5173` (Codespaces will prompt/preview it
   automatically). The app talks to the backend on port `8000`.
6. Interactive API docs: forwarded port `8000` → `/docs`.

## Running locally (outside Codespaces)

Requirements: Python 3.12+, Node 20+.

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example ../.env   # if not already present
uvicorn app.main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

Or with Docker Compose:
```bash
docker compose up
```

## Environment variables

See `.env.example` and `docs/DEPLOYMENT.md` for the full list
(`CORS_ORIGINS`, `CELESTRAK_BASE_URL`, `TLE_CACHE_TTL_SECONDS`,
`FORCE_DEMO_MODE`, `VITE_API_BASE_URL`, etc.).

## Tests

```bash
cd backend
pip install -r requirements.txt
pytest
```

Covers: coordinate/time-window/elevation-mask validation, pass
propagation correctness properties (window bounds, time-ordering,
elevation-mask monotonicity), scheduler scoring & conflict resolution
(including a brute-force optimality cross-check), and full API
integration tests (health, catalogue, pass prediction, end-to-end
scheduling).

A root-level HTTP smoke test against a *running* server is also provided:
```bash
bash tests/smoke_test.sh http://localhost:8000
```

## Deployment (free-tier)

See `docs/DEPLOYMENT.md` for concrete steps to deploy the backend
(Render/Railway/Fly.io free tier or any small VM) and frontend
(Vercel/Netlify/Cloudflare Pages) at zero cost.

## Limitations

- SGP4/TLE accuracy degrades over time since epoch; treat predictions
  from stale TLEs (including the demo fixture) as indicative, not
  operational.
- No atmospheric refraction, ionospheric, or local-terrain RF modelling.
- No solar-illumination ("sunlit") computation in the MVP.
- The scheduler considers only each request's single best candidate pass
  (highest elevation), not all feasible passes.
- No persistence layer in the MVP — schedules exist for the browser
  session unless exported.

Full detail in `docs/METHODOLOGY.md`.

## Responsible use

This is an educational/portfolio project performing legitimate orbital
calculations on public data. It has not been validated against an
operational ground-station system and must not be used as the sole basis
for real satellite communication operations. It does not claim ISRO
affiliation or access to restricted/government satellite data.

## License

Educational/portfolio project. Add a license of your choice (e.g. MIT)
before publishing publicly.
