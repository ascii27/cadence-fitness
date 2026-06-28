import StreakMeter from "./StreakMeter";

interface Props {
  streak: number;
  dateLabel: string;
  label: string | null;
}

export default function RestCard({ streak, dateLabel, label }: Props) {
  return (
    <div className="card relative overflow-hidden p-6">
      <div className="flex items-center justify-between">
        <span className="eyebrow text-faint">{dateLabel}</span>
        <span className="eyebrow text-faint">Recovery</span>
      </div>
      <h1 className="mt-3 font-display text-3xl font-semibold">{label ?? "Rest Day"}</h1>
      <p className="mt-2 text-muted">No session planned. Recovery is training — protect the joints.</p>
      <div className="mt-7 border-t border-line pt-5">
        <StreakMeter streak={streak} />
      </div>
    </div>
  );
}
