interface Props {
  online: boolean;
  pending: number;
}

export default function OfflineIndicator({ online, pending }: Props) {
  if (online && pending === 0) {
    return (
      <span className="flex items-center gap-1.5 text-faint" title="Connected">
        <span className="h-1.5 w-1.5 rounded-full bg-go" />
      </span>
    );
  }

  return (
    <span
      className="flex items-center gap-1.5 rounded-full border border-line bg-surface-2 px-2.5 py-1 text-xs"
      title={online ? "Syncing queued logs" : "Offline — logs are saved locally"}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${online ? "bg-amber" : "bg-rose"}`} />
      <span className="text-muted">
        {online ? "Syncing" : "Offline"}
        {pending > 0 && <span className="tnum text-faint"> · {pending}</span>}
      </span>
    </span>
  );
}
