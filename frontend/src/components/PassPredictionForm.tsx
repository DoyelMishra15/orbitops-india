import { useState } from "react";

interface Props {
  onSubmit: (startTimeUtc: string, durationHours: number) => void;
  loading: boolean;
  disabled: boolean;
}

function nowLocalInputValue(): string {
  const d = new Date(Date.now() + 2 * 60 * 1000); // 2 min from now
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(
    d.getHours()
  )}:${pad(d.getMinutes())}`;
}

export function PassPredictionForm({ onSubmit, loading, disabled }: Props) {
  const [start, setStart] = useState(nowLocalInputValue());
  const [durationHours, setDurationHours] = useState(24);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const iso = new Date(start).toISOString();
    onSubmit(iso, durationHours);
  }

  return (
    <div className="panel">
      <div className="panel-header">
        <span className="panel-title">Prediction Window</span>
      </div>
      <form onSubmit={handleSubmit}>
        <div className="field-group">
          <label htmlFor="pw-start">Start time (your local time zone)</label>
          <input
            id="pw-start"
            type="datetime-local"
            value={start}
            onChange={(e) => setStart(e.target.value)}
            required
          />
        </div>
        <div className="field-group">
          <label htmlFor="pw-duration">Duration (hours, max 168 = 7 days)</label>
          <input
            id="pw-duration"
            type="number"
            min={0.5}
            max={168}
            step={0.5}
            value={durationHours}
            onChange={(e) => setDurationHours(parseFloat(e.target.value))}
            required
          />
        </div>
        <button type="submit" className="btn btn-primary btn-block" disabled={loading || disabled}>
          {loading ? "Calculating passes…" : "Calculate Passes"}
        </button>
      </form>
    </div>
  );
}
