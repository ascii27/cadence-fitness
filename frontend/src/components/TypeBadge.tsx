import type { SessionType } from "../lib/types";

const META: Record<SessionType, { label: string; color: string }> = {
  run: { label: "Run", color: "var(--color-sky)" },
  strength: { label: "Strength", color: "var(--color-ember)" },
  mobility: { label: "Mobility", color: "var(--color-go)" },
  rest: { label: "Rest", color: "var(--color-faint)" },
};

export default function TypeBadge({ type }: { type: SessionType }) {
  const m = META[type];
  return (
    <span
      className="eyebrow inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1"
      style={{
        color: m.color,
        borderColor: `color-mix(in oklab, ${m.color} 35%, transparent)`,
        background: `color-mix(in oklab, ${m.color} 10%, transparent)`,
      }}
    >
      <span className="h-1.5 w-1.5 rounded-full" style={{ background: m.color }} />
      {m.label}
    </span>
  );
}
