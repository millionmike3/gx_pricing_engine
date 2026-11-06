"use client";

import React, { useEffect, useState } from "react";
import axios from "axios";

interface RevenueByProduct {
  product_type: string;
  total_loans: number;
  total_revenue_bps: number;
  total_revenue_dollars: number;
}

interface RevenueSummary {
  total_loans: number;
  total_revenue_dollars: number;
  avg_margin_bps: number;
  by_product: RevenueByProduct[];
}

export default function OwnerRevenueDashboardPage() {
  const [data, setData] = useState<RevenueSummary | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      const res = await axios.get(
        `${process.env.NEXT_PUBLIC_API_URL}/owners/revenue/summary`,
        {
          headers: {
            "x-admin-key": process.env.ADMIN_API_KEY,
          },
        }
      );
      setData(res.data);
    };

    fetchData().catch(console.error);
  }, []);

  if (!data) {
    return (
      <div className="p-6 text-white">
        Loading owner revenue dashboard…
      </div>
    );
  }

  return (
    <div className="p-6 bg-[#050505] min-h-screen text-white">
      <h1 className="text-2xl font-bold mb-4">Owner Revenue Dashboard</h1>

      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="p-4 bg-black border border-white/10 rounded-lg">
          <div className="text-sm text-gray-400">Total Loans</div>
          <div className="text-2xl font-semibold">{data.total_loans}</div>
        </div>
        <div className="p-4 bg-black border border-white/10 rounded-lg">
          <div className="text-sm text-gray-400">Total Revenue</div>
          <div className="text-2xl font-semibold">
            ${data.total_revenue_dollars.toLocaleString()}
          </div>
        </div>
        <div className="p-4 bg-black border border-white/10 rounded-lg">
          <div className="text-sm text-gray-400">Avg Margin (bps)</div>
          <div className="text-2xl font-semibold">{data.avg_margin_bps}</div>
        </div>
      </div>

      <h2 className="text-xl font-semibold mb-3">Revenue by Product</h2>
      <table className="w-full text-sm bg-black border border-white/10 rounded-lg overflow-hidden">
        <thead className="bg-white/5">
          <tr>
            <th className="px-3 py-2 text-left">Product</th>
            <th className="px-3 py-2 text-right">Loans</th>
            <th className="px-3 py-2 text-right">Revenue (bps)</th>
            <th className="px-3 py-2 text-right">Revenue ($)</th>
          </tr>
        </thead>
        <tbody>
          {data.by_product.map(p => (
            <tr key={p.product_type} className="border-t border-white/10">
              <td className="px-3 py-2">{p.product_type}</td>
              <td className="px-3 py-2 text-right">{p.total_loans}</td>
              <td className="px-3 py-2 text-right">{p.total_revenue_bps}</td>
              <td className="px-3 py-2 text-right">
                ${p.total_revenue_dollars.toLocaleString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
