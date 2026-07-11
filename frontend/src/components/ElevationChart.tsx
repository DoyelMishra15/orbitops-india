import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import type { PassEvent } from "../types";

export function ElevationChart({ pass }: { pass: PassEvent }) {
  const aosT = new Date(pass.aos_utc).getTime();
  const maxT = new Date(pass.max_elevation_utc).getTime();
  const losT = new Date(pass.los_utc).getTime();

  // Approximate elevation profile using the three known geometric points
  // (AOS = 0 deg, max-elevation point, LOS = 0 deg). This is a visual
  // approximation for quick-look purposes, not a re-sampled propagation —
  // labelled as such in the UI.
  const data = [
    { t: 0, label: "AOS", elevation: 0 },
    {
      t: Math.round(((maxT - aosT) / Math.max(losT - aosT, 1)) * 100),
      label: "MAX",
      elevation: pass.max_elevation_deg,
    },
    { t: 100, label: "LOS", elevation: 0 },
  ].sort((a, b) => a.t - b.t);

  return (
    <div>
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" />
          <XAxis
            dataKey="label"
            stroke="var(--text-muted)"
            tick={{ fontSize: 11, fill: "var(--text-muted)" }}
          />
          <YAxis
            domain={[0, 90]}
            stroke="var(--text-muted)"
            tick={{ fontSize: 11, fill: "var(--text-muted)" }}
            label={{
              value: "Elevation (°)",
              angle: -90,
              position: "insideLeft",
              fill: "var(--text-muted)",
              fontSize: 11,
            }}
          />
          <Tooltip
            contentStyle={{
              background: "var(--bg-panel-raised)",
              border: "1px solid var(--border-strong)",
              borderRadius: 6,
              fontSize: 12,
            }}
          />
          <Line
            type="monotone"
            dataKey="elevation"
            stroke="var(--accent-cyan)"
            strokeWidth={2}
            dot={{ r: 4, fill: "var(--accent-cyan)" }}
          />
        </LineChart>
      </ResponsiveContainer>
      <p className="muted" style={{ fontSize: 11 }}>
        Approximate profile through AOS → maximum elevation → LOS. Not a fully re-sampled
        propagation curve.
      </p>
    </div>
  );
}
