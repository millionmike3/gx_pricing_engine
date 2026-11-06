"use client";

import React, { useEffect, useState } from "react";
import axios from "axios";

interface FraudBucket {
  fraud_risk_tier: string;
  count: number;
  avg_fraud_score: number;
}

interface FraudDashboardSummary {
  total_loans: number;
  buckets: FraudBucket[];
}

export default function OwnerFraudDashboardPage() {
  const [data, setData] = useState<FraudDashboardSummary | null>(null);

  useEffect(() => {
    axios
      .get(`${process.env.NEXT_PUBLIC_API_URL}/owners/fraud/summary`, {
        headers: { "x-admin-key": process.env.ADMIN_API_KEY },
      })
      .then(res => setData(res.data))
      .catch(console.error);
  }, []);

  if (!data) return <div className="p-6 text-white">Loading fraud dashboard…</div>;

  return (
    <div className="p-6 bg-[#050505] min-h-screen text-white">
      <h1 className="text-2xl font-bold mb-4">Owner Fraud Intelligence Dashboard</h1>

      <div className="mb-4 p-4 bg-black border border-white/10 rounded-lg">
        <div className="text-sm text-gray-400">Total Loans</div>
        <div className="text-2xl font-semibold">{data.total_loans}</div>
      </div>

      <table className="w-full text-sm bg-black border border-white/10 rounded-lg overflow-hidden">
        <thead className="bg-white/5">
          <tr>
            <th className="px-3 py-2 text-left">Fraud Tier</th>
            <th className="px-3 py-2 text-right">Count</th>
            <th className="px-3 py-2 text-right">Avg Fraud Score</th>
          </tr>
        </thead>
        <tbody>
          {data.buckets.map(b => (
            <tr key={b.fraud_risk_tier} className="border-t border-white/10">
              <td className="px-3 py-2">{b.fraud_risk_tier}</td>
              <td className="px-3 py-2 text-right">{b.count}</td>
              <td className="px-3 py-2 text-right">{b.avg_fraud_score}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
