import { useEffect, useState } from "react";
import { Header } from "./components/Header";
import { GroundStationConfig } from "./components/GroundStationConfig";
import { SatelliteSelector } from "./components/SatelliteSelector";
import { PassPredictionForm } from "./components/PassPredictionForm";
import { PassResults } from "./components/PassResults";
import { SchedulingWorkspace } from "./components/SchedulingWorkspace";
import { ScheduleResults } from "./components/ScheduleResults";
import { ErrorBanner, LoadingState } from "./components/StatusStates";
import { api, ApiRequestError } from "./api/client";
import type {
  DataSourceStatus,
  GroundStation,
  SatelliteSummary,
  PassPredictionResponse,
  CommunicationRequest,
  ScheduleResult,
} from "./types";

const DEFAULT_GROUND_STATION: GroundStation = {
  name: "Bhubaneswar (Demo Campus Site)",
  latitude_deg: 20.2961,
  longitude_deg: 85.8245,
  altitude_m: 45.0,
  min_elevation_deg: 10.0,
};

export default function App() {
  const [status, setStatus] = useState<DataSourceStatus | null>(null);
  const [backendUnreachable, setBackendUnreachable] = useState(false);

  const [groundStation, setGroundStation] = useState<GroundStation>(DEFAULT_GROUND_STATION);
  const [satellites, setSatellites] = useState<SatelliteSummary[]>([]);
  const [selectedSat, setSelectedSat] = useState<SatelliteSummary | null>(null);

  const [predicting, setPredicting] = useState(false);
  const [predictError, setPredictError] = useState<string | null>(null);
  const [passResult, setPassResult] = useState<PassPredictionResponse | null>(null);

  const [requests, setRequests] = useState<CommunicationRequest[]>([]);
  const [generating, setGenerating] = useState(false);
  const [scheduleError, setScheduleError] = useState<string | null>(null);
  const [scheduleResult, setScheduleResult] = useState<ScheduleResult | null>(null);

  useEffect(() => {
    api
      .dataSourceStatus()
      .then(setStatus)
      .catch((e) => {
        if (e instanceof ApiRequestError && e.status === 0) setBackendUnreachable(true);
      });
    api.listSatellites().then(setSatellites).catch(() => undefined);
  }, []);

  async function handlePredict(startTimeUtc: string, durationHours: number) {
    if (!selectedSat) return;
    setPredicting(true);
    setPredictError(null);
    try {
      const result = await api.predictPasses({
        norad_id: selectedSat.norad_id,
        ground_station: groundStation,
        start_time_utc: startTimeUtc,
        duration_hours: durationHours,
      });
      setPassResult(result);
    } catch (e) {
      setPredictError(e instanceof Error ? e.message : "Unknown error");
      setPassResult(null);
    } finally {
      setPredicting(false);
    }
  }

  async function handleGenerateSchedule() {
    setGenerating(true);
    setScheduleError(null);
    try {
      const result = await api.generateSchedule({ ground_station: groundStation, requests });
      setScheduleResult(result);
    } catch (e) {
      setScheduleError(e instanceof Error ? e.message : "Unknown error");
      setScheduleResult(null);
    } finally {
      setGenerating(false);
    }
  }

  if (backendUnreachable) {
    return (
      <div className="app-shell">
        <Header status={null} />
        <div className="app-main" style={{ gridTemplateColumns: "1fr" }}>
          <ErrorBanner message="Could not reach the OrbitOps backend API. Start it with: cd backend && uvicorn app.main:app --reload --port 8000" />
        </div>
      </div>
    );
  }

  return (
    <div className="app-shell">
      <Header status={status} />

      <main className="app-main">
        <div className="column">
          <GroundStationConfig value={groundStation} onChange={setGroundStation} />
          <SatelliteSelector selected={selectedSat} onSelect={setSelectedSat} />
          <PassPredictionForm onSubmit={handlePredict} loading={predicting} disabled={!selectedSat} />
          {predictError && <ErrorBanner message={predictError} />}
        </div>

        <div className="column">
          {predicting ? <LoadingState label="Propagating orbit and searching for passes…" /> : <PassResults result={passResult} />}

          <SchedulingWorkspace
            satellites={satellites}
            requests={requests}
            onChange={setRequests}
            onGenerate={handleGenerateSchedule}
            generating={generating}
          />
          {scheduleError && <ErrorBanner message={scheduleError} />}

          {generating ? (
            <LoadingState label="Resolving conflicts and optimising the schedule…" />
          ) : (
            <ScheduleResults result={scheduleResult} />
          )}
        </div>
      </main>

      <footer className="app-footer">
        OrbitOps India — Educational / portfolio project. Not affiliated with ISRO or any government
        body. Uses legitimate public orbital data (Celestrak) or a clearly labelled offline demo
        fixture. Not for operational mission use.
      </footer>
    </div>
  );
}
