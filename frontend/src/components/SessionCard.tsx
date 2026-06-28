import { Link } from "react-router-dom";
import type { DerivedSession, Relativity, SessionLog } from "../lib/types";
import { STATUS_COLOR, titleCase } from "../lib/format";
import TypeBadge from "./TypeBadge";
import ExerciseList from "./ExerciseList";

interface Props {
  session: DerivedSession;
  log: SessionLog | null;
  dateLabel: string;
  relativity?: Relativity;
  logHref?: string;
}

export default function SessionCard({ session, log, dateLabel, relativity = "today", logHref = "/log" }: Props) {
  const logged = log?.status != null;
  const isFuture = relativity === "future";

  return (
    <div className="card relative overflow-hidden p-6">
      <div
        className="pointer-events-none absolute inset-x-0 top-0 h-px"
        style={{ background: "linear-gradient(90deg, transparent, var(--color-ember), transparent)" }}
      />

      <div className="flex items-center justify-between">
        <span className="eyebrow text-faint">{dateLabel}</span>
        <TypeBadge type={session.session_type} />
      </div>

      <h1 className="mt-3 font-display text-3xl font-semibold leading-tight">
        {session.label ?? titleCase(session.session_type)}
      </h1>

      {session.swapped && (
        <p className="mt-2 inline-flex items-center gap-2 rounded-lg bg-surface-2 px-3 py-1.5 text-xs text-go">
          ↺ Swapped to mobility — {titleCase(session.swap_reason ?? "")}
        </p>
      )}

      {/* Readout row */}
      <div className="mt-6 flex items-end gap-6">
        {session.duration_minutes != null && (
          <div>
            <div className="tnum font-mono text-4xl font-medium leading-none">
              {session.duration_minutes}
              <span className="ml-1 text-base text-faint">min</span>
            </div>
            <div className="eyebrow mt-1.5 text-faint">
              {session.modality === "amrap" ? "AMRAP" : "Target"}
            </div>
          </div>
        )}
        {session.hr_cap_bpm != null && (
          <div>
            <div className="tnum font-mono text-2xl font-medium leading-none text-sky">
              ≤{session.hr_cap_bpm}
              <span className="ml-1 text-sm text-faint">bpm</span>
            </div>
            <div className="eyebrow mt-1.5 text-faint">{session.hr_zone ?? "HR cap"}</div>
          </div>
        )}
      </div>

      {/* Exercises (strength/mobility) */}
      {session.exercises.length > 0 && (
        <div className="mt-6">
          <ExerciseList exercises={session.exercises} />
        </div>
      )}

      {session.progression_rule && (
        <p className="mt-4 text-sm text-muted">
          <span className="text-faint">Progression · </span>
          {session.progression_rule}
        </p>
      )}

      {/* CTA / logged state */}
      <div className="mt-7">
        {logged ? (
          <div className="flex items-center justify-between rounded-xl border border-line bg-surface-2 px-4 py-3">
            <span className="flex items-center gap-2.5">
              <span className="h-2.5 w-2.5 rounded-full" style={{ background: STATUS_COLOR[log!.status!] }} />
              <span className="font-medium">{titleCase(log!.status!)}</span>
              {log!.duration_minutes != null && (
                <span className="tnum text-sm text-faint">· {log!.duration_minutes} min</span>
              )}
            </span>
            {!isFuture && (
              <Link to={logHref} className="eyebrow text-ember">
                Edit
              </Link>
            )}
          </div>
        ) : isFuture ? (
          <div className="flex items-center justify-center gap-2 rounded-xl border border-dashed border-line px-4 py-3 text-faint">
            <span className="eyebrow">Upcoming · preview</span>
          </div>
        ) : (
          <Link
            to={logHref}
            className="flex min-h-[56px] items-center justify-center rounded-full bg-ember text-lg font-semibold text-ink transition-transform active:scale-[0.98]"
          >
            {relativity === "today" ? "Log Workout" : "Log this day"}
          </Link>
        )}
      </div>
    </div>
  );
}
