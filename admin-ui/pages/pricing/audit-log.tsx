"use client";

import React, { useEffect, useState } from "react";
import { api } from "../../services/api";

interface AuditEvent {
  id: number;
  actor_role: string;
  actor_id: number | null;
  action: string;
  module: string;
  details: unknown;
  status: string;
  duration_ms: number | null;
  created_at: string;
}

function formatDetails(details: unknown): string {
  if (details === null || details === undefined) {
    return "—";
  }

  if (typeof details === "string") {
    return details;
  }

  try {
    return JSON.stringify(details, null, 2) ?? "—";
  } catch {
    return "Details unavailable";
  }
}

function formatTimestamp(value: string): string {
  const timestamp = new Date(value);

  if (Number.isNaN(timestamp.getTime())) {
    return value || "—";
  }

  return timestamp.toLocaleString();
}

export default function PricingAuditLogPage() {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    async function loadEvents() {
      try {
        const response = await api.get<AuditEvent[]>(
          "/pricing/audit-log/recent"
        );

        if (!Array.isArray(response.data)) {
          throw new Error("Unexpected audit log response.");
        }

        if (active) {
          setEvents(response.data);
          setError("");
        }
      } catch {
        if (active) {
          setError(
            "Pricing audit activity is currently unavailable. Please try again later."
          );
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    loadEvents();

    return () => {
      active = false;
    };
  }, []);

  return (
    <div className="min-h-screen bg-[#050505] p-6 text-white">
      <h1 className="mb-2 text-2xl font-bold">Pricing Audit Log</h1>

      <p className="mb-6 text-sm text-gray-400">
        Recent recorded pricing-engine activity and operational metadata.
      </p>

      {loading && (
        <div className="py-6 text-sm text-gray-400">
          Loading pricing audit activity...
        </div>
      )}

      {!loading && error && (
        <div
          role="alert"
          className="rounded-lg border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-300"
        >
          {error}
        </div>
      )}

      {!loading && !error && events.length === 0 && (
        <div className="rounded-lg border border-white/10 bg-white/5 p-4 text-sm text-gray-400">
          No pricing audit activity was returned.
        </div>
      )}

      {!loading && !error && events.length > 0 && (
        <div className="overflow-x-auto rounded-lg border border-white/10">
          <table className="w-full min-w-[1100px] bg-black text-left text-sm">
            <thead className="bg-white/5 text-gray-300">
              <tr>
                <th className="px-3 py-3">Timestamp</th>
                <th className="px-3 py-3">Actor Role</th>
                <th className="px-3 py-3">Actor ID</th>
                <th className="px-3 py-3">Action</th>
                <th className="px-3 py-3">Module</th>
                <th className="px-3 py-3">Status</th>
                <th className="px-3 py-3">Duration (ms)</th>
                <th className="px-3 py-3">Details</th>
              </tr>
            </thead>

            <tbody>
              {events.map((event) => (
                <tr
                  key={event.id}
                  className="border-t border-white/10 align-top"
                >
                  <td className="whitespace-nowrap px-3 py-3 text-gray-300">
                    {formatTimestamp(event.created_at)}
                  </td>

                  <td className="px-3 py-3">
                    {event.actor_role || "—"}
                  </td>

                  <td className="px-3 py-3">
                    {event.actor_id ?? "—"}
                  </td>

                  <td className="px-3 py-3 font-medium">
                    {event.action || "—"}
                  </td>

                  <td className="px-3 py-3">
                    {event.module || "—"}
                  </td>

                  <td className="px-3 py-3">
                    {event.status || "—"}
                  </td>

                  <td className="px-3 py-3 tabular-nums">
                    {event.duration_ms ?? "—"}
                  </td>

                  <td className="max-w-md px-3 py-3">
                    <pre className="whitespace-pre-wrap break-words text-xs text-gray-300">
                      {formatDetails(event.details)}
                    </pre>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}