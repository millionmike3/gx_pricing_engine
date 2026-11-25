"use client";

import React, { useEffect, useState } from "react";
import { api } from "../../services/api";

interface ActionActivity {
  action: string;
  event_count: number;
}

interface ModuleActivity {
  module: string;
  event_count: number;
}

interface BehaviorDashboardSummary {
  period_days: number;
  total_events: number;
  by_action: ActionActivity[];
  by_module: ModuleActivity[];
}

function formatCount(value: number | undefined): string {
  return Number(value ?? 0).toLocaleString();
}

export default function OwnerBehaviorDashboardPage() {
  const [data, setData] = useState<BehaviorDashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    const fetchData = async () => {
      try {
        const res = await api.get("/owners/behavior/summary");

        if (active) {
          setData(res.data as BehaviorDashboardSummary);
          setError(null);
        }
      } catch {
        if (active) {
          setError(
            "Unable to load pricing-engine activity. Verify your access and activity database availability."
          );
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    };

    fetchData();

    return () => {
      active = false;
    };
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#050505] p-6 text-white">
        Loading pricing-engine activity...
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen bg-[#050505] p-6 text-white">
        <h1 className="mb-3 text-2xl font-bold">
          Pricing Behavior Analytics
        </h1>
        <div
          role="alert"
          className="rounded-lg border border-red-500/30 bg-red-500/10 p-4 text-red-200"
        >
          {error || "Pricing activity data is unavailable."}
        </div>
      </div>
    );
  }

  const actions = Array.isArray(data.by_action) ? data.by_action : [];
  const modules = Array.isArray(data.by_module) ? data.by_module : [];

  return (
    <div className="min-h-screen bg-[#050505] p-6 text-white">
      <div className="mb-6">
        <h1 className="text-2xl font-bold">
          Pricing Behavior Analytics
        </h1>
        <p className="mt-2 text-sm text-gray-400">
          Recorded pricing-engine activity over the last{" "}
          {formatCount(data.period_days)} days.
        </p>
      </div>

      <div className="mb-6 rounded-lg border border-white/10 bg-black p-5">
        <div className="text-sm text-gray-400">
          Total Recorded Events
        </div>
        <div className="mt-2 text-3xl font-semibold tabular-nums">
          {formatCount(data.total_events)}
        </div>
      </div>

      <div className="mb-6 grid grid-cols-1 gap-4 lg:grid-cols-2">
        <section className="rounded-lg border border-white/10 bg-black p-5">
          <h2 className="mb-4 text-lg font-semibold">
            Activity by Action
          </h2>

          {actions.length === 0 ? (
            <p className="text-sm text-gray-400">
              No action activity records were returned for this reporting
              period.
            </p>
          ) : (
            <div className="space-y-3">
              {actions.map((item) => (
                <div
                  key={item.action}
                  className="flex items-center justify-between gap-3 border-b border-white/10 pb-3"
                >
                  <span className="break-all text-sm text-gray-300">
                    {item.action}
                  </span>
                  <span className="shrink-0 text-lg font-semibold tabular-nums">
                    {formatCount(item.event_count)}
                  </span>
                </div>
              ))}
            </div>
          )}
        </section>

        <section className="rounded-lg border border-white/10 bg-black p-5">
          <h2 className="mb-4 text-lg font-semibold">
            Activity by Module
          </h2>

          {modules.length === 0 ? (
            <p className="text-sm text-gray-400">
              No module activity records were returned for this reporting
              period.
            </p>
          ) : (
            <div className="space-y-3">
              {modules.map((item) => (
                <div
                  key={item.module}
                  className="flex items-center justify-between gap-3 border-b border-white/10 pb-3"
                >
                  <span className="break-all text-sm text-gray-300">
                    {item.module}
                  </span>
                  <span className="shrink-0 text-lg font-semibold tabular-nums">
                    {formatCount(item.event_count)}
                  </span>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>

      <div className="rounded-lg border border-white/10 bg-white/5 p-4">
        <h2 className="mb-2 font-semibold">
          Reporting Scope
        </h2>
        <p className="text-sm leading-6 text-gray-400">
          This dashboard summarizes recorded pricing-engine events by
          action and module. It does not measure borrower behavior, loan
          performance, customer risk scores, funded loans, or realized
          revenue.
        </p>
      </div>
    </div>
  );
}
