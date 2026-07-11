import type { DataSourceStatus } from "../types";

export function StatusBadge({ status }: { status: DataSourceStatus | null }) {
  if (!status) {
    return (
      <span className="badge badge-demo">
        <span className="badge-dot" /> Checking data source…
      </span>
    );
  }
  const isLive = status.mode === "live";
  return (
    <span
      className={isLive ? "badge badge-live" : "badge badge-demo"}
      title={status.message}
    >
      <span className="badge-dot" />
      {isLive ? "Live Data" : "Demo / Archive Mode"}
    </span>
  );
}

export function LoadingState({ label = "Loading…" }: { label?: string }) {
  return (
    <div className="state-box">
      <div className="spinner" />
      <span>{label}</span>
    </div>
  );
}

export function ErrorBanner({ message }: { message: string }) {
  return <div className="error-banner">⚠ {message}</div>;
}

export function EmptyState({ label }: { label: string }) {
  return (
    <div className="state-box">
      <span>{label}</span>
    </div>
  );
}
