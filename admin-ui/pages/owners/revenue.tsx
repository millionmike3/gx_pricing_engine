"use client";

import React, { useEffect, useState } from "react";
import { api } from "../../services/api";

interface RevenueSummary {
  period_days: number;
  total_quote_requests: number;
  successful_events: number;
  failed_events: number;
  estimated_revenue_available: boolean;
  estimated_margin_available: boolean;
  revenue_note: string;
}

function formatCount(value: number | undefined): string {
  return Number(value ?? 0).toLocaleString();
}

export default function OwnerRevenueDashboardPage() {
  const [data, setData] = useState<RevenueSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    const fetchData = async () => {
      try {
        const res = await api.get("/owners/revenue/summary");

        if (active) {
          setData(res.data as RevenueSummary);
          setError(null);
        }
      } catch {
        if (active) {
          setError(
            "Unable to load pricing activity. Please verify your access and try again."
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
        Loading owner pricing activity...
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen bg-[#050505] p-6 text-white">
        <h1 className="mb-3 text-2xl font-bold">
          Owner Pricing Activity
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

  return (
    <div className="min-h-screen bg-[#050505] p-6 text-white">
      <div className="mb-6">
        <h1 className="text-2xl font-bold">
          Owner Pricing Activity
        </h1>
        <p className="mt-2 text-sm text-gray-400">
          Pricing-engine quote activity over the last{" "}
          {formatCount(data.period_days)} days.
        </p>
      </div>

      <div className="mb-6 grid grid-cols-1 gap-4 md:grid-cols-3">
        <div className="rounded-lg border border-white/10 bg-black p-4">
          <div className="text-sm text-gray-400">
            Quote Requests
          </div>
          <div className="mt-2 text-2xl font-semibold">
            {formatCount(data.total_quote_requests)}
          </div>
        </div>

        <div className="rounded-lg border border-white/10 bg-black p-4">
          <div className="text-sm text-gray-400">
            Successful Events
          </div>
          <div className="mt-2 text-2xl font-semibold text-green-400">
            {formatCount(data.successful_events)}
          </div>
        </div>

        <div className="rounded-lg border border-white/10 bg-black p-4">
          <div className="text-sm text-gray-400">
            Failed Events
          </div>
          <div className="mt-2 text-2xl font-semibold text-red-400">
            {formatCount(data.failed_events)}
          </div>
        </div>
      </div>

      <div className="mb-6 rounded-lg border border-white/10 bg-black p-5">
        <h2 className="mb-4 text-lg font-semibold">
          Revenue and Margin Reporting
        </h2>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div>
            <div className="text-sm text-gray-400">
              Realized Revenue
            </div>
            <div className="mt-1 text-xl font-semibold text-gray-300">
              {data.estimated_revenue_available
                ? "Available"
                : "Not available"}
            </div>
          </div>

          <div>
            <div className="text-sm text-gray-400">
              Pricing Margin
            </div>
            <div className="mt-1 text-xl font-semibold text-gray-300">
              {data.estimated_margin_available
                ? "Available"
                : "Not available"}
            </div>
          </div>
        </div>

        <p className="mt-4 border-t border-white/10 pt-4 text-sm text-gray-400">
          {data.revenue_note}
        </p>
      </div>

      <div className="rounded-lg border border-white/10 bg-white/5 p-4">
        <h2 className="mb-2 font-semibold">
          Reporting Scope
        </h2>
        <p className="text-sm leading-6 text-gray-400">
          This dashboard reports recorded pricing-engine activity,
          including quote requests and operational outcomes. It does
          not represent funded loans, collected fees, realized revenue,
          or verified profit and loss.
        </p>
      </div>
    </div>
  );
}