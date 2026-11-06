"use client";

import React from "react";

interface TableProps {
  columns: string[];
  data: Record<string, any>[];
  className?: string;
}

export default function Table({
  columns,
  data,
  className = "",
}: TableProps) {
  return (
    <table
      className={`w-full border-collapse bg-black border border-white/10 rounded-lg overflow-hidden ${className}`}
    >
      <thead className="bg-white/5">
        <tr>
          {columns.map((col) => (
            <th
              key={col}
              className="border border-white/10 px-3 py-2 text-left text-sm"
            >
              {col}
            </th>
          ))}
        </tr>
      </thead>

      <tbody>
        {data.map((row, idx) => (
          <tr key={idx} className="border-t border-white/10">
            {columns.map((col) => (
              <td key={col} className="px-3 py-2 text-sm">
                {row[col]}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
