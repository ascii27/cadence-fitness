import type { Readiness } from "../lib/types";

interface Props {
  onAnswer: (r: Readiness) => void;
  pending?: boolean;
}

const OPTIONS: { value: Readiness; label: string; hint: string; color: string }[] = [
  { value: "great", label: "Great", hint: "Full send", color: "var(--color-go)" },
  { value: "tired", label: "Tired but OK", hint: "Proceed", color: "var(--color-amber)" },
  { value: "joint_pain", label: "Joint pain", hint: "Swap to mobility", color: "var(--color-rose)" },
];

export default function ReadinessCheck({ onAnswer, pending }: Props) {
  return (
    <div className="card p-5">
      <p className="eyebrow text-faint">Readiness</p>
      <h3 className="mt-1 text-lg">How are you feeling?</h3>
      <div className="mt-4 grid gap-2.5">
        {OPTIONS.map((o) => (
          <button
            key={o.value}
            disabled={pending}
            onClick={() => onAnswer(o.value)}
            className="group flex min-h-[52px] items-center justify-between rounded-xl border border-line bg-surface-2 px-4 text-left transition-all hover:border-line-bright active:scale-[0.99] disabled:opacity-50"
          >
            <span className="flex items-center gap-3">
              <span className="h-2.5 w-2.5 rounded-full" style={{ background: o.color }} />
              <span className="font-medium">{o.label}</span>
            </span>
            <span className="eyebrow text-faint transition-colors group-hover:text-muted">{o.hint}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
