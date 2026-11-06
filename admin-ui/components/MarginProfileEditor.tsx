"use client";

import React from "react";

interface MarginProfile {
  name: string;
  margin_bps: number;
}

export default function MarginProfileEditor({
  profiles,
}: {
  profiles: MarginProfile[];
}) {
  return (
    <div className="space-y-4">
      {profiles.map((p, i) => (
        <div
          key={i}
          className="p-4 bg-black border border-white/10 rounded-lg flex justify-between"
        >
          <div>{p.name}</div>
          <div>{p.margin_bps} bps</div>
        </div>
      ))}
    </div>
  );
}
