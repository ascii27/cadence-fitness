import {
  useQuery,
  useMutation,
  useQueryClient,
  type UseQueryResult,
} from "@tanstack/react-query";
import { api, UnauthorizedError } from "./api";
import * as queue from "./offlineQueue";
import type {
  Adherence,
  CatalogExercise,
  Goals,
  LogCreate,
  LogSaveResult,
  Readiness,
  Routine,
  SessionLog,
  TodayResponse,
} from "./types";

export interface Me {
  email: string;
}

export function useMe(): UseQueryResult<Me | null> {
  return useQuery({
    queryKey: ["me"],
    queryFn: async () => {
      try {
        return await api.get<Me>("/api/auth/me");
      } catch (e) {
        if (e instanceof UnauthorizedError) return null;
        throw e;
      }
    },
    retry: false,
    staleTime: 60_000,
  });
}

export function useToday() {
  return useQuery({ queryKey: ["today"], queryFn: () => api.get<TodayResponse>("/api/sessions/today") });
}

export function useDay(dateIso: string, todayIso: string) {
  // The current day shares the ["today"] cache key so logging/readiness updates it directly.
  const isToday = dateIso === todayIso;
  return useQuery({
    queryKey: isToday ? ["today"] : ["day", dateIso],
    queryFn: () =>
      api.get<TodayResponse>(isToday ? "/api/sessions/today" : `/api/sessions/day/${dateIso}`),
  });
}

export function useRoutine() {
  return useQuery({ queryKey: ["routine"], queryFn: () => api.get<Routine>("/api/routine/current") });
}

export function useGoals() {
  return useQuery({ queryKey: ["goals"], queryFn: () => api.get<Goals>("/api/goals") });
}

export function useExercises() {
  return useQuery({
    queryKey: ["exercises"],
    queryFn: () => api.get<CatalogExercise[]>("/api/exercises"),
    staleTime: 60 * 60 * 1000, // catalog is effectively static
  });
}

export function useAdherence() {
  return useQuery({ queryKey: ["adherence"], queryFn: () => api.get<Adherence>("/api/adherence") });
}

export function useHistory(sessionType?: string, limit = 200) {
  return useQuery({
    queryKey: ["history", sessionType ?? "all", limit],
    queryFn: () => {
      const params = new URLSearchParams({ limit: String(limit) });
      if (sessionType) params.set("session_type", sessionType);
      return api.get<SessionLog[]>(`/api/sessions?${params.toString()}`);
    },
  });
}

function isNetworkError(e: unknown): boolean {
  return e instanceof TypeError || (typeof navigator !== "undefined" && !navigator.onLine);
}

export function useReadiness() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (readiness: Readiness) =>
      api.post<TodayResponse>("/api/sessions/readiness", { readiness }),
    onSuccess: (data) => {
      qc.setQueryData(["today"], data);
    },
  });
}

export function useLogWorkout() {
  const qc = useQueryClient();
  return useMutation<LogSaveResult | { queued: true }, Error, LogCreate>({
    mutationFn: async (body: LogCreate) => {
      try {
        return await api.post<LogSaveResult>("/api/sessions/log", body);
      } catch (e) {
        if (isNetworkError(e)) {
          await queue.enqueue({ kind: "create", payload: body });
          return { queued: true };
        }
        throw e;
      }
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["today"] });
      qc.invalidateQueries({ queryKey: ["history"] });
      qc.invalidateQueries({ queryKey: ["adherence"] });
    },
  });
}

export function useEditLog() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ logId, body }: { logId: string; body: Partial<SessionLog> }) => {
      try {
        return await api.patch<SessionLog>(`/api/sessions/${logId}`, body);
      } catch (e) {
        if (isNetworkError(e)) {
          await queue.enqueue({ kind: "patch", log_id: logId, payload: body });
          return null;
        }
        throw e;
      }
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["history"] });
      qc.invalidateQueries({ queryKey: ["today"] });
    },
  });
}

export function useAcknowledgeRoutine() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => api.post<Routine>("/api/routine/acknowledge"),
    onSuccess: (data) => qc.setQueryData(["routine"], data),
  });
}

export function useRevertRoutine() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => api.post<Routine>("/api/routine/revert"),
    onSuccess: (data) => {
      qc.setQueryData(["routine"], data);
      qc.invalidateQueries({ queryKey: ["today"] });
    },
  });
}

/** Send one queued log item to the backend. */
export async function sendQueued(item: queue.QueuedLog): Promise<void> {
  if (item.kind === "create") {
    await api.post("/api/sessions/log", item.payload);
  } else {
    await api.patch(`/api/sessions/${item.log_id}`, item.payload);
  }
}
