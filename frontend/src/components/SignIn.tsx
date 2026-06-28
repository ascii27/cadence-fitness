export default function SignIn() {
  return (
    <div className="relative z-10 grid min-h-dvh place-items-center px-6">
      <div className="w-full max-w-sm text-center stagger">
        <div className="mb-3 flex items-center justify-center gap-2">
          <span className="font-display text-4xl font-semibold tracking-tight">Cadence</span>
          <span className="h-2.5 w-2.5 rounded-full bg-ember" style={{ animation: "pulse-ring 2.4s infinite" }} />
        </div>
        <p className="eyebrow text-faint">Goal-driven training engine</p>

        <div className="card mt-10 p-7">
          <p className="text-muted">
            Your routine, tuned by <span className="text-text">Eva</span>. Log every session, hold the
            <span className="text-go"> streak</span>, protect the joints.
          </p>
          <a
            href="/api/auth/login"
            className="mt-7 flex min-h-[52px] items-center justify-center gap-3 rounded-full bg-text px-6 font-medium text-ink transition-transform active:scale-[0.98]"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" aria-hidden>
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.27-4.74 3.27-8.1z" />
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84A11 11 0 0 0 12 23z" />
              <path fill="#FBBC05" d="M5.84 14.1a6.6 6.6 0 0 1 0-4.2V7.06H2.18a11 11 0 0 0 0 9.88l3.66-2.84z" />
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1A11 11 0 0 0 2.18 7.06l3.66 2.84C6.71 7.3 9.14 5.38 12 5.38z" />
            </svg>
            Sign in with Google
          </a>
          <p className="mt-4 text-xs text-faint">Single-user · access restricted to the owner</p>
        </div>
      </div>
    </div>
  );
}
