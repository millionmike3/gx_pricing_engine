"use client";

import React, { useEffect, useState } from "react";
import { api } from "../../services/api";

interface ControlAction {
  action: string;
  event_count: number;
}

interface FraudDashboardSummary {
  period_days: number;
  control_events: number;
  observed_control_actions: ControlAction[];
  fraud_scores_available: boolean;
  note: string;
}

function formatCount(value: number | undefined): string {
  return Number(value ?? 0).toLocaleString();
}

const actionLabels: Record<string, string> = {
  QUOTE_VALIDATION_FAILED: "Quote validation failures",
  QUOTE_REJECTED: "Rejected quote requests",
  MATRIX_VALIDATION_FAILED: "Pricing matrix validation failures",
};

export default function OwnerFraudDashboardPage() {
  const [data, setData] = useState<FraudDashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    const fetchData = async () => {
      try {
        const res = await api.get("/owners/fraud/summary");

        if (active) {
          setData(res.data as FraudDashboardSummary);
          setError(null);
        }
      } catch {
        if (active) {
          setError(
            "Unable to load pricing-control activity. Verify your access and activity database availability."
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
        Loading pricing-control activity...
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen bg-[#050505] p-6 text-white">
        <h1 className="mb-3 text-2xl font-bold">
          Pricing Controls & Risk Signals
        </h1>
        <div
          role="alert"
          className="rounded-lg border border-red-500/30 bg-red-500/10 p-4 text-red-200"
        >
          {error || "Pricing-control data is unavailable."}
        </div>
      </div>
    );
  }

  const actions = Array.isArray(data.observed_control_actions)
    ? data.observed_control_actions
    : [];

  return (
    <div className="min-h-screen bg-[#050505] p-6 text-white">
      <div className="mb-6">
        <h1 className="text-2xl font-bold">
          Pricing Controls & Risk Signals
        </h1>
        <p className="mt-2 text-sm text-gray-400">
          Recorded pricing-engine validation and control events over the
          last {formatCount(data.period_days)} days.
        </p>
      </div>

      <div className="mb-6 grid grid-cols-1 gap-4 md:grid-cols-2">
        <div className="rounded-lg border border-white/10 bg-black p-5">
          <div className="text-sm text-gray-400">
            Recorded Control Events
          </div>
          <div className="mt-2 text-3xl font-semibold">
            {formatCount(data.control_events)}
          </div>
        </div>

        <div className="rounded-lg border border-white/10 bg-black p-5">
          <div className="text-sm text-gray-400">
            Fraud Scores
          </div>
          <div className="mt-2 text-xl font-semibold text-gray-300">
            {data.fraud_scores_available
              ? "Available"
              : "Not available"}
          </div>
        </div>
      </div>

      <div className="mb-6 rounded-lg border border-white/10 bg-black p-5">
        <h2 className="mb-4 text-lg font-semibold">
          Observed Pricing-Control Events
        </h2>

        {actions.length === 0 ? (
          <p className="text-sm text-gray-400">
            No recorded control events were returned for this reporting
            period. This does not establish that no validation issues
            occurred.
          </p>
        ) : (
          <div className="space-y-3">
            {actions.map((item) => (
              <div
                key={item.action}
                className="flex flex-col justify-between gap-2 border-b border-white/10 pb-3 sm:flex-row sm:items-center"
              >
                <div>
                  <div className="font-medium">
                    {actionLabels[item.action] || item.action}
                  </div>
                  <div className="mt-1 text-xs text-gray-500">
                    {item.action}
                  </div>
                </div>

                <div className="text-lg font-semibold tabular-nums">
                  {formatCount(item.event_count)}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="rounded-lg border border-white/10 bg-white/5 p-4">
        <h2 className="mb-2 font-semibold">
          Reporting Scope & Limitations
        </h2>
        <p className="text-sm leading-6 text-gray-400">
          {data.note}
        </p>
        <p className="mt-3 text-sm leading-6 text-gray-400">
          This dashboard reports recorded pricing-engine control events.
          It does not independently determine fraud, assign borrower risk
          scores, or establish fraudulent intent.
        </p>
      </div>
    </div>
  );
}
