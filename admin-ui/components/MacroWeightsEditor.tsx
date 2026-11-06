"use client";

import React from "react";

interface MacroWeight {
  factor: string;
  weight: number;
}

export default function MacroWeightsEditor({
  weights,
}: {
  weights: MacroWeight[];
}) {
  return (
    <div className="space-y-4">
      {weights.map((w, i) => (
        <div
          key={i}
          className="p-4 bg-black border border-white/10 rounded-lg flex justify-between"
        >
          <div>{w.factor}</div>
          <div>{w.weight}</div>
        </div>
      ))}
    </div>
  );
}
