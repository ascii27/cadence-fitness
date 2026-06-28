import { useState } from "react";
import { useRoutine, useDay, useReadiness } from "../lib/queries";
import { weekdayLong, todayISO } from "../lib/format";
import SessionCard from "../components/SessionCard";
import RestCard from "../components/RestCard";
import ReadinessCheck from "../components/ReadinessCheck";
import EvaUpdateBanner from "../components/EvaUpdateBanner";
import StreakMeter from "../components/StreakMeter";
import DayNav from "../components/DayNav";
import Skeleton from "../components/Skeleton";

export default function TodayPage() {
  const [date, setDate] = useState(todayISO());
  const today = useDay(date, todayISO());
  const routine = useRoutine();
  const readiness = useReadiness();
  const [dismissed, setDismissed] = useState(false);

  return (
    <div className="space-y-4 stagger">
      {routine.data?.eva_update_pending && <EvaUpdateBanner reason={routine.data.reason} />}

      <DayNav dateIso={date} onChange={setDate} />

      {today.isLoading || !today.data ? (
        <Skeleton className="h-80 w-full" />
      ) : (
        <DayBody
          data={today.data}
          dismissed={dismissed}
          onDismiss={() => setDismissed(true)}
          onReadiness={(r) => readiness.mutate(r)}
          readinessPending={readiness.isPending}
        />
      )}

      {today.isError && (
        <p className="text-rose">Couldn't load this day's plan. Check your connection.</p>
      )}
    </div>
  );
}

function DayBody({
  data,
  dismissed,
  onDismiss,
  onReadiness,
  readinessPending,
}: {
  data: import("../lib/types").TodayResponse;
  dismissed: boolean;
  onDismiss: () => void;
  onReadiness: (r: import("../lib/types").Readiness) => void;
  readinessPending: boolean;
}) {
  const { session, log, readiness_answered, streak, relativity, session_date } = data;
  const isToday = relativity === "today";
  const dateLabel = weekdayLong(session_date);
  const showReadiness = isToday && !session.is_rest && !readiness_answered && !dismissed;
  const logHref = isToday ? "/log" : `/log?date=${session_date}`;

  return (
    <div className="space-y-4">
      {isToday && !session.is_rest && (
        <div className="flex items-center justify-between px-1">
          <p className="eyebrow text-faint">Today's plan</p>
          <StreakMeter streak={streak} />
        </div>
      )}

      {showReadiness && (
        <div className="relative">
          <ReadinessCheck onAnswer={onReadiness} pending={readinessPending} />
          <button onClick={onDismiss} className="eyebrow absolute right-5 top-5 text-faint hover:text-muted">
            Skip
          </button>
        </div>
      )}

      {session.is_rest ? (
        <RestCard streak={streak} dateLabel={dateLabel} label={session.label} showStreak={isToday} />
      ) : (
        <SessionCard session={session} log={log} dateLabel={dateLabel} relativity={relativity} logHref={logHref} />
      )}
    </div>
  );
}
