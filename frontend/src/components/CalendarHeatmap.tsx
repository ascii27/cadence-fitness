import type { SessionLog, Status } from "../lib/types";
import { STATUS_COLOR } from "../lib/format";

interface Props {
  logs: SessionLog[];
  weeks?: number;
  onSelect: (date: string) => void;
  selected?: string | null;
}

function isoOf(d: Date): string {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

const DAY_LABELS = ["M", "T", "W", "T", "F", "S", "S"];

export default function CalendarHeatmap({ logs, weeks = 12, onSelect, selected }: Props) {
  const statusByDate = new Map<string, Status>();
  for (const l of logs) if (l.status) statusByDate.set(l.session_date, l.status);

  const today = new Date();
  today.setHours(0, 0, 0, 0);
  // Monday of the current week.
  const mondayThisWeek = new Date(today);
  const dow = (today.getDay() + 6) % 7; // 0 = Monday
  mondayThisWeek.setDate(today.getDate() - dow);

  const start = new Date(mondayThisWeek);
  start.setDate(mondayThisWeek.getDate() - (weeks - 1) * 7);

  const columns: { date: string; future: boolean; status?: Status }[][] = [];
  for (let w = 0; w < weeks; w++) {
    const col: { date: string; future: boolean; status?: Status }[] = [];
    for (let d = 0; d < 7; d++) {
      const cell = new Date(start);
      cell.setDate(start.getDate() + w * 7 + d);
      const iso = isoOf(cell);
      col.push({ date: iso, future: cell > today, status: statusByDate.get(iso) });
    }
    columns.push(col);
  }

  return (
    <div className="flex gap-3">
      <div className="flex flex-col justify-between py-[2px] pr-0.5">
        {DAY_LABELS.map((d, i) => (
          <span key={i} className="eyebrow h-[14px] text-[9px] leading-[14px] text-faint">
            {d}
          </span>
        ))}
      </div>
      <div className="flex flex-1 gap-[4px] overflow-x-auto">
        {columns.map((col, ci) => (
          <div key={ci} className="flex flex-col gap-[4px]">
            {col.map((cell) => {
              const color = cell.status ? STATUS_COLOR[cell.status] : undefined;
              const isSel = selected === cell.date;
              return (
                <button
                  key={cell.date}
                  disabled={cell.future}
                  onClick={() => onSelect(cell.date)}
                  title={cell.date}
                  className="h-[14px] w-[14px] rounded-[3px] transition-transform hover:scale-110 disabled:cursor-default disabled:hover:scale-100"
                  style={{
                    background: color ?? "var(--color-surface-2)",
                    opacity: cell.future ? 0.25 : 1,
                    outline: isSel ? "1.5px solid var(--color-text)" : undefined,
                    outlineOffset: "1px",
                  }}
                />
              );
            })}
          </div>
        ))}
      </div>
    </div>
  );
}
