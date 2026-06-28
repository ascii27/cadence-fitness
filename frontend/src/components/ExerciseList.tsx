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

  // Resolve a routine exercise to its catalog entry by slug, or by a normalized
  // name match (so routines that predate slugs, or omit them, still link up).
  const resolve = useMemo(() => {
    const bySlug = new Map<string, CatalogExercise>();
    const byNorm = new Map<string, CatalogExercise>();
    const norm = (s: string) => s.toLowerCase().replace(/[^a-z0-9]/g, "");
    for (const e of catalog.data ?? []) {
      bySlug.set(e.slug, e);
      byNorm.set(norm(e.slug), e);
      byNorm.set(norm(e.name), e);
    }
    return (ex: Exercise): CatalogExercise | undefined => {
      if (ex.slug && bySlug.has(ex.slug)) return bySlug.get(ex.slug);
      const k = norm(ex.name);
      return byNorm.get(k) ?? byNorm.get(k.replace(/s$/, "")) ?? undefined;
    };
  }, [catalog.data]);

  if (exercises.length === 0) return null;

  return (
    <>
      <ul className="divide-y divide-line border-y border-line">
        {exercises.map((ex, i) => {
          const detail = resolve(ex);
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
