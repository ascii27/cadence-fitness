interface Props {
  value: number;
  onChange: (v: number) => void;
  min?: number;
  max?: number;
  label?: string;
}

export default function Stepper({ value, onChange, min = 0, max = 99, label }: Props) {
  const clamp = (v: number) => Math.max(min, Math.min(max, v));
  return (
    <div className="flex items-center gap-4">
      <button
        type="button"
        aria-label={`decrease ${label ?? ""}`}
        onClick={() => onChange(clamp(value - 1))}
        className="grid h-14 w-14 place-items-center rounded-xl border border-line bg-surface-2 text-2xl transition active:scale-95"
      >
        −
      </button>
      <span className="tnum w-12 text-center font-mono text-3xl font-medium">{value}</span>
      <button
        type="button"
        aria-label={`increase ${label ?? ""}`}
        onClick={() => onChange(clamp(value + 1))}
        className="grid h-14 w-14 place-items-center rounded-xl border border-line bg-surface-2 text-2xl transition active:scale-95"
      >
        +
      </button>
    </div>
  );
}
