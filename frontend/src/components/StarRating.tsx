interface Props {
  value: number | null;
  onChange: (v: number) => void;
}

export default function StarRating({ value, onChange }: Props) {
  return (
    <div className="flex gap-2">
      {[1, 2, 3, 4, 5].map((n) => {
        const active = value != null && n <= value;
        return (
          <button
            key={n}
            type="button"
            aria-label={`${n} star${n > 1 ? "s" : ""}`}
            onClick={() => onChange(n)}
            className="grid h-12 w-12 place-items-center rounded-xl border border-line bg-surface-2 transition active:scale-95"
            style={active ? { borderColor: "color-mix(in oklab, var(--color-amber) 50%, transparent)" } : undefined}
          >
            <svg width="22" height="22" viewBox="0 0 24 24" fill={active ? "var(--color-amber)" : "none"} stroke={active ? "var(--color-amber)" : "var(--color-faint)"} strokeWidth="1.5">
              <path d="M12 2.5l2.9 6 6.6.9-4.8 4.6 1.2 6.5L12 17.9 6.1 21l1.2-6.5L2.5 9.9l6.6-.9z" />
            </svg>
          </button>
        );
      })}
    </div>
  );
}
