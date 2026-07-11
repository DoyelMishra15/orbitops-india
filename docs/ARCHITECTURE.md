# Architecture

## Overview

OrbitOps India is a two-service monorepo:

```
┌─────────────────────┐        HTTPS/JSON        ┌──────────────────────────┐
│   React + Vite SPA   │  ───────────────────────▶ │   FastAPI backend         │
│   (frontend/)        │ ◀─────────────────────── │   (backend/)               │
└─────────────────────┘                            └──────────────────────────┘
                                                              │
                                                              ▼
                                          ┌───────────────────────────────────┐
                                          │ TLE Provider                       │
                                          │  live: Celestrak public GP API     │
                                          │  fallback: local demo fixture      │
                                          └───────────────────────────────────┘
                                                              │
                                                              ▼
                                          ┌───────────────────────────────────┐
                                          │ Pass Predictor (Skyfield/SGP4)     │
                                          └───────────────────────────────────┘
                                                              │
                                                              ▼
                                          ┌───────────────────────────────────┐
                                          │ Scheduler (weighted interval DP)   │
                                          └───────────────────────────────────┘
```

## Backend layout

```
backend/
  app/
    main.py            FastAPI app, CORS, error handlers, router registration
    config.py           Environment-driven settings
    core/
      constants.py       Ground-station presets, operational limits
      validation.py       Pure-Python domain validation (framework-independent)
    models/
      schemas.py          Pydantic request/response models
    services/
      tle_provider.py     Live/demo TLE catalogue with in-process caching
      pass_predictor.py   Skyfield-based AOS/LOS/max-elevation computation
      scheduler.py        Explainable weighted interval scheduling
      export_service.py   CSV/JSON schedule export
    routers/
      health.py, satellites.py, passes.py, schedule.py, export.py
  tests/                 pytest suite (unit + API integration)
```

## Frontend layout

```
frontend/
  src/
    api/client.ts        Typed fetch wrapper around the backend API
    types/index.ts        TypeScript types mirroring the Pydantic schemas
    components/            One component per UI concern (ground station,
                            satellite selector, prediction form, results,
                            timeline, elevation chart, scheduling workspace,
                            schedule results, status/loading/error states)
    App.tsx                 Top-level state & data flow
```

## Data flow: pass prediction

1. User selects/enters a ground station and satellite, sets a time window.
2. Frontend POSTs to `/api/v1/passes/predict`.
3. Backend loads the satellite's TLE from the (cached) catalogue.
4. `pass_predictor.predict_passes` propagates the orbit with Skyfield/SGP4
   and finds AOS/culminate/LOS events above the elevation mask.
5. Results are returned as structured JSON and rendered as a timeline,
   table, and elevation chart.

## Data flow: scheduling

1. User adds communication requests (satellite, priority, window,
   elevation mask, minimum contact duration) in the Scheduling Workspace.
2. Frontend POSTs the full request list + ground station to
   `/api/v1/schedule/generate`.
3. For each request, the backend finds its best candidate pass (see
   `docs/METHODOLOGY.md`), scores it, and resolves conflicts with a
   provably-optimal weighted interval scheduling DP.
4. Scheduled and rejected requests (with reasons) are returned together
   with utilization statistics, and can be exported as JSON or CSV.

## Why this architecture fits a free-tier deployment

- **Single lightweight backend process** (FastAPI/Uvicorn) — no
  background workers, queues, or GPUs.
- **Static frontend build** — deployable to any static host (Vercel,
  Netlify, GitHub Pages, Cloudflare Pages) independent of the backend.
- **No mandatory database** — the MVP is stateless; requests and results
  live in the frontend's React state for the session. This keeps the
  footprint minimal and avoids managing a persistence layer for a
  portfolio deployment. (See `docs/DEPLOYMENT.md` for how to add SQLite
  persistence later if desired.)
- **Bounded computation** — request limits (`MAX_PREDICTION_DAYS`,
  `MAX_SCHEDULE_REQUESTS`, `MAX_SATELLITES_PER_TLE_LOAD`) keep every
  request's CPU/memory cost small and predictable.
