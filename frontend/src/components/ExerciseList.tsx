import { useMemo, useState } from "react";
import type { CatalogExercise, Exercise } from "../lib/types";
import { useExercises } from "../lib/queries";
import ExerciseDetail from "./ExerciseDetail";

interface Props {
  exercises: Exercise[];
}

export default function ExerciseList({ exercises }: Props) {
  const catalog = useExercises();
  const [selected, setSelected] = useState<CatalogExercise | null>(null);

  const bySlug = useMemo(() => {
    const m = new Map<string, CatalogExercise>();
    for (const e of catalog.data ?? []) m.set(e.slug, e);
    return m;
  }, [catalog.data]);

  if (exercises.length === 0) return null;

  return (
    <>
      <ul className="divide-y divide-line border-y border-line">
        {exercises.map((ex, i) => {
          const detail = ex.slug ? bySlug.get(ex.slug) : undefined;
          const sub = ex.note ?? (ex.reps ? `${ex.reps} reps` : "");
          const row = (
            <span className="flex items-center gap-3">
              {detail ? (
                <img src={detail.image} alt="" className="h-10 w-12 shrink-0 rounded-md bg-ink-2" loading="lazy" />
              ) : (
                <span className="h-2 w-2 shrink-0 rounded-full bg-ember" />
              )}
              <span className="min-w-0">
                <span className="block truncate font-medium">{ex.name}</span>
                {sub && <span className="block truncate text-sm text-faint">{sub}</span>}
              </span>
            </span>
          );
          return (
            <li key={i}>
              {detail ? (
                <button
                  onClick={() => setSelected(detail)}
                  className="flex w-full items-center justify-between py-3 text-left transition-colors hover:text-text"
                >
                  {row}
                  <span className="eyebrow shrink-0 text-faint">How-to ›</span>
                </button>
              ) : (
                <div className="flex items-center justify-between py-3">{row}</div>
              )}
            </li>
          );
        })}
      </ul>
      <ExerciseDetail exercise={selected} onClose={() => setSelected(null)} />
    </>
  );
}
