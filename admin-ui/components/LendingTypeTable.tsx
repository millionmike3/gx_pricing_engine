"use client";

import React from "react";

interface LendingType {
  type: string;
  description: string;
}

export default function LendingTypeTable({ types }: { types: LendingType[] }) {
  return (
    <table className="w-full text-sm bg-black border border-white/10 rounded-lg overflow-hidden">
      <thead className="bg-white/5">
        <tr>
          <th className="px-3 py-2 text-left">Type</th>
          <th className="px-3 py-2 text-left">Description</th>
        </tr>
      </thead>
      <tbody>
        {types.map((t, i) => (
          <tr key={i} className="border-t border-white/10">
            <td className="px-3 py-2">{t.type}</td>
            <td className="px-3 py-2">{t.description}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
