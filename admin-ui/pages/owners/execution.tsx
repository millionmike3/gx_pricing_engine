"use client";

import React, { useEffect, useState } from "react";
import { api } from "../../services/api";

interface ModuleActivity {
  module: string;
  event_count: number;
}

interface ExecutionDashboardSummary {
  period_days: number;
  total_events: number;
  successful_events: number;
  failed_events: number;
  quote_requests: number;
  matrix_events: number;
  average_duration_ms: number | null;
  p95_duration_ms: number | null;
  by_module: ModuleActivity[];
  performance_note: string;
}

function formatDuration(value: number | null): string {
  return value === null || value === undefined
    ? "Not available"
    : `${value.toLocaleString()} ms`;
}

export default function OwnerExecutionDashboardPage() {
  const [data, setData] = useState<ExecutionDashboardSummary | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .get("/owners/execution/summary")
      .then((res) => setData(res.data))
      .catch(() => {
        setError("Pricing performance data is currently unavailable.");
      });
  }, []);

  if (error) {
    return (
      <div className="min-h-screen bg-[#050505] p-6 text-white">
        <h1 className="mb-3 text-2xl font-bold">
          Pricing API &amp; System Performance
        </h1>
        <p className="text-red-300">{error}</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-screen bg-[#050505] p-6 text-white">
        Loading pricing performance...
      </div>
    );
  }

  const metrics = [
    { label: "Total Recorded Events", value: data.total_events },
    { label: "Successful Events", value: data.successful_events },
    { label: "Failed Events", value: data.failed_events },
    { label: "Quote Requests", value: data.quote_requests },
    { label: "Pricing Matrix Events", value: data.matrix_events },
    {
      label: "Average Operation Duration",
      value: formatDuration(data.average_duration_ms),
    },
    {
      label: "95th-Percentile Duration",
      value: formatDuration(data.p95_duration_ms),
    },
  ];

  return (
    <div className="min-h-screen bg-[#050505] p-6 text-white">
      <h1 className="mb-2 text-2xl font-bold">
        Pricing API &amp; System Performance
      </h1>

      <p className="mb-6 text-sm text-gray-400">
        Recorded pricing-engine operations · Last {data.period_days} days
      </p>

      <div className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {metrics.map((metric) => (
          <div
            key={metric.label}
            className="rounded-lg border border-white/10 bg-black p-4"
          >
            <div className="text-sm text-gray-400">{metric.label}</div>
            <div className="mt-2 text-2xl font-semibold">
              {typeof metric.value === "number"
                ? metric.value.toLocaleString()
                : metric.value}
            </div>
          </div>
        ))}
      </div>

      <h2 className="mb-3 text-xl font-semibold">Activity by Module</h2>

      <div className="overflow-x-auto rounded-lg border border-white/10 bg-black">
        <table className="w-full text-sm">
          <thead className="bg-white/5">
            <tr>
              <th className="px-4 py-3 text-left">Module</th>
              <th className="px-4 py-3 text-right">Recorded Events</th>
            </tr>
          </thead>
          <tbody>
            {data.by_module.length === 0 ? (
              <tr>
                <td colSpan={2} className="px-4 py-5 text-center text-gray-400">
                  No module activity is available for this period.
                </td>
              </tr>
            ) : (
              data.by_module.map((item) => (
                <tr key={item.module} className="border-t border-white/10">
                  <td className="px-4 py-3">{item.module}</td>
                  <td className="px-4 py-3 text-right">
                    {item.event_count.toLocaleString()}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <div className="mt-6 rounded-lg border border-white/10 bg-black p-4">
        <h2 className="mb-2 font-semibold">Measurement scope</h2>
        <p className="text-sm text-gray-400">
          {data.performance_note}
        </p>
        <p className="mt-2 text-sm text-gray-400">
          These metrics describe recorded pricing-engine activity. They do not
          represent funded loans, secondary-market trades, investor execution,
          realized revenue, or profit and loss.
        </p>
      </div>
    </div>
  );
}
