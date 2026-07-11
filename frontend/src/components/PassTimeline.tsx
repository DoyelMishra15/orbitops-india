import type { PassEvent } from "../types";

interface Props {
  passes: PassEvent[];
  windowStart: string;
  windowEnd: string;
  selectedIndex: number | null;
  onSelect: (index: number) => void;
}

export function PassTimeline({ passes, windowStart, windowEnd, selectedIndex, onSelect }: Props) {
  const start = new Date(windowStart).getTime();
  const end = new Date(windowEnd).getTime();
  const totalMs = Math.max(end - start, 1);

  return (
    <div className="timeline-wrap">
      <div
        style={{
          position: "relative",
          height: 46,
          background: "var(--bg-surface)",
          borderRadius: 6,
          border: "1px solid var(--border-subtle)",
          minWidth: 600,
        }}
      >
        {passes.map((p, i) => {
          const aos = new Date(p.aos_utc).getTime();
          const los = new Date(p.los_utc).getTime();
          const leftPct = (Math.max(aos - start, 0) / totalMs) * 100;
          const widthPct = Math.max(((los - aos) / totalMs) * 100, 0.4);
          const isSelected = selectedIndex === i;
          return (
            <div
              key={i}
              title={`AOS ${new Date(p.aos_utc).toLocaleString()} — max ${p.max_elevation_deg}°`}
              onClick={() => onSelect(i)}
              style={{
                position: "absolute",
                left: `${leftPct}%`,
                width: `${widthPct}%`,
                top: 8,
                height: 30,
                background: isSelected
                  ? "linear-gradient(180deg, var(--accent-cyan), var(--accent-cyan-dim))"
                  : "rgba(77, 216, 230, 0.35)",
                border: isSelected ? "1px solid var(--accent-cyan)" : "1px solid rgba(77,216,230,0.5)",
                borderRadius: 4,
                cursor: "pointer",
                minWidth: 3,
              }}
            />
          );
        })}
      </div>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          fontSize: 11,
          color: "var(--text-muted)",
          marginTop: 4,
          minWidth: 600,
        }}
      >
        <span>{new Date(windowStart).toLocaleString()}</span>
        <span>{new Date(windowEnd).toLocaleString()}</span>
      </div>
    </div>
  );
}
