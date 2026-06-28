import { useGoals, useRoutine } from "../lib/queries";
import { humanGoal, titleCase } from "../lib/format";
import TypeBadge from "../components/TypeBadge";
import Skeleton from "../components/Skeleton";

export default function GoalsPage() {
  const goals = useGoals();
  const routine = useRoutine();

  if (goals.isLoading) return <Skeleton className="h-72 w-full" />;

  const constraints = (goals.data?.constraints ?? {}) as Record<string, unknown>;
  const restDays = (constraints.rest_days as string[] | undefined) ?? [];
  const strengthCap = constraints.strength_cap_minutes as number | undefined;
  const updatedBy = goals.data?.updated_by ?? "—";
  const updatedAt = goals.data?.updated_at ? new Date(goals.data.updated_at).toLocaleDateString() : "—";

  return (
    <div className="space-y-6 stagger">
      <h1 className="font-display text-2xl">Goals</h1>

      <div className="card p-5">
        <p className="eyebrow text-faint">Active goals</p>
        <div className="mt-3 flex flex-wrap gap-2">
          {goals.data?.goals.map((g) => (
            <span
              key={g}
              className="rounded-full border border-line bg-surface-2 px-3.5 py-1.5 text-sm"
              style={g === "joint_longevity" ? { color: "var(--color-go)", borderColor: "color-mix(in oklab, var(--color-go) 40%, transparent)" } : undefined}
            >
              {humanGoal(g)}
              {g === "joint_longevity" && <span className="ml-1.5 text-xs text-faint">· binding</span>}
            </span>
          ))}
        </div>
      </div>

      <div className="card p-5">
        <p className="eyebrow text-faint">Constraints</p>
        <dl className="mt-3 space-y-3">
          <div className="flex items-center justify-between">
            <dt className="text-muted">Rest days</dt>
            <dd className="font-medium">{restDays.map(titleCase).join(", ") || "—"}</dd>
          </div>
          <div className="flex items-center justify-between border-t border-line pt-3">
            <dt className="text-muted">Strength cap</dt>
            <dd className="tnum font-mono">{strengthCap != null ? `${strengthCap} min` : "—"}</dd>
          </div>
        </dl>
      </div>

      {/* Weekly routine overview */}
      <div className="card p-5">
        <p className="eyebrow text-faint">This week's routine</p>
        {routine.isLoading ? (
          <Skeleton className="mt-3 h-40 w-full" />
        ) : (
          <ul className="mt-3 divide-y divide-line">
            {routine.data?.days.map((d) => (
              <li key={d.day_of_week} className="flex items-center justify-between py-2.5">
                <span className="flex items-center gap-3">
                  <span className="eyebrow w-9 text-faint">{titleCase(d.day_of_week).slice(0, 3)}</span>
                  <span className={d.session_type === "rest" ? "text-faint" : "font-medium"}>
                    {d.label ?? titleCase(d.session_type)}
                  </span>
                </span>
                <span className="flex items-center gap-3">
                  {d.duration_minutes != null && <span className="tnum text-sm text-faint">{d.duration_minutes}m</span>}
                  <TypeBadge type={d.session_type} />
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>

      <p className="px-1 text-xs text-faint">
        Goals & routine are tuned by Eva. Last updated by <span className="text-muted">{titleCase(updatedBy)}</span> on {updatedAt}.
      </p>
    </div>
  );
}
