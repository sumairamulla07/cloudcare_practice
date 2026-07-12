"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getDemoSession, type DemoSession } from "@/lib/auth";
import Sidebar from "@/components/dashboard/Sidebar";
import DashboardHeader from "@/components/dashboard/DashboardHeader";
import KpiCards from "@/components/dashboard/KpiCards";
import CostTrendChart from "@/components/dashboard/CostTrendChart";
import HealthDonut from "@/components/dashboard/HealthDonut";
import AgentFeed from "@/components/dashboard/AgentFeed";
import ResourceTable from "@/components/dashboard/ResourceTable";
import NextSteps from "@/components/dashboard/NextSteps";

// NOTE: this route is protected client-side only, which is fine for a demo.
// PLACEHOLDER: once real auth exists, protect this route server-side with
// Next.js middleware (middleware.ts) checking a session cookie instead.
export default function DashboardPage() {
  const router = useRouter();
  const [session, setSession] = useState<DemoSession | null>(null);
  const [checked, setChecked] = useState(false);

  useEffect(() => {
    const s = getDemoSession();
    if (!s) {
      router.replace("/login");
      return;
    }
    setSession(s);
    setChecked(true);
  }, [router]);

  if (!checked || !session) {
    return (
      <main className="min-h-screen flex items-center justify-center bg-bg">
        <p className="text-inkFaint text-sm">Loading dashboard…</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-bg flex">
      <Sidebar />
      <div className="flex-1 min-w-0">
        <DashboardHeader userId={session.userId} />
        <div className="p-7 flex flex-col gap-6 max-w-6xl">
          <KpiCards />
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <CostTrendChart />
            <HealthDonut />
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <AgentFeed />
            <ResourceTable />
          </div>
          <NextSteps />
        </div>
      </div>
    </main>
  );
}
