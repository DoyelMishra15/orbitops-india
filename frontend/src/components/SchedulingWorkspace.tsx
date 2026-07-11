import { useState } from "react";
import type { CommunicationRequest, Priority, SatelliteSummary } from "../types";

interface Props {
  satellites: SatelliteSummary[];
  requests: CommunicationRequest[];
  onChange: (requests: CommunicationRequest[]) => void;
  onGenerate: () => void;
  generating: boolean;
}

const PRIORITIES: Priority[] = ["LOW", "MEDIUM", "HIGH", "CRITICAL"];

function defaultWindow() {
  const start = new Date(Date.now() + 5 * 60 * 1000);
  const end = new Date(Date.now() + 48 * 60 * 60 * 1000);
  return { start, end };
}

export function SchedulingWorkspace({ satellites, requests, onChange, onGenerate, generating }: Props) {
  const [norad, setNorad] = useState<number | "">(satellites[0]?.norad_id ?? "");
  const [priority, setPriority] = useState<Priority>("MEDIUM");
  const [minElevation, setMinElevation] = useState(10);
  const [minContact, setMinContact] = useState(60);

  function addRequest() {
    if (norad === "") return;
    const sat = satellites.find((s) => s.norad_id === norad);
    const { start, end } = defaultWindow();
    const newRequest: CommunicationRequest = {
      request_id: `REQ-${Date.now()}`,
      norad_id: Number(norad),
      satellite_name: sat?.name,
      priority,
      earliest_start_utc: start.toISOString(),
      latest_end_utc: end.toISOString(),
      min_elevation_deg: minElevation,
      min_contact_seconds: minContact,
    };
    onChange([...requests, newRequest]);
  }

  function removeRequest(id: string) {
    onChange(requests.filter((r) => r.request_id !== id));
  }

  return (
    <div className="panel">
      <div className="panel-header">
        <span className="panel-title">Scheduling Workspace</span>
      </div>

      <div className="field-row">
        <div className="field-group">
          <label htmlFor="req-sat">Satellite</label>
          <select id="req-sat" value={norad} onChange={(e) => setNorad(Number(e.target.value))}>
            {satellites.map((s) => (
              <option key={s.norad_id} value={s.norad_id}>
                {s.name} ({s.norad_id})
              </option>
            ))}
          </select>
        </div>
        <div className="field-group">
          <label htmlFor="req-priority">Priority</label>
          <select
            id="req-priority"
            value={priority}
            onChange={(e) => setPriority(e.target.value as Priority)}
          >
            {PRIORITIES.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="field-row">
        <div className="field-group">
          <label htmlFor="req-elev">Min. elevation (°)</label>
          <input
            id="req-elev"
            type="number"
            min={0}
            max={45}
            value={minElevation}
            onChange={(e) => setMinElevation(parseFloat(e.target.value))}
          />
        </div>
        <div className="field-group">
          <label htmlFor="req-contact">Min. contact (s)</label>
          <input
            id="req-contact"
            type="number"
            min={1}
            value={minContact}
            onChange={(e) => setMinContact(parseFloat(e.target.value))}
          />
        </div>
      </div>

      <button className="btn btn-block" onClick={addRequest} disabled={satellites.length === 0}>
        + Add Communication Request
      </button>

      <hr className="section-divider" />

      <span className="panel-title">Pending Requests ({requests.length}/50)</span>
      <div style={{ display: "flex", flexDirection: "column", gap: 8, marginTop: 10 }}>
        {requests.length === 0 && <span className="muted">No requests added yet.</span>}
        {requests.map((r) => (
          <div className="request-card" key={r.request_id}>
            <div>
              <div>
                <strong>{r.satellite_name ?? r.norad_id}</strong>{" "}
                <span className={`priority-${r.priority}`}>{r.priority}</span>
              </div>
              <div className="muted" style={{ fontSize: 11 }}>
                {new Date(r.earliest_start_utc).toLocaleString()} →{" "}
                {new Date(r.latest_end_utc).toLocaleString()}
              </div>
            </div>
            <button className="btn btn-sm" onClick={() => removeRequest(r.request_id)}>
              Remove
            </button>
          </div>
        ))}
      </div>

      <hr className="section-divider" />

      <button
        className="btn btn-primary btn-block"
        onClick={onGenerate}
        disabled={requests.length === 0 || generating}
      >
        {generating ? "Generating schedule…" : "Generate Conflict-Free Schedule"}
      </button>
    </div>
  );
}
