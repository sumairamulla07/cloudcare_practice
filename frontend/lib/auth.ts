// ---------------------------------------------------------------------------
// REAL AUTHENTICATION HELPERS
// ---------------------------------------------------------------------------

const STORAGE_KEY = "cloudcare_demo_session";
const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export interface DemoSession {
  userId: string;
  loggedInAt: string;
}

export function saveSession(userId: string): DemoSession {
  const session: DemoSession = {
    userId: userId.trim() || "Demo User",
    loggedInAt: new Date().toISOString(),
  };
  if (typeof window !== "undefined") {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
  }
  return session;
}

export async function realLogout() {
  try {
    await fetch(`${BASE_URL}/v1/auth/logout`, {
      method: "POST",
      credentials: "include",
    });
  } catch (err) {
    console.error("Failed to execute backend logout:", err);
  }
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

// Keep the old exports so that existing dashboard components don't break
export const demoLogin = saveSession;
export const demoLogout = realLogout;
