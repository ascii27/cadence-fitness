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

export function withinEditWindow(loggedAt: string): boolean {
  const ts = new Date(loggedAt.endsWith("Z") ? loggedAt : loggedAt + "Z").getTime();
  return Date.now() - ts <= 24 * 60 * 60 * 1000;
}
