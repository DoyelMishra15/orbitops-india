import type { DataSourceStatus } from "../types";
import { StatusBadge } from "./StatusStates";

export function Header({ status }: { status: DataSourceStatus | null }) {
  return (
    <header className="app-header">
      <div className="brand">
        <div className="brand-mark" />
        <div>
          <div className="brand-title">ORBITOPS INDIA</div>
          <div className="brand-subtitle">Satellite Pass Planning &amp; Ground-Station Scheduling</div>
        </div>
      </div>
      <StatusBadge status={status} />
    </header>
  );
}
