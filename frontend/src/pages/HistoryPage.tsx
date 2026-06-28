import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useAdherence, useHistory } from "../lib/queries";
import type { SessionLog, SessionType } from "../lib/types";
import { STATUS_COLOR, titleCase, shortDate, weekdayLong, withinEditWindow } from "../lib/format";
import CalendarHeatmap from "../components/CalendarHeatmap";
import TypeBadge from "../components/TypeBadge";
import Skeleton from "../components/Skeleton";

const FILTERS: { value: SessionType | "all"; label: string }[] = [
  { value: "all", label: "All" },
  { value: "run", label: "Run" },
  { value: "strength", label: "Strength" },
  { value: "mobility", label: "Mobility" },
];

function Stat({ value, label, accent }: { value: string | number; label: string; accent?: string }) {
  return (
    <div className="card flex-1 p-4">
      <div className="tnum font-mono text-3xl font-medium" style={{ color: accent }}>
        {value}
      </div>
      <div className="eyebrow mt-1 text-faint">{label}</div>
    </div>
  );
}

export default function HistoryPage() {
  const history = useHistory();
  const adherence = useAdherence();
  const [filter, setFilter] = useState<SessionType | "all">("all");
  const [selected, setSelected] = useState<string | null>(null);

  const logs = history.data ?? [];
  const byDate = useMemo(() => {
    const m = new Map<string, SessionLog>();
    for (const l of logs) if (!m.has(l.session_date)) m.set(l.session_date, l);
    return m;
  }, [logs]);

  const filtered = filter === "all" ? logs : logs.filter((l) => l.session_type === filter);
  const selectedLog = selected ? byDate.get(selected) : undefined;
  const thisWeek = adherence.data?.weeks.at(-1);

  return (
    <div className="space-y-6 stagger">
      <h1 className="font-display text-2xl">History</h1>

      {/* Adherence stats */}
      <div className="flex gap-3">
        {adherence.isLoading ? (
          <Skeleton className="h-24 w-full" />
        ) : (
          <>
            <Stat value={adherence.data?.current_streak ?? 0} label="Current streak" accent="var(--color-ember)" />
            <Stat value={adherence.data?.longest_streak ?? 0} label="Longest" />
            <Stat
              value={thisWeek ? `${thisWeek.completed}/${thisWeek.planned}` : "—"}
              label="This week"
              accent="var(--color-go)"
            />
          </>
        )}
      </div>

      {/* Heatmap */}
      <div className="card p-5">
        <p className="eyebrow mb-4 text-faint">Last 12 weeks</p>
        {history.isLoading ? (
          <Skeleton className="h-28 w-full" />
        ) : (
          <CalendarHeatmap logs={logs} onSelect={setSelected} selected={selected} />
        )}
        <div className="mt-4 flex flex-wrap gap-3 text-xs text-faint">
          {(["completed", "partial", "missed", "swapped"] as const).map((s) => (
            <span key={s} className="flex items-center gap-1.5">
              <span className="h-2.5 w-2.5 rounded-[3px]" style={{ background: STATUS_COLOR[s] }} />
              {titleCase(s)}
            </span>
          ))}
        </div>
      </div>

      {/* Day drawer */}
      {selected && (
        <div className="card p-5">
          <div className="flex items-center justify-between">
            <div>
              <p className="eyebrow text-faint">{weekdayLong(selected)}</p>
              <h3 className="mt-0.5 text-lg">{shortDate(selected)}</h3>
            </div>
            <button onClick={() => setSelected(null)} className="text-faint hover:text-text">✕</button>
          </div>
          {selectedLog ? (
            <div className="mt-4 space-y-2.5">
              <div className="flex items-center gap-2">
                <span className="h-2.5 w-2.5 rounded-full" style={{ background: STATUS_COLOR[selectedLog.status!] }} />
                <span className="font-medium">{titleCase(selectedLog.status!)}</span>
                <span className="text-faint">· {selectedLog.label}</span>
              </div>
              <div className="flex gap-4 text-sm text-muted">
                {selectedLog.duration_minutes != null && <span className="tnum">{selectedLog.duration_minutes} min</span>}
                {selectedLog.rounds_completed != null && <span className="tnum">{selectedLog.rounds_completed} rounds</span>}
                {selectedLog.rating != null && <span className="tnum text-amber">{"★".repeat(selectedLog.rating)}</span>}
              </div>
              {selectedLog.notes && <p className="text-sm text-muted">"{selectedLog.notes}"</p>}
              {withinEditWindow(selectedLog.logged_at) && (
                <Link to={`/log?date=${selected}`} className="eyebrow inline-block text-ember">Edit (within 24h)</Link>
              )}
            </div>
          ) : (
            <div className="mt-4">
              <p className="text-muted">No session logged this day.</p>
              <Link to={`/log?date=${selected}`} className="eyebrow mt-2 inline-block text-ember">Log missed workout</Link>
            </div>
          )}
        </div>
      )}

      {/* Filter + list */}
      <div>
        <div className="mb-3 flex gap-2">
          {FILTERS.map((f) => (
            <button
              key={f.value}
              onClick={() => setFilter(f.value)}
              className="rounded-full border px-3.5 py-1.5 text-sm transition"
              style={{
                borderColor: filter === f.value ? "var(--color-line-bright)" : "var(--color-line)",
                background: filter === f.value ? "var(--color-surface-2)" : "transparent",
                color: filter === f.value ? "var(--color-text)" : "var(--color-faint)",
              }}
            >
              {f.label}
            </button>
          ))}
        </div>

        {history.isLoading ? (
          <Skeleton className="h-40 w-full" />
        ) : filtered.length === 0 ? (
          <p className="py-8 text-center text-faint">No sessions logged yet.</p>
        ) : (
          <ul className="space-y-2">
            {filtered.map((l) => (
              <li key={l.log_id}>
                <button
                  onClick={() => setSelected(l.session_date)}
                  className="flex w-full items-center justify-between rounded-xl border border-line bg-surface px-4 py-3 text-left transition hover:border-line-bright"
                >
                  <span className="flex items-center gap-3">
                    <span className="h-2.5 w-2.5 rounded-full" style={{ background: l.status ? STATUS_COLOR[l.status] : "var(--color-faint)" }} />
                    <span>
                      <span className="block font-medium">{l.label ?? titleCase(l.session_type)}</span>
                      <span className="tnum text-xs text-faint">{shortDate(l.session_date)}</span>
                    </span>
                  </span>
                  <span className="flex items-center gap-3">
                    {l.duration_minutes != null && <span className="tnum text-sm text-muted">{l.duration_minutes}m</span>}
                    <TypeBadge type={l.session_type} />
                  </span>
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
