"use client";

import React, { useEffect, useState } from "react";
import axios, { AxiosResponse } from "axios";

interface InvestorRateRow {
  product_type: string;
  investor: string;
  buy_price_bps: number;
  sell_price_bps: number;
}

export default function InvestorRateSheetPage() {
  const [rows, setRows] = useState<InvestorRateRow[]>([]);

  useEffect(() => {
    axios
      .get<InvestorRateRow[]>(
        `${process.env.NEXT_PUBLIC_API_URL}/investors/rate-sheet`
      )
      .then((res: AxiosResponse<InvestorRateRow[]>) => {
        setRows(res.data);
      })
      .catch(console.error);
  }, []);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Investor Rate Sheet</h1>
      <table className="w-full text-sm bg-black border border-white/10 rounded-lg overflow-hidden">
        <thead className="bg-white/5">
          <tr>
            <th className="px-3 py-2 text-left">Investor</th>
            <th className="px-3 py-2 text-left">Product</th>
            <th className="px-3 py-2 text-right">Buy (bps)</th>
            <th className="px-3 py-2 text-right">Sell (bps)</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i} className="border-t border-white/10">
              <td className="px-3 py-2">{r.investor}</td>
              <td className="px-3 py-2">{r.product_type}</td>
              <td className="px-3 py-2 text-right">{r.buy_price_bps}</td>
              <td className="px-3 py-2 text-right">{r.sell_price_bps}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
