"use client";

import React, { useEffect, useState } from "react";
import axios from "axios";

interface ExecutionBucket {
  investor: string;
  total_loans: number;
  avg_execution_bps: number;
  total_pnl_dollars: number;
}

interface ExecutionDashboardSummary {
  total_loans: number;
  total_pnl_dollars: number;
  buckets: ExecutionBucket[];
}

export default function OwnerExecutionDashboardPage() {
  const [data, setData] = useState<ExecutionDashboardSummary | null>(null);

  useEffect(() => {
    axios
      .get(`${process.env.NEXT_PUBLIC_API_URL}/owners/execution/summary`, {
        headers: { "x-admin-key": process.env.ADMIN_API_KEY },
      })
      .then(res => setData(res.data))
      .catch(console.error);
  }, []);

  if (!data) return <div className="p-6 text-white">Loading execution dashboard…</div>;

  return (
    <div className="p-6 bg-[#050505] min-h-screen text-white">
      <h1 className="text-2xl font-bold mb-4">Secondary‑Market Execution Dashboard</h1>

      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="p-4 bg-black border border-white/10 rounded-lg">
          <div className="text-sm text-gray-400">Total Loans</div>
          <div className="text-2xl font-semibold">{data.total_loans}</div>
        </div>
        <div className="p-4 bg-black border border-white/10 rounded-lg">
          <div className="text-sm text-gray-400">Total P&L</div>
          <div className="text-2xl font-semibold">
            ${data.total_pnl_dollars.toLocaleString()}
          </div>
        </div>
      </div>

      <h2 className="text-xl font-semibold mb-3">Execution by Investor</h2>
      <table className="w-full text-sm bg-black border border-white/10 rounded-lg overflow-hidden">
        <thead className="bg-white/5">
          <tr>
            <th className="px-3 py-2 text-left">Investor</th>
            <th className="px-3 py-2 text-right">Loans</th>
            <th className="px-3 py-2 text-right">Avg Execution (bps)</th>
            <th className="px-3 py-2 text-right">Total P&L ($)</th>
          </tr>
        </thead>
        <tbody>
          {data.buckets.map(b => (
            <tr key={b.investor} className="border-t border-white/10">
              <td className="px-3 py-2">{b.investor}</td>
              <td className="px-3 py-2 text-right">{b.total_loans}</td>
              <td className="px-3 py-2 text-right">{b.avg_execution_bps}</td>
              <td className="px-3 py-2 text-right">
                ${b.total_pnl_dollars.toLocaleString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
