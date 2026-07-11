export type DataMode = "live" | "demo_archive";
export type Priority = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

export interface GroundStation {
  name: string;
  latitude_deg: number;
  longitude_deg: number;
  altitude_m: number;
  min_elevation_deg: number;
}

export interface GroundStationPreset {
  id: string;
  name: string;
  latitude_deg: number;
  longitude_deg: number;
  altitude_m: number;
  note: string;
}

export interface SatelliteSummary {
  norad_id: number;
  name: string;
  tle_epoch?: string | null;
  source: DataMode;
}

export interface DataSourceStatus {
  mode: DataMode;
  provider: string;
  last_refreshed?: string | null;
  satellite_count: number;
  message: string;
}

export interface PassEvent {
  aos_utc: string;
  los_utc: string;
  max_elevation_utc: string;
  max_elevation_deg: number;
  duration_seconds: number;
  aos_azimuth_deg?: number | null;
  los_azimuth_deg?: number | null;
  max_elevation_azimuth_deg?: number | null;
  sunlit_at_max?: boolean | null;
}

export interface PassPredictionResponse {
  norad_id: number;
  satellite_name: string;
  ground_station: GroundStation;
  data_mode: DataMode;
  window_start_utc: string;
  window_end_utc: string;
  passes: PassEvent[];
  pass_count: number;
}

export interface CommunicationRequest {
  request_id: string;
  norad_id: number;
  satellite_name?: string;
  priority: Priority;
  earliest_start_utc: string;
  latest_end_utc: string;
  min_elevation_deg: number;
  min_contact_seconds: number;
}

export interface ScheduledContact {
  request_id: string;
  norad_id: number;
  satellite_name?: string | null;
  priority: string;
  aos_utc: string;
  los_utc: string;
  max_elevation_deg: number;
  scheduled_start_utc: string;
  scheduled_end_utc: string;
  score: number;
  reason: string;
}

export interface RejectedRequest {
  request_id: string;
  norad_id: number;
  reason: string;
}

export interface ScheduleResult {
  ground_station: GroundStation;
  scheduled: ScheduledContact[];
  rejected: RejectedRequest[];
  total_requests: number;
  scheduled_count: number;
  rejected_count: number;
  utilization_seconds: number;
  window_start_utc?: string | null;
  window_end_utc?: string | null;
  utilization_pct: number;
}

export interface ApiError {
  detail: string;
  errors?: unknown;
}
