import type { ScheduleResult } from "../types";
import { api } from "../api/client";
import { EmptyState } from "./StatusStates";

export function ScheduleResults({ result }: { result: ScheduleResult | null }) {
  if (!result) {
    return (
      <div className="panel">
        <div className="panel-header">
          <span className="panel-title">Generated Schedule</span>
        </div>
        <EmptyState label="Add communication requests and generate a schedule to see results here." />
      </div>
    );
  }

  async function exportAs(format: "json" | "csv") {
    const resp = await fetch(`${api.exportScheduleUrl()}?format=${format}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(result),
    });
    const blob = await resp.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `orbitops_schedule.${format}`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="panel">
      <div className="panel-header">
        <span className="panel-title">Generated Schedule</span>
        <div style={{ display: "flex", gap: 6 }}>
          <button className="btn btn-sm" onClick={() => exportAs("json")}>
            Export JSON
          </button>
          <button className="btn btn-sm" onClick={() => exportAs("csv")}>
            Export CSV
          </button>
        </div>
      </div>

      <div className="stat-grid">
        <div className="stat-card">
          <div className="stat-value">{result.scheduled_count}</div>
          <div className="stat-label">Scheduled</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{result.rejected_count}</div>
          <div className="stat-label">Rejected</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{result.utilization_pct}%</div>
          <div className="stat-label">Window Utilization</div>
        </div>
      </div>

      <hr className="section-divider" />

      <span className="panel-title">Scheduled Contacts</span>
      {result.scheduled.length === 0 ? (
        <EmptyState label="No requests could be scheduled." />
      ) : (
        <table>
          <thead>
            <tr>
              <th>Request</th>
              <th>Satellite</th>
              <th>Priority</th>
              <th>Window (UTC)</th>
              <th>Max Elev.</th>
              <th>Score</th>
            </tr>
          </thead>
          <tbody>
            {result.scheduled.map((c) => (
              <tr key={c.request_id} title={c.reason}>
                <td className="mono">{c.request_id}</td>
                <td>{c.satellite_name ?? c.norad_id}</td>
                <td className={`priority-${c.priority}`}>{c.priority}</td>
                <td>
                  {new Date(c.scheduled_start_utc).toLocaleString()} →{" "}
                  {new Date(c.scheduled_end_utc).toLocaleTimeString()}
                </td>
                <td>{c.max_elevation_deg.toFixed(1)}°</td>
                <td className="mono">{c.score.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <hr className="section-divider" />

      <span className="panel-title">Rejected Requests &amp; Reasons</span>
      {result.rejected.length === 0 ? (
        <p className="muted">None — every request was scheduled.</p>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 6, marginTop: 8 }}>
          {result.rejected.map((r) => (
            <div key={r.request_id} className="request-card">
              <div>
                <strong className="mono">{r.request_id}</strong>
                <div className="muted" style={{ fontSize: 12 }}>
                  {r.reason}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
