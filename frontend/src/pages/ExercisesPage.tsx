import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useExercises } from "../lib/queries";
import type { CatalogExercise } from "../lib/types";
import ExerciseDetail from "../components/ExerciseDetail";
import Skeleton from "../components/Skeleton";

const CATEGORY_ORDER: { key: string; label: string }[] = [
  { key: "push", label: "Push" },
  { key: "pull", label: "Pull & Posterior" },
  { key: "core", label: "Core" },
  { key: "lower", label: "Lower Body" },
  { key: "mobility", label: "Mobility" },
  { key: "conditioning", label: "Conditioning" },
];

export default function ExercisesPage() {
  const catalog = useExercises();
  const [selected, setSelected] = useState<CatalogExercise | null>(null);

  const grouped = useMemo(() => {
    const m = new Map<string, CatalogExercise[]>();
    for (const e of catalog.data ?? []) {
      const arr = m.get(e.category) ?? [];
      arr.push(e);
      m.set(e.category, arr);
    }
    return m;
  }, [catalog.data]);

  return (
    <div className="space-y-6 stagger">
      <div className="flex items-center justify-between">
        <h1 className="font-display text-2xl">Exercise Library</h1>
        <Link to="/goals" className="eyebrow text-faint hover:text-text">‹ Goals</Link>
      </div>
      <p className="-mt-3 text-sm text-muted">
        {catalog.data?.length ?? "…"} no-equipment movements Eva can program. Tap any for instructions and form cues.
      </p>

      {catalog.isLoading ? (
        <Skeleton className="h-96 w-full" />
      ) : (
        CATEGORY_ORDER.filter((c) => grouped.has(c.key)).map((cat) => (
          <section key={cat.key}>
            <h2 className="eyebrow mb-3 text-faint">{cat.label}</h2>
            <div className="grid grid-cols-2 gap-3">
              {(grouped.get(cat.key) ?? []).map((ex) => (
                <button
                  key={ex.slug}
                  onClick={() => setSelected(ex)}
                  className="card overflow-hidden p-0 text-left transition hover:border-line-bright active:scale-[0.99]"
                >
                  <div className="grid place-items-center bg-ink-2 py-3">
                    <img src={ex.image} alt="" className="h-24 w-auto" loading="lazy" />
                  </div>
                  <div className="flex items-center justify-between px-3 py-2.5">
                    <span className="min-w-0">
                      <span className="block truncate text-sm font-medium">{ex.name}</span>
                      <span className="eyebrow text-faint">{ex.difficulty}</span>
                    </span>
                    <span
                      className="h-2 w-2 shrink-0 rounded-full"
                      title={ex.low_impact ? "Low impact" : "Higher impact"}
                      style={{ background: ex.low_impact ? "var(--color-go)" : "var(--color-amber)" }}
                    />
                  </div>
                </button>
              ))}
            </div>
          </section>
        ))
      )}

      <ExerciseDetail exercise={selected} onClose={() => setSelected(null)} />
    </div>
  );
}
