import { useMe } from "../lib/queries";
import { api } from "../lib/api";

export default function SettingsPage() {
  const me = useMe();

  async function logout() {
    await api.post("/api/auth/logout");
    window.location.href = "/";
  }

  return (
    <div className="space-y-6 stagger">
      <h1 className="font-display text-2xl">Settings</h1>

      <div className="card p-5">
        <p className="eyebrow text-faint">Account</p>
        <p className="mt-2 font-medium">{me.data?.email ?? "—"}</p>
        <button
          onClick={logout}
          className="mt-5 min-h-[48px] w-full rounded-full border border-line bg-surface-2 font-medium text-muted transition hover:border-line-bright active:scale-[0.98]"
        >
          Sign out
        </button>
      </div>

      <div className="card p-5">
        <p className="eyebrow text-faint">About</p>
        <p className="mt-2 text-sm text-muted">
          Cadence — Phase 1. Your routine is tuned by <span className="text-text">Eva</span> and progress
          is streamed to <span className="text-text">Jester</span>. Logs are saved locally first and sync
          when you're online.
        </p>
        <p className="mt-3 eyebrow text-faint">v0.1.0</p>
      </div>
    </div>
  );
}
