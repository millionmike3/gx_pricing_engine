"use client";

import React, { useEffect, useState } from "react";
import axios from "axios";

interface BaseRateRow {
  product_type: string;
  base_rate: number;
}

export default function BaseRateEditorPage() {
  const [rows, setRows] = useState<BaseRateRow[]>([]);

  useEffect(() => {
    axios
      .get(`${process.env.NEXT_PUBLIC_API_URL}/pricing/base-rates`)
      .then(res => setRows(res.data))
      .catch(console.error);
  }, []);

  const updateRate = async (product_type: string, base_rate: number) => {
    await axios.put(`${process.env.NEXT_PUBLIC_API_URL}/pricing/base-rates`, {
      product_type,
      base_rate,
    });
    setRows(r =>
      r.map(row =>
        row.product_type === product_type ? { ...row, base_rate } : row
      )
    );
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Base Rate Editor</h1>
      <table className="w-full text-sm bg-black border border-white/10 rounded-lg overflow-hidden">
        <thead className="bg-white/5">
          <tr>
            <th className="px-3 py-2 text-left">Product</th>
            <th className="px-3 py-2 text-right">Base Rate</th>
            <th className="px-3 py-2 text-right">Actions</th>
          </tr>
        </thead>
        <tbody>
          {rows.map(row => (
            <tr key={row.product_type} className="border-t border-white/10">
              <td className="px-3 py-2">{row.product_type}</td>
              <td className="px-3 py-2 text-right">
                {row.base_rate.toFixed(3)}%
              </td>
              <td className="px-3 py-2 text-right">
                <button
                  className="px-3 py-1 bg-[#3CF46B] text-black rounded"
                  onClick={() =>
                    updateRate(row.product_type, row.base_rate + 0.125)
                  }
                >
                  +0.125
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
