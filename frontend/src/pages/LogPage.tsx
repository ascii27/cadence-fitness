import { useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useToday, useLogWorkout } from "../lib/queries";
import type { Status } from "../lib/types";
import { STATUS_COLOR, titleCase, shortDate, todayISO } from "../lib/format";
import StarRating from "../components/StarRating";
import Stepper from "../components/Stepper";
import Skeleton from "../components/Skeleton";

const STATUSES: Status[] = ["completed", "partial", "missed"];

export default function LogPage() {
  const [params] = useSearchParams();
  const dateParam = params.get("date");
  const today = useToday();
  const logMutation = useLogWorkout();

  const session = today.data?.session;
  const isAmrap = session?.modality === "amrap" || session?.session_type === "strength";
  const plannedDuration = session?.duration_minutes ?? 30;

  const [status, setStatus] = useState<Status>("completed");
  const [duration, setDuration] = useState<number>(plannedDuration);
  const [touchedDuration, setTouchedDuration] = useState(false);
  const [rounds, setRounds] = useState(0);
  const [rating, setRating] = useState<number | null>(null);
  const [notes, setNotes] = useState("");

  // Sync the default duration once today's plan loads (unless user edited it).
  const effectiveDuration = useMemo(() => {
    if (touchedDuration) return duration;
    return status === "missed" ? 0 : plannedDuration;
  }, [touchedDuration, duration, status, plannedDuration]);

  if (today.isLoading) {
    return <Skeleton className="h-96 w-full" />;
  }

  const targetDate = dateParam ?? today.data?.session_date ?? todayISO();
  const isPast = !!dateParam && dateParam !== today.data?.session_date;

  function submit() {
    logMutation.mutate({
      status,
      duration_minutes: effectiveDuration,
      session_date: targetDate,
      session_type: session?.session_type,
      label: session?.label ?? undefined,
      rounds_completed: isAmrap && status !== "missed" ? rounds : null,
      rating: rating,
      notes: notes.trim() || null,
      swap_reason: session?.swapped ? session.swap_reason : null,
    });
  }

  // Success state
  if (logMutation.isSuccess) {
    const result = logMutation.data;
    const queued = "queued" in result;
    return (
      <div className="card p-8 text-center stagger">
        <div className="mx-auto grid h-16 w-16 place-items-center rounded-full bg-surface-2" style={{ borderColor: "var(--color-go)" }}>
          <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="var(--color-go)" strokeWidth="2.5">
            <path d="M20 6 9 17l-5-5" />
          </svg>
        </div>
        <h2 className="mt-5 font-display text-2xl">{queued ? "Saved offline" : "Logged"}</h2>
        {queued ? (
          <p className="mt-2 text-muted">It'll sync automatically when you're back online.</p>
        ) : (
          <>
            <p className="mt-2 text-muted">
              Streak now <span className="tnum font-mono text-ember">{result.streak}</span> days.
            </p>
            {result.milestone_hit && (
              <p className="mt-3 inline-block rounded-full bg-ember/15 px-4 py-1.5 text-ember">
                🔥 {result.milestone_hit}-day milestone!
              </p>
            )}
          </>
        )}
        <Link to="/" className="mt-7 inline-flex min-h-[48px] items-center justify-center rounded-full bg-text px-8 font-medium text-ink">
          Back to Today
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6 stagger">
      <div className="flex items-center justify-between">
        <div>
          <p className="eyebrow text-faint">{isPast ? "Log past session" : "Log workout"}</p>
          <h1 className="mt-1 font-display text-2xl">{session?.label ?? "Session"}</h1>
        </div>
        <span className="tnum rounded-lg border border-line bg-surface-2 px-3 py-1.5 font-mono text-sm text-muted">
          {shortDate(targetDate)}
        </span>
      </div>

      {/* Status */}
      <div>
        <p className="eyebrow mb-2.5 text-faint">Status</p>
        <div className="grid grid-cols-3 gap-2">
          {STATUSES.map((s) => {
            const active = status === s;
            return (
              <button
                key={s}
                onClick={() => setStatus(s)}
                className="min-h-[52px] rounded-xl border bg-surface-2 font-medium transition active:scale-[0.98]"
                style={{
                  borderColor: active ? STATUS_COLOR[s] : "var(--color-line)",
                  color: active ? STATUS_COLOR[s] : "var(--color-muted)",
                  background: active ? `color-mix(in oklab, ${STATUS_COLOR[s]} 12%, var(--color-surface-2))` : undefined,
                }}
              >
                {titleCase(s)}
              </button>
            );
          })}
        </div>
      </div>

      {status !== "missed" && (
        <>
          {/* Duration */}
          <div>
            <div className="mb-2.5 flex items-center justify-between">
              <p className="eyebrow text-faint">Duration</p>
              <span className="tnum font-mono text-lg">
                {effectiveDuration}
                <span className="text-faint"> min</span>
              </span>
            </div>
            <input
              type="range"
              min={0}
              max={120}
              value={effectiveDuration}
              onChange={(e) => {
                setTouchedDuration(true);
                setDuration(Number(e.target.value));
              }}
              className="w-full accent-[var(--color-ember)]"
            />
          </div>

          {/* Rounds (AMRAP only) */}
          {isAmrap && (
            <div>
              <p className="eyebrow mb-2.5 text-faint">Rounds completed</p>
              <Stepper value={rounds} onChange={setRounds} label="rounds" />
            </div>
          )}

          {/* Rating */}
          <div>
            <p className="eyebrow mb-2.5 text-faint">How did it feel?</p>
            <StarRating value={rating} onChange={setRating} />
          </div>
        </>
      )}

      {/* Notes */}
      <div>
        <p className="eyebrow mb-2.5 text-faint">Notes</p>
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          rows={3}
          placeholder="Anything worth telling Eva — tightness, energy, terrain…"
          className="w-full resize-none rounded-xl border border-line bg-surface-2 p-4 text-text placeholder:text-faint focus:border-line-bright"
        />
      </div>

      {logMutation.isError && <p className="text-rose">Couldn't save. Try again.</p>}

      <div className="flex gap-3">
        <Link to="/" className="grid min-h-[56px] flex-1 place-items-center rounded-full border border-line bg-surface-2 font-medium text-muted">
          Cancel
        </Link>
        <button
          onClick={submit}
          disabled={logMutation.isPending}
          className="min-h-[56px] flex-[2] rounded-full bg-ember text-lg font-semibold text-ink transition active:scale-[0.98] disabled:opacity-60"
        >
          {logMutation.isPending ? "Saving…" : "Save"}
        </button>
      </div>
    </div>
  );
}
