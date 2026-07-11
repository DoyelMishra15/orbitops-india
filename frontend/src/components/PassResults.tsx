import { useState } from "react";
import type { PassPredictionResponse } from "../types";
import { PassTimeline } from "./PassTimeline";
import { ElevationChart } from "./ElevationChart";
import { EmptyState } from "./StatusStates";

function fmt(iso: string) {
  return new Date(iso).toLocaleString(undefined, {
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function PassResults({ result }: { result: PassPredictionResponse | null }) {
  const [selected, setSelected] = useState<number | null>(null);

  if (!result) {
    return (
      <div className="panel">
        <div className="panel-header">
          <span className="panel-title">Upcoming Passes</span>
        </div>
        <EmptyState label="Configure a ground station and satellite, then calculate passes." />
      </div>
    );
  }

  if (result.passes.length === 0) {
    return (
      <div className="panel">
        <div className="panel-header">
          <span className="panel-title">Upcoming Passes</span>
        </div>
        <EmptyState label="No passes above the elevation mask were found in this window. Try a longer window or a lower elevation mask." />
      </div>
    );
  }

  const activeIndex = selected ?? 0;
  const activePass = result.passes[activeIndex];

  return (
    <div className="panel">
      <div className="panel-header">
        <span className="panel-title">
          Upcoming Passes — {result.satellite_name} (NORAD {result.norad_id})
        </span>
      </div>

      <div className="stat-grid">
        <div className="stat-card">
          <div className="stat-value">{result.pass_count}</div>
          <div className="stat-label">Passes Found</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">
            {Math.max(...result.passes.map((p) => p.max_elevation_deg)).toFixed(0)}°
          </div>
          <div className="stat-label">Best Elevation</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">
            {Math.round(
              result.passes.reduce((s, p) => s + p.duration_seconds, 0) / result.passes.length / 60
            )}
            m
          </div>
          <div className="stat-label">Avg Duration</div>
        </div>
      </div>

      <hr className="section-divider" />

      <PassTimeline
        passes={result.passes}
        windowStart={result.window_start_utc}
        windowEnd={result.window_end_utc}
        selectedIndex={activeIndex}
        onSelect={setSelected}
      />

      <hr className="section-divider" />

      <div style={{ maxHeight: 260, overflowY: "auto" }}>
        <table>
          <thead>
            <tr>
              <th>AOS (UTC)</th>
              <th>Max Elev. (UTC)</th>
              <th>LOS (UTC)</th>
              <th>Duration</th>
              <th>Max Elev.</th>
              <th>Az. (AOS→LOS)</th>
            </tr>
          </thead>
          <tbody>
            {result.passes.map((p, i) => (
              <tr
                key={i}
                onClick={() => setSelected(i)}
                style={{
                  cursor: "pointer",
                  background: activeIndex === i ? "rgba(77,216,230,0.08)" : undefined,
                }}
              >
                <td>{fmt(p.aos_utc)}</td>
                <td>{fmt(p.max_elevation_utc)}</td>
                <td>{fmt(p.los_utc)}</td>
                <td>{Math.round(p.duration_seconds / 60)}m {Math.round(p.duration_seconds % 60)}s</td>
                <td>{p.max_elevation_deg.toFixed(1)}°</td>
                <td className="mono">
                  {p.aos_azimuth_deg?.toFixed(0) ?? "—"}° → {p.los_azimuth_deg?.toFixed(0) ?? "—"}°
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <hr className="section-divider" />
      <span className="panel-title">Elevation Profile — Selected Pass</span>
      <ElevationChart pass={activePass} />
    </div>
  );
}
