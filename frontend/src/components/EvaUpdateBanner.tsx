import { useAcknowledgeRoutine, useRevertRoutine } from "../lib/queries";

interface Props {
  reason: string | null;
}

export default function EvaUpdateBanner({ reason }: Props) {
  const ack = useAcknowledgeRoutine();
  const revert = useRevertRoutine();
  const busy = ack.isPending || revert.isPending;

  return (
    <div
      className="card overflow-hidden p-0"
      style={{ borderColor: "color-mix(in oklab, var(--color-sky) 40%, var(--color-line))" }}
    >
      <div className="flex items-start gap-3 p-5">
        <span className="mt-0.5 grid h-8 w-8 shrink-0 place-items-center rounded-full" style={{ background: "color-mix(in oklab, var(--color-sky) 18%, transparent)" }}>
          <span className="font-display text-sm font-semibold text-sky">E</span>
        </span>
        <div className="min-w-0 flex-1">
          <p className="eyebrow text-sky">Eva adjusted your routine</p>
          <p className="mt-1 text-sm text-muted">{reason || "Routine updated."}</p>
          <div className="mt-4 flex gap-2.5">
            <button
              disabled={busy}
              onClick={() => ack.mutate()}
              className="min-h-[44px] flex-1 rounded-full bg-text px-4 text-sm font-medium text-ink transition active:scale-[0.98] disabled:opacity-50"
            >
              Keep
            </button>
            <button
              disabled={busy}
              onClick={() => revert.mutate()}
              className="min-h-[44px] flex-1 rounded-full border border-line bg-surface-2 px-4 text-sm font-medium transition hover:border-line-bright active:scale-[0.98] disabled:opacity-50"
            >
              Revert
            </button>
          </div>
          {revert.isError && <p className="mt-2 text-xs text-rose">Revert window has passed.</p>}
        </div>
      </div>
    </div>
  );
}
