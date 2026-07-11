# Methodology

## 1. Pass prediction

### Propagation model

OrbitOps India uses **SGP4** (Simplified General Perturbations model 4),
the standard propagator for objects described by two-line element (TLE)
sets, via the [Skyfield](https://rhodesmill.org/skyfield/) library
(which itself wraps the widely used `sgp4` Python package).

Given a TLE and a timestamp, SGP4 returns the satellite's position and
velocity in an Earth-centered inertial frame. Skyfield converts this into
a topocentric (observer-relative) altitude/azimuth for the configured
ground station, accounting for WGS84 geodesy (latitude, longitude,
altitude of the station).

### Event detection

For a given ground station and elevation mask, we use Skyfield's
`EarthSatellite.find_events()` to locate, across the requested window:

- **Rise (AOS — Acquisition of Signal):** the moment elevation crosses
  above the mask.
- **Culminate (max elevation):** the local maximum elevation of the pass.
- **Set (LOS — Loss of Signal):** the moment elevation crosses back below
  the mask.

Azimuth at each event is computed from the same topocentric position.

### Assumptions & limitations (please read before relying on this for
anything beyond a demo/portfolio context)

- **TLE accuracy degrades with time since epoch.** For active satellites,
  TLEs should be refreshed at least every few days; predictions using a
  TLE more than ~1–2 weeks old can be off by many kilometres, which can
  shift pass timing and geometry noticeably.
- **No atmospheric refraction correction.** The elevation mask is a pure
  geometric cutoff; near the horizon, real refraction can make objects
  visible slightly below the geometric elevation predicted here.
- **No solar illumination ("sunlit") computation in the MVP.** This would
  require an additional planetary ephemeris file (tens of MB), which was
  intentionally omitted to keep the deployment lightweight. The
  `sunlit_at_max` field exists in the API for forward compatibility but is
  currently always `null`.
- **No ionospheric or local RF-obstruction modelling.** The elevation mask
  is a simple, user-configurable proxy for "usable" passes given local
  terrain/building obstructions — it is not derived from an actual terrain
  model.
- **Circular dependency on TLE freshness in demo mode.** The offline demo
  fixture uses a TLE with a 2000-era epoch (see `docs/DATA_SOURCES.md`) —
  predictions from it should be treated purely as pipeline demonstrations,
  never as real current passes.

## 2. Scheduling

### Problem framing

Multiple communication requests may compete for the same ground station.
A ground station can serve only one contact at a time, so the scheduler
must pick a conflict-free subset of requests that makes good use of the
station's time.

### Algorithm (fully explainable, no opaque "AI score")

1. **Feasibility filtering.** For each request, predict passes restricted
   to that request's own time window and elevation mask. If no pass meets
   the request's minimum contact duration, the request is rejected
   immediately with a stated reason (e.g. "no orbital elements available"
   or "no pass above N° lasting M seconds").

2. **Candidate selection.** Among a request's feasible passes, the pass
   with the **highest maximum elevation** is chosen as its scheduling
   opportunity (higher elevation generally means a shorter slant range and
   better link margin — a reasonable, explainable proxy for pass quality).
   *Limitation:* only the single best pass per request is considered in
   this MVP; a future extension could evaluate all passes per request.

3. **Explainable scoring.**

   ```
   score = priority_weight(request.priority)
           × (1 + max_elevation_deg / 90)      # pass-quality factor, range [1, 2]
           × (duration_seconds / 3600)          # contact-length factor, in hours
   ```

   `priority_weight` is a fixed lookup table:
   `LOW=1, MEDIUM=2, HIGH=3, CRITICAL=4`.

   Every term in this formula is inspectable and directly traceable to a
   physical or user-specified quantity — there is no learned/opaque model
   involved in scoring.

4. **Conflict resolution — Weighted Interval Scheduling.** Because a
   station can only host one contact at a time, selecting the best
   conflict-free subset of opportunities is exactly the classical
   **weighted interval scheduling** problem from algorithms courses. We
   solve it with the standard O(n log n) dynamic program:

   - Sort opportunities by end time.
   - For each opportunity `i`, binary-search for its latest
     non-overlapping predecessor `p(i)`.
   - `dp[i] = max(dp[i-1], score(i) + dp[p(i)])`.
   - Backtrack through `dp` to recover the selected subset.

   This DP is **provably optimal**: it finds the conflict-free subset
   maximising total score, not just *a* greedy conflict-free subset. This
   was verified in this project against brute-force search over 200
   randomized small instances (see `PROJECT_STATUS.md` for the test
   output) in addition to the pytest unit tests in
   `backend/tests/test_scheduler.py`.

5. **Explanation.** Every scheduled contact records the priority, max
   elevation, duration and score that led to its selection. Every rejected
   request records either why no pass existed, or that a higher-value
   overlapping contact was chosen instead.

### Why this design was chosen over a "fake AI" ranking

The project brief explicitly discourages introducing machine learning
where it would weaken scientific credibility. Ground-station scheduling
under a single-resource, non-overlapping constraint is a solved,
well-understood combinatorial optimisation problem; weighted interval
scheduling is the textbook-correct tool for it, is trivially explainable
in a technical interview, and gives provably optimal results — a stronger
guarantee than an unexplainable heuristic score would provide.
