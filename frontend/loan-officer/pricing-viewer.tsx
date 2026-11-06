"use client";

import React, { useEffect, useState } from "react";
import axios, { AxiosResponse } from "axios";

interface PricingRow {
  product_type: string;
  property_type: string;
  lending_type: string;
  credit_tier: string;
  base_rate: number;
  final_rate: number;
  margin_bps: number;
}

export default function LoanOfficerPricingViewerPage({
  params,
}: {
  params: { loanId: string };
}) {
  const [rows, setRows] = useState<PricingRow[]>([]);

  useEffect(() => {
    axios
      .get<PricingRow[]>(
        `${process.env.NEXT_PUBLIC_API_URL}/loan-officers/pricing-viewer/${params.loanId}`
      )
      .then((res: AxiosResponse<PricingRow[]>) => {
        setRows(res.data);
      })
      .catch(console.error);
  }, [params.loanId]);

  return (
    <div className="p-6 bg-[#050505] min-h-screen text-white">
      <h1 className="text-2xl font-bold mb-4">Loan Officer Pricing Viewer</h1>

      <table className="w-full text-sm bg-black border border-white/10 rounded-lg overflow-hidden">
        <thead className="bg-white/5">
          <tr>
            <th className="px-3 py-2 text-left">Product</th>
            <th className="px-3 py-2 text-left">Property</th>
            <th className="px-3 py-2 text-left">Lending</th>
            <th className="px-3 py-2 text-left">Credit Tier</th>
            <th className="px-3 py-2 text-right">Base Rate</th>
            <th className="px-3 py-2 text-right">Final Rate</th>
            <th className="px-3 py-2 text-right">Margin (bps)</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i} className="border-t border-white/10">
              <td className="px-3 py-2">{r.product_type}</td>
              <td className="px-3 py-2">{r.property_type}</td>
              <td className="px-3 py-2">{r.lending_type}</td>
              <td className="px-3 py-2">{r.credit_tier}</td>
              <td className="px-3 py-2 text-right">{r.base_rate.toFixed(3)}%</td>
              <td className="px-3 py-2 text-right">{r.final_rate.toFixed(3)}%</td>
              <td className="px-3 py-2 text-right">{r.margin_bps}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
