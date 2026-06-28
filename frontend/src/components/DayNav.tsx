import { isoAddDays, relativeDayWord, shortDate, dayDiffFromToday } from "../lib/format";

interface Props {
  dateIso: string;
  onChange: (iso: string) => void;
}

function Arrow({ dir }: { dir: "left" | "right" }) {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      {dir === "left" ? <path d="M15 18l-6-6 6-6" /> : <path d="M9 18l6-6-6-6" />}
    </svg>
  );
}

export default function DayNav({ dateIso, onChange }: Props) {
  const isToday = dayDiffFromToday(dateIso) === 0;
  const word = relativeDayWord(dateIso);

  return (
    <div className="flex items-center justify-between gap-2">
      <button
        aria-label="Previous day"
        onClick={() => onChange(isoAddDays(dateIso, -1))}
        className="grid h-11 w-11 place-items-center rounded-full border border-line bg-surface-2 text-muted transition hover:border-line-bright hover:text-text active:scale-95"
      >
        <Arrow dir="left" />
      </button>

      <button
        onClick={() => !isToday && onChange(todayIso())}
        disabled={isToday}
        className="flex min-h-[44px] flex-col items-center justify-center px-3 leading-tight disabled:cursor-default"
      >
        <span className="font-display text-lg font-semibold" style={{ color: isToday ? "var(--color-text)" : "var(--color-ember)" }}>
          {word}
        </span>
        <span className="tnum eyebrow text-faint">
          {shortDate(dateIso)}
          {!isToday && <span className="ml-1.5 text-ember">· tap for today</span>}
        </span>
      </button>

      <button
        aria-label="Next day"
        onClick={() => onChange(isoAddDays(dateIso, 1))}
        className="grid h-11 w-11 place-items-center rounded-full border border-line bg-surface-2 text-muted transition hover:border-line-bright hover:text-text active:scale-95"
      >
        <Arrow dir="right" />
      </button>
    </div>
  );
}

function todayIso(): string {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}
