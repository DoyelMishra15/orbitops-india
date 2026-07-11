import { useEffect, useState } from "react";
import type { SatelliteSummary } from "../types";
import { api } from "../api/client";
import { LoadingState, ErrorBanner, EmptyState } from "./StatusStates";

interface Props {
  selected: SatelliteSummary | null;
  onSelect: (sat: SatelliteSummary) => void;
}

export function SatelliteSelector({ selected, onSelect }: Props) {
  const [satellites, setSatellites] = useState<SatelliteSummary[]>([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    api
      .listSatellites()
      .then((sats) => {
        setSatellites(sats);
        setError(null);
        if (!selected && sats.length > 0) onSelect(sats[0]);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const filtered = query
    ? satellites.filter(
        (s) =>
          s.name.toLowerCase().includes(query.toLowerCase()) ||
          String(s.norad_id).includes(query)
      )
    : satellites;

  return (
    <div className="panel">
      <div className="panel-header">
        <span className="panel-title">Satellite</span>
      </div>

      <div className="field-group">
        <label htmlFor="sat-search">Search by name or NORAD ID</label>
        <input
          id="sat-search"
          type="text"
          placeholder="e.g. VANGUARD or 5"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      </div>

      {loading && <LoadingState label="Loading satellite catalogue…" />}
      {error && <ErrorBanner message={error} />}
      {!loading && !error && filtered.length === 0 && (
        <EmptyState label="No satellites match your search." />
      )}

      {!loading && !error && filtered.length > 0 && (
        <div style={{ maxHeight: 220, overflowY: "auto" }}>
          <table>
            <thead>
              <tr>
                <th>Satellite</th>
                <th>NORAD ID</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((s) => (
                <tr
                  key={s.norad_id}
                  onClick={() => onSelect(s)}
                  style={{
                    cursor: "pointer",
                    background:
                      selected?.norad_id === s.norad_id ? "rgba(77,216,230,0.08)" : undefined,
                  }}
                >
                  <td>{s.name}</td>
                  <td className="mono">{s.norad_id}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
