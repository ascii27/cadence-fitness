import { useEffect, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import * as queue from "./offlineQueue";
import { sendQueued } from "./queries";

/** Tracks connectivity, pending-queue size, and drains the queue on reconnect. */
export function useOfflineSync() {
  const qc = useQueryClient();
  const [online, setOnline] = useState(typeof navigator !== "undefined" ? navigator.onLine : true);
  const [pending, setPending] = useState(0);

  useEffect(() => {
    let cancelled = false;

    async function refresh() {
      const n = await queue.count();
      if (!cancelled) setPending(n);
    }

    async function drain() {
      const before = await queue.count();
      if (before === 0) return;
      const result = await queue.flush(sendQueued);
      if (result.sent > 0) {
        qc.invalidateQueries({ queryKey: ["today"] });
        qc.invalidateQueries({ queryKey: ["history"] });
        qc.invalidateQueries({ queryKey: ["adherence"] });
      }
      await refresh();
    }

    function goOnline() {
      setOnline(true);
      void drain();
    }
    function goOffline() {
      setOnline(false);
      void refresh();
    }

    window.addEventListener("online", goOnline);
    window.addEventListener("offline", goOffline);
    void refresh();
    void drain();
    const interval = window.setInterval(() => {
      void refresh();
      if (navigator.onLine) void drain();
    }, 30_000);

    return () => {
      cancelled = true;
      window.removeEventListener("online", goOnline);
      window.removeEventListener("offline", goOffline);
      window.clearInterval(interval);
    };
  }, [qc]);

  return { online, pending };
}
