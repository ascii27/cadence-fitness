import { NavLink, Route, Routes } from "react-router-dom";
import { useMe } from "./lib/queries";
import { useOfflineSync } from "./lib/useOfflineSync";
import SignIn from "./components/SignIn";
import OfflineIndicator from "./components/OfflineIndicator";
import TodayPage from "./pages/TodayPage";
import LogPage from "./pages/LogPage";
import HistoryPage from "./pages/HistoryPage";
import GoalsPage from "./pages/GoalsPage";
import SettingsPage from "./pages/SettingsPage";

const NAV = [
  { to: "/", label: "Today", end: true },
  { to: "/history", label: "History", end: false },
  { to: "/goals", label: "Goals", end: false },
];

export default function App() {
  const me = useMe();
  const { online, pending } = useOfflineSync();

  if (me.isLoading) {
    return (
      <div className="grid min-h-dvh place-items-center">
        <span className="eyebrow text-faint animate-pulse">Cadence</span>
      </div>
    );
  }

  if (!me.data) return <SignIn />;

  return (
    <div className="relative z-10 mx-auto flex min-h-dvh max-w-xl flex-col px-5 pb-28 pt-6">
      <header className="mb-6 flex items-center justify-between">
        <NavLink to="/" className="flex items-baseline gap-2">
          <span className="font-display text-2xl font-semibold tracking-tight text-text">
            Cadence
          </span>
          <span className="h-2 w-2 rounded-full bg-ember" style={{ animation: "pulse-ring 2.4s infinite" }} />
        </NavLink>
        <div className="flex items-center gap-3">
          <OfflineIndicator online={online} pending={pending} />
          <NavLink to="/settings" className="text-faint transition-colors hover:text-text" aria-label="Settings">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6">
              <circle cx="12" cy="12" r="3" />
              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
            </svg>
          </NavLink>
        </div>
      </header>

      <main className="flex-1">
        <Routes>
          <Route path="/" element={<TodayPage />} />
          <Route path="/log" element={<LogPage />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/goals" element={<GoalsPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Routes>
      </main>

      <nav className="fixed inset-x-0 bottom-0 z-20 border-t border-line bg-ink/85 backdrop-blur-md">
        <div className="mx-auto flex max-w-xl items-stretch justify-around px-2">
          {NAV.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `flex min-h-[60px] flex-1 flex-col items-center justify-center gap-1 text-xs transition-colors ${
                  isActive ? "text-ember" : "text-faint hover:text-muted"
                }`
              }
            >
              {({ isActive }) => (
                <>
                  <span
                    className="h-1 w-6 rounded-full transition-colors"
                    style={{ background: isActive ? "var(--color-ember)" : "transparent" }}
                  />
                  <span className="eyebrow">{item.label}</span>
                </>
              )}
            </NavLink>
          ))}
        </div>
      </nav>
    </div>
  );
}
