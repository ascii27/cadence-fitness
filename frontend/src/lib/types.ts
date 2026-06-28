export type SessionType = "run" | "strength" | "mobility" | "rest";
export type Status = "completed" | "partial" | "missed" | "swapped";
export type Readiness = "great" | "tired" | "joint_pain";

export interface Exercise {
  name: string;
  reps: number | null;
  note: string | null;
}

export interface DerivedSession {
  day_of_week: string;
  session_type: SessionType;
  label: string | null;
  modality: string | null;
  duration_minutes: number | null;
  exercises: Exercise[];
  hr_zone: string | null;
  hr_cap_bpm: number | null;
  progression_rule: string | null;
  is_rest: boolean;
  swapped: boolean;
  swap_reason: string | null;
  routine_version: number | null;
}

export interface SessionLog {
  log_id: string;
  logged_at: string;
  session_date: string;
  day_of_week: string;
  session_type: SessionType;
  label: string | null;
  status: Status | null;
  swap_reason: string | null;
  readiness: Readiness | null;
  duration_minutes: number | null;
  rounds_completed: number | null;
  rating: number | null;
  notes: string | null;
  source: string;
  health_metrics: Record<string, number | null>;
  routine_version: number | null;
}

export type Relativity = "past" | "today" | "future";

export interface TodayResponse {
  session_date: string;
  session: DerivedSession;
  log: SessionLog | null;
  readiness_answered: boolean;
  streak: number;
  relativity: Relativity;
}

export interface RoutineDay {
  day_of_week: string;
  session_type: SessionType;
  label: string | null;
  modality?: string | null;
  duration_minutes?: number | null;
  exercises?: Exercise[];
  hr_zone?: string | null;
  hr_cap_bpm?: number | null;
  progression_rule?: string | null;
}

export interface Routine {
  routine_id: string;
  version: number;
  created_at: string;
  source: string;
  reason: string | null;
  days: RoutineDay[];
  is_current: boolean;
  eva_update_pending: boolean;
  eva_applied_at: string | null;
}

export interface Goals {
  goals: string[];
  constraints: Record<string, unknown>;
  updated_at: string;
  updated_by: string;
}

export interface WeeklySummary {
  week_start: string;
  planned: number;
  completed: number;
}

export interface Adherence {
  current_streak: number;
  longest_streak: number;
  weeks: WeeklySummary[];
}

export interface LogCreate {
  status: Status;
  duration_minutes: number;
  session_date?: string;
  session_type?: string;
  label?: string;
  rounds_completed?: number | null;
  rating?: number | null;
  notes?: string | null;
  swap_reason?: string | null;
}

export interface LogSaveResult {
  log: SessionLog;
  streak: number;
  milestone_hit: number | null;
}
