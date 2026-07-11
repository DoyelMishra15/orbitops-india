# Deployment (Free-Tier)

OrbitOps India is deliberately architected as **one static frontend +
one lightweight stateless backend process**, so it fits comfortably
within common free tiers. Below are two concrete, low-effort options.

## Option A — Backend on Render/Railway/Fly.io free tier + Frontend on
Vercel/Netlify/Cloudflare Pages

### Backend

1. Push the repository to GitHub.
2. Create a new **Web Service** on your chosen platform, pointed at the
   `backend/` directory.
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Set environment variables (see `.env.example`):
   - `CORS_ORIGINS=https://<your-frontend-domain>`
   - `LOG_LEVEL=INFO`
6. Most free tiers on these platforms give enough CPU/RAM for this
   workload (no GPU, no large models, bounded request sizes).

### Frontend

1. Create a new static site project pointed at `frontend/`.
2. Build command: `npm install && npm run build`
3. Output directory: `dist`
4. Set `VITE_API_BASE_URL=https://<your-backend-domain>/api/v1` as a
   build-time environment variable.

## Option B — Both services on a single free VM (e.g. Oracle Cloud
Always Free, or any small always-on VM)

1. Install Python 3.12 and Node 20.
2. `cd backend && pip install -r requirements.txt`
3. Run behind a process manager (systemd, pm2, or simply `tmux`):
   `uvicorn app.main:app --host 0.0.0.0 --port 8000`
4. `cd frontend && npm install && npm run build`
5. Serve the built `frontend/dist` directory with any static file server
   (nginx, Caddy, or `python -m http.server` for a quick demo), and set
   `VITE_API_BASE_URL` before building to point at the backend's public
   address.
6. Optionally put nginx/Caddy in front of both to serve them under one
   domain (`/` → static files, `/api` → proxy to Uvicorn).

## Keeping it lightweight

- No GPU, no Kubernetes, no Kafka, no mandatory Redis, no paid LLM API.
- No database is required for the MVP (stateless request/response); if
  you want to persist schedules across sessions later, SQLite is a
  reasonable next step and fits free-tier disk limits — see "Future
  Work" below.
- Request limits (`MAX_PREDICTION_DAYS=7`, `MAX_SCHEDULE_REQUESTS=50`,
  `MAX_SATELLITES_PER_TLE_LOAD=200`) keep each request's CPU/memory cost
  small and bounded, which matters a lot on shared/free-tier CPU.
- The Skyfield/SGP4 propagation cost per request is small (millisecond
  range per pass search over a multi-day window), so a single small
  instance can serve realistic classroom-demo traffic.

## Future work: adding persistence

If you want ground stations, satellites-of-interest, or generated
schedules to survive a page reload or be shared across a team, add a
single SQLite file (`sqlite:///./orbitops.db`) via SQLAlchemy or
`sqlite3` directly, and add simple CRUD endpoints. This was intentionally
left out of the MVP per the "keep it simple unless it adds real value"
guidance in the project brief — the core demo (predict → schedule →
export) does not require it.

## Environment variables summary

| Variable | Where | Purpose |
|---|---|---|
| `CORS_ORIGINS` | backend | Comma-separated list of allowed frontend origins |
| `CELESTRAK_BASE_URL` | backend | Live TLE source (override for testing/mirrors) |
| `TLE_CACHE_TTL_SECONDS` | backend | How long live TLEs are cached in-process |
| `TLE_FETCH_TIMEOUT_SECONDS` | backend | Network timeout before falling back to demo mode |
| `FORCE_DEMO_MODE` | backend | Force offline demo mode even with network access |
| `LOG_LEVEL` | backend | Python logging level |
| `VITE_API_BASE_URL` | frontend (build-time) | Backend API base URL |
