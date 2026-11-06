"use client";

import React, { useState } from "react";
import axios from "axios";

interface PricingPreview {
  product_type: string;
  final_rate: number;
  payment: number;
}

export default function BorrowerPricingPreviewPage() {
  const [amount, setAmount] = useState(400000);
  const [fico, setFico] = useState(720);
  const [results, setResults] = useState<PricingPreview[]>([]);

  const runPreview = async () => {
    const res = await axios.post(
      `${process.env.NEXT_PUBLIC_API_URL}/borrowers/pricing-preview`,
      { amount, fico }
    );
    setResults(res.data);
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Your Pricing Preview</h1>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <label className="text-sm text-gray-400">Loan Amount</label>
          <input
            type="number"
            value={amount}
            onChange={e => setAmount(Number(e.target.value))}
            className="mt-1 p-2 bg-black border border-white/10 rounded-lg w-full"
          />
        </div>
        <div>
          <label className="text-sm text-gray-400">Estimated Credit Score</label>
          <input
            type="number"
            value={fico}
            onChange={e => setFico(Number(e.target.value))}
            className="mt-1 p-2 bg-black border border-white/10 rounded-lg w-full"
          />
        </div>
      </div>

      <button
        onClick={runPreview}
        className="px-4 py-2 bg-[#3CF46B] text-black font-bold rounded-lg"
      >
        See My Rates
      </button>

      {results.length > 0 && (
        <table className="mt-6 w-full text-sm bg-black border border-white/10 rounded-lg overflow-hidden">
          <thead className="bg-white/5">
            <tr>
              <th className="px-3 py-2 text-left">Product</th>
              <th className="px-3 py-2 text-right">Rate</th>
              <th className="px-3 py-2 text-right">Payment</th>
            </tr>
          </thead>
          <tbody>
            {results.map((r, i) => (
              <tr key={i} className="border-t border-white/10">
                <td className="px-3 py-2">{r.product_type}</td>
                <td className="px-3 py-2 text-right">
                  {r.final_rate.toFixed(3)}%
                </td>
                <td className="px-3 py-2 text-right">
                  ${r.payment.toLocaleString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
