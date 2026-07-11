import { useEffect, useState } from "react";
import type { GroundStation, GroundStationPreset } from "../types";
import { api } from "../api/client";

interface Props {
  value: GroundStation;
  onChange: (gs: GroundStation) => void;
}

export function GroundStationConfig({ value, onChange }: Props) {
  const [presets, setPresets] = useState<GroundStationPreset[]>([]);
  const [selectedPreset, setSelectedPreset] = useState<string>("custom");
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    api
      .groundStationPresets()
      .then(setPresets)
      .catch((e) => setLoadError(e.message));
  }, []);

  function applyPreset(id: string) {
    setSelectedPreset(id);
    if (id === "custom") return;
    const preset = presets.find((p) => p.id === id);
    if (preset) {
      onChange({
        name: preset.name,
        latitude_deg: preset.latitude_deg,
        longitude_deg: preset.longitude_deg,
        altitude_m: preset.altitude_m,
        min_elevation_deg: value.min_elevation_deg,
      });
    }
  }

  return (
    <div className="panel">
      <div className="panel-header">
        <span className="panel-title">Ground Station</span>
      </div>

      {loadError && <div className="error-banner">⚠ {loadError}</div>}

      <div className="field-group">
        <label htmlFor="preset-select">Demo preset (illustrative, not verified facilities)</label>
        <select
          id="preset-select"
          value={selectedPreset}
          onChange={(e) => applyPreset(e.target.value)}
        >
          <option value="custom">Custom coordinates</option>
          {presets.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name}
            </option>
          ))}
        </select>
      </div>

      <div className="field-group">
        <label htmlFor="gs-name">Station name</label>
        <input
          id="gs-name"
          type="text"
          value={value.name}
          onChange={(e) => onChange({ ...value, name: e.target.value })}
        />
      </div>

      <div className="field-row">
        <div className="field-group">
          <label htmlFor="gs-lat">Latitude (°)</label>
          <input
            id="gs-lat"
            type="number"
            step="0.0001"
            min={-90}
            max={90}
            value={value.latitude_deg}
            onChange={(e) => {
              setSelectedPreset("custom");
              onChange({ ...value, latitude_deg: parseFloat(e.target.value) });
            }}
          />
        </div>
        <div className="field-group">
          <label htmlFor="gs-lon">Longitude (°)</label>
          <input
            id="gs-lon"
            type="number"
            step="0.0001"
            min={-180}
            max={180}
            value={value.longitude_deg}
            onChange={(e) => {
              setSelectedPreset("custom");
              onChange({ ...value, longitude_deg: parseFloat(e.target.value) });
            }}
          />
        </div>
      </div>

      <div className="field-row">
        <div className="field-group">
          <label htmlFor="gs-alt">Altitude (m)</label>
          <input
            id="gs-alt"
            type="number"
            step="1"
            value={value.altitude_m}
            onChange={(e) => onChange({ ...value, altitude_m: parseFloat(e.target.value) })}
          />
        </div>
        <div className="field-group">
          <label htmlFor="gs-mask">Min. elevation mask (°)</label>
          <input
            id="gs-mask"
            type="number"
            step="1"
            min={0}
            max={45}
            value={value.min_elevation_deg}
            onChange={(e) => onChange({ ...value, min_elevation_deg: parseFloat(e.target.value) })}
          />
        </div>
      </div>
      <p className="muted" style={{ fontSize: 11.5 }}>
        Presets are illustrative city/campus coordinates for demonstration only — not verified
        operational ground-station facilities, and not affiliated with ISRO or any government body.
      </p>
    </div>
  );
}
