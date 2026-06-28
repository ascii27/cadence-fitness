import { useEffect } from "react";
import type { CatalogExercise } from "../lib/types";
import { titleCase } from "../lib/format";

interface Props {
  exercise: CatalogExercise | null;
  onClose: () => void;
}

const UNIT_LABEL: Record<string, string> = {
  reps: "Reps",
  seconds: "Timed",
  reps_per_side: "Reps / side",
  seconds_per_side: "Timed / side",
};

export default function ExerciseDetail({ exercise, onClose }: Props) {
  useEffect(() => {
    if (!exercise) return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [exercise, onClose]);

  if (!exercise) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center sm:items-center" role="dialog" aria-modal="true">
      <button aria-label="Close" className="absolute inset-0 bg-ink/70 backdrop-blur-sm" onClick={onClose} />
      <div className="relative max-h-[88dvh] w-full max-w-xl overflow-y-auto rounded-t-3xl border border-line bg-surface p-6 pb-10 sm:rounded-3xl"
        style={{ animation: "rise 0.28s cubic-bezier(0.2,0.8,0.2,1)" }}>
        <div className="mx-auto mb-4 h-1 w-10 rounded-full bg-line sm:hidden" />

        <div className="flex items-start justify-between gap-3">
          <div>
            <p className="eyebrow text-faint">{titleCase(exercise.category)}</p>
            <h2 className="mt-1 font-display text-2xl font-semibold">{exercise.name}</h2>
          </div>
          <button onClick={onClose} className="grid h-9 w-9 place-items-center rounded-full border border-line text-faint hover:text-text">✕</button>
        </div>

        {/* Visual */}
        <div className="mt-4 grid place-items-center rounded-2xl border border-line bg-ink-2 py-4">
          <img src={exercise.image} alt={`${exercise.name} demonstration`} className="h-40 w-auto" loading="lazy" />
        </div>

        {/* Badges */}
        <div className="mt-4 flex flex-wrap gap-2 text-xs">
          <Badge>{titleCase(exercise.difficulty)}</Badge>
          <Badge>{UNIT_LABEL[exercise.unit] ?? titleCase(exercise.unit)}</Badge>
          <Badge>No equipment</Badge>
          {exercise.low_impact ? (
            <Badge accent="var(--color-go)">Low impact</Badge>
          ) : (
            <Badge accent="var(--color-amber)">Higher impact</Badge>
          )}
        </div>

        <div className="mt-3 flex flex-wrap gap-1.5">
          {exercise.target.map((t) => (
            <span key={t} className="rounded-full bg-surface-2 px-2.5 py-1 text-xs text-muted">{titleCase(t)}</span>
          ))}
        </div>

        {/* Instructions */}
        <h3 className="mt-6 eyebrow text-faint">How to</h3>
        <ol className="mt-2 space-y-2.5">
          {exercise.instructions.map((step, i) => (
            <li key={i} className="flex gap-3">
              <span className="tnum grid h-6 w-6 shrink-0 place-items-center rounded-full bg-ember/15 font-mono text-xs text-ember">{i + 1}</span>
              <span className="text-sm text-text">{step}</span>
            </li>
          ))}
        </ol>

        {/* Cues */}
        <h3 className="mt-6 eyebrow text-faint">Form cues</h3>
        <ul className="mt-2 space-y-1.5">
          {exercise.cues.map((c, i) => (
            <li key={i} className="flex gap-2 text-sm text-muted">
              <span className="text-ember">·</span>
              {c}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

function Badge({ children, accent }: { children: React.ReactNode; accent?: string }) {
  return (
    <span
      className="rounded-full border px-2.5 py-1"
      style={{
        color: accent ?? "var(--color-muted)",
        borderColor: accent ? `color-mix(in oklab, ${accent} 40%, transparent)` : "var(--color-line)",
        background: accent ? `color-mix(in oklab, ${accent} 10%, transparent)` : "var(--color-surface-2)",
      }}
    >
      {children}
    </span>
  );
}
