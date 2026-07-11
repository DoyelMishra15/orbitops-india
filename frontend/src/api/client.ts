import type {
  DataSourceStatus,
  GroundStationPreset,
  SatelliteSummary,
  PassPredictionResponse,
  GroundStation,
  CommunicationRequest,
  ScheduleResult,
} from "../types";

const API_BASE_URL: string =
  (import.meta as unknown as { env: Record<string, string> }).env
    ?.VITE_API_BASE_URL ||
"https://ominous-garbanzo-pjr6wq67qv5gh7j67-8000.app.github.dev/api/v1";

export class ApiRequestError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
    this.name = "ApiRequestError";
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  let resp: Response;
  try {
    resp = await fetch(`${API_BASE_URL}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
  } catch {
    throw new ApiRequestError(
      0,
      "Could not reach the OrbitOps API. Is the backend running on the expected port?"
    );
  }

  if (!resp.ok) {
    let detail = `Request failed with status ${resp.status}`;
    try {
      const body = await resp.json();
      if (body?.detail) {
        detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
      }
    } catch {
      /* ignore parse errors, keep default detail */
    }
    throw new ApiRequestError(resp.status, detail);
  }

  return (await resp.json()) as T;
}

export const api = {
  health: () => request<{ status: string; service: string; version: string }>("/health"),

  dataSourceStatus: () => request<DataSourceStatus>("/data-source/status"),

  groundStationPresets: () => request<GroundStationPreset[]>("/ground-stations/presets"),

  listSatellites: (query?: string) =>
    request<SatelliteSummary[]>(`/satellites${query ? `?q=${encodeURIComponent(query)}` : ""}`),

  predictPasses: (payload: {
    norad_id: number;
    ground_station: GroundStation;
    start_time_utc: string;
    duration_hours: number;
  }) =>
    request<PassPredictionResponse>("/passes/predict", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  generateSchedule: (payload: { ground_station: GroundStation; requests: CommunicationRequest[] }) =>
    request<ScheduleResult>("/schedule/generate", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  exportScheduleUrl: () => `${API_BASE_URL}/export/schedule`,
};

export { API_BASE_URL };
