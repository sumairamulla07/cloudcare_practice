"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { loginUser } from "@/lib/api";
import { saveSession } from "@/lib/auth";

type Step = "password" | "otp" | "biometric";

export default function LoginPage() {
  const router = useRouter();
  const [step, setStep] = useState<Step>("password");
  const [userId, setUserId] = useState("");
  const [password, setPassword] = useState("");
  const [otp, setOtp] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  // Held between steps once step 1 succeeds, used to finish login after OTP + biometric.
  const [pendingToken, setPendingToken] = useState<{ access_token: string; user_id: string; tenant_id: string } | null>(null);

  async function handlePasswordSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const data = await loginUser(userId, password);
      setPendingToken(data);
      setStep("otp");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  }

  async function handleOtpSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    // TODO(Anay): replace with a real call once /v1/auth/otp/verify exists.
    // For now any 6-digit code is accepted so the flow can be demoed end to end.
    if (otp.trim().length !== 6) {
      setError("Enter the 6-digit code");
      return;
    }
    setStep("biometric");
  }

  async function handleBiometricPrompt() {
    setError(null);
    setLoading(true);
    // TODO(Anay): replace with a real @simplewebauthn/browser call once
    // /v1/auth/webauthn/login exists on the backend.
    await new Promise((r) => setTimeout(r, 600)); // fake device prompt delay
    setLoading(false);

    if (!pendingToken) {
      setError("Session expired, please log in again");
      setStep("password");
      return;
    }
    saveSession({
      accessToken: pendingToken.access_token,
      userId: pendingToken.user_id,
      tenantId: pendingToken.tenant_id,
    });
    router.push("/dashboard");
  }

  return (
    <main className="min-h-screen flex items-center justify-center bg-bg px-6">
      <div className="w-full max-w-sm">
        <Link href="/" className="flex items-center justify-center gap-2.5 font-display font-bold text-xl text-ink mb-8">
          <span className="w-8 h-8 rounded-[10px] bg-gradient-to-br from-brandBlue to-brandTeal inline-block" />
          CloudCare
        </Link>

        <div className="bg-surface border border-line rounded-lg2 shadow-soft p-8">
          {/* step indicator */}
          <div className="flex items-center gap-2 mb-6">
            {(["password", "otp", "biometric"] as Step[]).map((s, i) => (
              <div key={s} className={`h-1.5 flex-1 rounded-full ${step === s || (["otp","biometric"].includes(step) && i === 0) || (step === "biometric" && i === 1) ? "bg-brandBlue" : "bg-line"}`} />
            ))}
          </div>

          {step === "password" && (
            <>
              <h1 className="font-display text-xl font-semibold text-ink mb-1">Welcome back</h1>
              <p className="text-sm text-inkSoft mb-6">Step 1 of 3 — password</p>
              <form onSubmit={handlePasswordSubmit} className="flex flex-col gap-4">
                <div>
                  <label className="block text-[12.5px] font-semibold text-inkSoft mb-1.5">User ID</label>
                  <input
                    type="text"
                    value={userId}
                    onChange={(e) => setUserId(e.target.value)}
                    placeholder="demo.user"
                    className="w-full border-[1.5px] border-line rounded-lg px-3.5 py-3 text-[14.5px] bg-bg focus:outline-none focus:border-brandBlue focus:shadow-[0_0_0_4px_rgba(47,102,144,0.12)] transition-all"
                  />
                </div>
                <div>
                  <label className="block text-[12.5px] font-semibold text-inkSoft mb-1.5">Password</label>
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full border-[1.5px] border-line rounded-lg px-3.5 py-3 text-[14.5px] bg-bg focus:outline-none focus:border-brandBlue focus:shadow-[0_0_0_4px_rgba(47,102,144,0.12)] transition-all"
                  />
                </div>
                {error && <p className="text-[12.5px] text-red-600">{error}</p>}
                <button
                  type="submit"
                  disabled={loading}
                  className="mt-2 inline-flex items-center justify-center rounded-full bg-ink px-6 py-3 text-sm font-semibold text-white hover:-translate-y-0.5 hover:shadow-[0_10px_20px_-8px_rgba(16,34,46,0.4)] transition-all disabled:opacity-50"
                >
                  {loading ? "Checking…" : "Continue"}
                </button>
              </form>
            </>
          )}

          {step === "otp" && (
            <>
              <h1 className="font-display text-xl font-semibold text-ink mb-1">Verify it's you</h1>
              <p className="text-sm text-inkSoft mb-6">Step 2 of 3 — enter the 6-digit code sent to your email/phone</p>
              <form onSubmit={handleOtpSubmit} className="flex flex-col gap-4">
                <input
                  type="text"
                  inputMode="numeric"
                  maxLength={6}
                  value={otp}
                  onChange={(e) => setOtp(e.target.value.replace(/\D/g, ""))}
                  placeholder="000000"
                  className="w-full border-[1.5px] border-line rounded-lg px-3.5 py-3 text-[18px] tracking-[0.4em] text-center bg-bg focus:outline-none focus:border-brandBlue"
                />
                {error && <p className="text-[12.5px] text-red-600">{error}</p>}
                <button
                  type="submit"
                  className="mt-2 inline-flex items-center justify-center rounded-full bg-ink px-6 py-3 text-sm font-semibold text-white hover:-translate-y-0.5 transition-all"
                >
                  Verify
                </button>
              </form>
            </>
          )}

          {step === "biometric" && (
            <div className="flex flex-col items-center text-center gap-4">
              <h1 className="font-display text-xl font-semibold text-ink">Confirm with biometrics</h1>
              <p className="text-sm text-inkSoft">Step 3 of 3 — use Face ID / Touch ID / Windows Hello</p>
              <button
                onClick={handleBiometricPrompt}
                disabled={loading}
                className="mt-2 inline-flex items-center justify-center rounded-full bg-ink px-6 py-3 text-sm font-semibold text-white hover:-translate-y-0.5 transition-all disabled:opacity-50"
              >
                {loading ? "Verifying…" : "Scan / Confirm"}
              </button>
              {error && <p className="text-[12.5px] text-red-600">{error}</p>}
            </div>
          )}
        </div>

        <p className="text-center text-[13px] text-inkFaint mt-6">
          <Link href="/" className="hover:text-brandBlue transition-colors">← Back to home</Link>
        </p>
      </div>
    </main>
  );
}