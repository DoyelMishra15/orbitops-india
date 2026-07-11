# Data Sources

## Live mode

OrbitOps India's live mode fetches current, publicly available two-line
element (TLE) sets from **[Celestrak](https://celestrak.org)**
(`celestrak.org/NORAD/elements/gp.php`), a long-standing, freely
accessible catalogue of orbital elements widely used across the amateur
satellite, academic, and space-situational-awareness communities.

The app queries three public Celestrak groups relevant to university /
small-satellite operations:

- `cubesat` — active CubeSats
- `amateur` — amateur radio satellites
- `stations` — crewed stations (e.g. ISS) and similar high-interest objects

Live-mode responses are cached in-process for `TLE_CACHE_TTL_SECONDS`
(default 6 hours) to avoid excessive upstream requests and to keep the
app responsive.

**No data is fabricated in live mode.** Every satellite name, NORAD ID,
and orbital element returned to the user comes directly from Celestrak's
public feed.

## Demo / archive mode (automatic fallback)

If live fetch fails — no network access, Celestrak temporarily
unavailable, request timeout — or if `FORCE_DEMO_MODE=true` is set, the
backend falls back to a small local fixture:
`backend/app/data/demo_tles.txt`.

This fixture intentionally contains **exactly one** TLE: the standard
SGP4 verification vector for **Vanguard 1 (NORAD catalogue ID 5)**, as
published in *"Revisiting Spacetrack Report #3"* (Vallado, Crawford,
Hujsak & Kelso, AIAA 2006-6753) — the reference paper behind the modern
open-source SGP4 implementations, and a fixture reused directly in the
`sgp4` Python package's own test suite.

This choice was deliberate:

- It is a **real, publicly published, independently verifiable** orbital
  element set — not an invented one.
- Its epoch (day 179.78495062 of the year **2000**) makes it obviously a
  non-current reference vector, which is the correct property for a
  fixture whose job is to demonstrate the *pipeline* (propagation → pass
  detection → scheduling) deterministically offline, without ever being
  mistaken for a live, present-day pass.

**What demo mode is not:** it is not a source of current Indian CubeSat
positions, and the UI always labels it clearly ("Demo / Archive Mode")
via the data-source status badge and API (`GET /api/v1/data-source/status`).

## Ground-station location presets

The preset ground-station coordinates shown in the UI
(`backend/app/core/constants.py::PRESET_GROUND_STATIONS`) are
**illustrative city/campus coordinates for demonstration purposes only**.
They are:

- **Not** claimed to be verified, licensed, or operational ground-station
  facilities.
- **Not** affiliated with ISRO or any government body.
- Intended purely to let a user quickly try the app with a plausible
  Indian location before entering their own team's real coordinates.

Users are expected to enter their own verified latitude/longitude/altitude
for any real planning use.

## Responsible-use note

This application is an educational/portfolio project. It performs
geometrically and physically legitimate calculations using public data,
but it has not been validated against an operational ground-station
system, has known limitations (see `docs/METHODOLOGY.md`), and should not
be used as the sole basis for real satellite communication operations.
