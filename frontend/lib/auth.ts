// ---------------------------------------------------------------------------
// DEMO AUTH — NOT REAL AUTHENTICATION
// ---------------------------------------------------------------------------
// This accepts any userId/password and stores a flag in localStorage so the
// dashboard route can check "is someone logged in" client-side.
//
// PLACEHOLDER: replace this whole file with real auth once the backend is
// ready. Suggested path:
//   1. POST /api/auth/login (FastAPI) -> verifies against MongoDB users
//      collection, returns a JWT.
//   2. Store the JWT in an httpOnly cookie (set by the backend response),
//      not localStorage — localStorage is not secure against XSS.
//   3. Use Next.js middleware (middleware.ts) to protect /dashboard/* routes
//      server-side instead of the client-side check used here.
// ---------------------------------------------------------------------------

const STORAGE_KEY = "cloudcare_demo_session";

export interface DemoSession {
  userId: string;
  loggedInAt: string;
}

export function demoLogin(userId: string): DemoSession {
  const session: DemoSession = {
    userId: userId.trim() || "Demo User",
    loggedInAt: new Date().toISOString(),
  };
  if (typeof window !== "undefined") {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
  }
  return session;
}

export function demoLogout() {
  if (typeof window !== "undefined") {
    window.localStorage.removeItem(STORAGE_KEY);
  }
}

export function getDemoSession(): DemoSession | null {
  if (typeof window === "undefined") return null;
  const raw = window.localStorage.getItem(STORAGE_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as DemoSession;
  } catch {
    return null;
  }
}
