"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { demoLogin } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const [userId, setUserId] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // PLACEHOLDER: swap this for a real POST /api/auth/login call once the
    // FastAPI backend + MongoDB users collection are wired up. For now this
    // demo accepts any input (even empty) as a successful login.
    demoLogin(userId);
    router.push("/dashboard");
  };

  return (
    <main className="min-h-screen flex items-center justify-center bg-bg px-6">
      <div className="w-full max-w-sm">
        <Link href="/" className="flex items-center justify-center gap-2.5 font-display font-bold text-xl text-ink mb-8">
          <span className="w-8 h-8 rounded-[10px] bg-gradient-to-br from-brandBlue to-brandTeal inline-block" />
          CloudCare
        </Link>

        <div className="bg-surface border border-line rounded-lg2 shadow-soft p-8">
          <h1 className="font-display text-xl font-semibold text-ink mb-1">Welcome back</h1>
          <p className="text-sm text-inkSoft mb-6">Log in to view your cloud cost dashboard.</p>

          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
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
            <button
              type="submit"
              className="mt-2 inline-flex items-center justify-center rounded-full bg-ink px-6 py-3 text-sm font-semibold text-white hover:-translate-y-0.5 hover:shadow-[0_10px_20px_-8px_rgba(16,34,46,0.4)] transition-all"
            >
              Log in
            </button>
          </form>

          <p className="text-center text-[12.5px] text-inkFaint mt-5">
            Demo mode — enter any User ID and Password to continue.
          </p>
        </div>

        <p className="text-center text-[13px] text-inkFaint mt-6">
          <Link href="/" className="hover:text-brandBlue transition-colors">
            ← Back to home
          </Link>
        </p>
      </div>
    </main>
  );
}
