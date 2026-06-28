import type { Status } from "./types";

export function titleCase(s: string): string {
  return s.replace(/(^|[_\s])(\w)/g, (_, sep, c) => (sep ? " " : "") + c.toUpperCase()).trim();
}

export function humanGoal(slug: string): string {
  return titleCase(slug.replace(/_/g, " "));
}

export const STATUS_COLOR: Record<Status, string> = {
  completed: "var(--color-go)",
  partial: "var(--color-amber)",
  missed: "var(--color-rose)",
  swapped: "var(--color-sky)",
};

export function todayISO(): string {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(
    d.getDate(),
  ).padStart(2, "0")}`;
}

export function shortDate(iso: string): string {
  const [y, m, d] = iso.split("-").map(Number);
  const date = new Date(y, m - 1, d);
  return date.toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

export function weekdayLong(iso: string): string {
  const [y, m, d] = iso.split("-").map(Number);
  return new Date(y, m - 1, d).toLocaleDateString(undefined, { weekday: "long" });
}

function localDate(iso: string): Date {
  const [y, m, d] = iso.split("-").map(Number);
  return new Date(y, m - 1, d);
}

export function isoAddDays(iso: string, n: number): string {
  const d = localDate(iso);
  d.setDate(d.getDate() + n);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

export function dayDiffFromToday(iso: string): number {
  const a = localDate(iso).getTime();
  const b = localDate(todayISO()).getTime();
  return Math.round((a - b) / (24 * 60 * 60 * 1000));
}

/** "Today" / "Tomorrow" / "Yesterday", else the weekday name. */
export function relativeDayWord(iso: string): string {
  const diff = dayDiffFromToday(iso);
  if (diff === 0) return "Today";
  if (diff === 1) return "Tomorrow";
  if (diff === -1) return "Yesterday";
  return weekdayLong(iso);
}

export function withinEditWindow(loggedAt: string): boolean {
  const ts = new Date(loggedAt.endsWith("Z") ? loggedAt : loggedAt + "Z").getTime();
  return Date.now() - ts <= 24 * 60 * 60 * 1000;
}
