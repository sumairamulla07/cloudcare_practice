// ---------------------------------------------------------------------------
// REAL AUTH — stores the JWT returned by /v1/auth/login
// ---------------------------------------------------------------------------
// NOTE: localStorage is used here for demo speed. The blueprint's real
// recommendation is an httpOnly cookie set by the backend, checked via
// Next.js middleware — flagged as a post-hackathon hardening task, not a
// blocker for the demo.
// ---------------------------------------------------------------------------

const STORAGE_KEY = "cloudcare_session";

export interface Session {
  accessToken: string;
  userId: string;
  tenantId: string;
  loggedInAt: string;
}

export function saveSession(s: Omit<Session, "loggedInAt">): Session {
  const session: Session = { ...s, loggedInAt: new Date().toISOString() };
  if (typeof window !== "undefined") {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
  }
  return session;
}

export function logout() {
  if (typeof window !== "undefined") {
    window.localStorage.removeItem(STORAGE_KEY);
  }
}

export function getSession(): Session | null {
  if (typeof window === "undefined") return null;
  const raw = window.localStorage.getItem(STORAGE_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as Session;
  } catch {
    return null;
  }
}