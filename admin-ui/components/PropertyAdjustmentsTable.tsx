"use client";

import React from "react";

interface PropertyAdjustment {
  property_type: string;
  adjustment_bps: number;
}

export default function PropertyAdjustmentsTable({
  adjustments,
}: {
  adjustments: PropertyAdjustment[];
}) {
  return (
    <table className="w-full text-sm bg-black border border-white/10 rounded-lg overflow-hidden">
      <thead className="bg-white/5">
        <tr>
          <th className="px-3 py-2 text-left">Property Type</th>
          <th className="px-3 py-2 text-right">Adjustment (bps)</th>
        </tr>
      </thead>
      <tbody>
        {adjustments.map((a, i) => (
          <tr key={i} className="border-t border-white/10">
            <td className="px-3 py-2">{a.property_type}</td>
            <td className="px-3 py-2 text-right">{a.adjustment_bps}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
