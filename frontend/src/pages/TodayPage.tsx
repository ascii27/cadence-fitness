import { useState } from "react";
import { useRoutine, useToday, useReadiness } from "../lib/queries";
import { weekdayLong, todayISO } from "../lib/format";
import SessionCard from "../components/SessionCard";
import RestCard from "../components/RestCard";
import ReadinessCheck from "../components/ReadinessCheck";
import EvaUpdateBanner from "../components/EvaUpdateBanner";
import StreakMeter from "../components/StreakMeter";
import Skeleton from "../components/Skeleton";

export default function TodayPage() {
  const today = useToday();
  const routine = useRoutine();
  const readiness = useReadiness();
  const [dismissed, setDismissed] = useState(false);

  if (today.isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-10 w-40" />
        <Skeleton className="h-80 w-full" />
      </div>
    );
  }
  if (today.isError || !today.data) {
    return <p className="text-rose">Couldn't load today's plan. Check your connection.</p>;
  }

  const { session, log, readiness_answered, streak, session_date } = today.data;
  const dateLabel = weekdayLong(session_date || todayISO());
  const showReadiness = !session.is_rest && !readiness_answered && !dismissed;

  return (
    <div className="space-y-4 stagger">
      {routine.data?.eva_update_pending && <EvaUpdateBanner reason={routine.data.reason} />}

      {!session.is_rest && (
        <div className="flex items-center justify-between px-1">
          <p className="eyebrow text-faint">Today's plan</p>
          <StreakMeter streak={streak} />
        </div>
      )}

      {showReadiness && (
        <div className="relative">
          <ReadinessCheck onAnswer={(r) => readiness.mutate(r)} pending={readiness.isPending} />
          <button
            onClick={() => setDismissed(true)}
            className="eyebrow absolute right-5 top-5 text-faint hover:text-muted"
          >
            Skip
          </button>
        </div>
      )}

      {session.is_rest ? (
        <RestCard streak={streak} dateLabel={dateLabel} label={session.label} />
      ) : (
        <SessionCard session={session} log={log} dateLabel={dateLabel} />
      )}
    </div>
  );
}
