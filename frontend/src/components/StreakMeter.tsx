interface Props {
  streak: number;
  label?: string;
}

/** Flame-styled streak readout. */
export default function StreakMeter({ streak, label = "Day streak" }: Props) {
  const lit = streak > 0;
  return (
    <div className="flex items-center gap-3">
      <span
        className="grid h-11 w-11 place-items-center rounded-full border"
        style={{
          borderColor: lit ? "color-mix(in oklab, var(--color-ember) 50%, transparent)" : "var(--color-line)",
          background: lit ? "color-mix(in oklab, var(--color-ember) 14%, transparent)" : "transparent",
        }}
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill={lit ? "var(--color-ember)" : "var(--color-faint)"}>
          <path d="M12 2c1 3 4 4.5 4 8a4 4 0 0 1-8 0c0-1 .3-1.8.8-2.5C7 8 6 10 6 12.5a6 6 0 0 0 12 0c0-4.5-3.5-7-6-10.5z" />
        </svg>
      </span>
      <div className="leading-tight">
        <div className="tnum font-display text-2xl font-semibold" style={{ color: lit ? "var(--color-text)" : "var(--color-muted)" }}>
          {streak}
        </div>
        <div className="eyebrow text-faint">{label}</div>
      </div>
    </div>
  );
}
