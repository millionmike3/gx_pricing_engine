"use client";

import React, { useEffect, useState } from "react";
import axios from "axios";

interface AuditEvent {
  id: string;
  actor_role: string;
  actor_id?: string;
  action: string;
  module: string;
  details: string;
  created_at: string;
}

export default function PricingAuditLogPage() {
  const [events, setEvents] = useState<AuditEvent[]>([]);

  useEffect(() => {
    axios
      .get(`${process.env.NEXT_PUBLIC_API_URL}/pricing/audit-log/recent`, {
        headers: { "x-admin-key": process.env.ADMIN_API_KEY },
      })
      .then(res => setEvents(res.data))
      .catch(console.error);
  }, []);

  return (
    <div className="p-6 bg-[#050505] min-h-screen text-white">
      <h1 className="text-2xl font-bold mb-4">Pricing Audit Log</h1>

      <table className="w-full text-sm bg-black border border-white/10 rounded-lg overflow-hidden">
        <thead className="bg-white/5">
          <tr>
            <th className="px-3 py-2 text-left">Timestamp</th>
            <th className="px-3 py-2 text-left">Actor Role</th>
            <th className="px-3 py-2 text-left">Actor ID</th>
            <th className="px-3 py-2 text-left">Action</th>
            <th className="px-3 py-2 text-left">Module</th>
            <th className="px-3 py-2 text-left">Details</th>
          </tr>
        </thead>
        <tbody>
          {events.map(e => (
            <tr key={e.id} className="border-t border-white/10">
              <td className="px-3 py-2">
                {new Date(e.created_at).toLocaleString()}
              </td>
              <td className="px-3 py-2">{e.actor_role}</td>
              <td className="px-3 py-2">{e.actor_id || "—"}</td>
              <td className="px-3 py-2">{e.action}</td>
              <td className="px-3 py-2">{e.module}</td>
              <td className="px-3 py-2">{e.details}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
