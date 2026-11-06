"use client";

import React from "react";

interface CreditTier {
  tier: string;
  minScore: number;
  maxScore: number;
}

export default function CreditTierTable({ tiers }: { tiers: CreditTier[] }) {
  return (
    <table className="w-full text-sm bg-black border border-white/10 rounded-lg overflow-hidden">
      <thead className="bg-white/5">
        <tr>
          <th className="px-3 py-2 text-left">Tier</th>
          <th className="px-3 py-2 text-left">Min Score</th>
          <th className="px-3 py-2 text-left">Max Score</th>
        </tr>
      </thead>
      <tbody>
        {tiers.map((t, i) => (
          <tr key={i} className="border-t border-white/10">
            <td className="px-3 py-2">{t.tier}</td>
            <td className="px-3 py-2">{t.minScore}</td>
            <td className="px-3 py-2">{t.maxScore}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
