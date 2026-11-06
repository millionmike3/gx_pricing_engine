"use client";

import React from "react";

interface SelectOption {
  label: string;
  value: string | number;
}

interface SelectProps {
  label?: string;
  value: string | number;
  options: SelectOption[];
  onChange: (value: string | number) => void;
  className?: string;
}

export default function Select({
  label,
  value,
  options,
  onChange,
  className = "",
}: SelectProps) {
  return (
    <div className="flex flex-col mb-3">
      {label && <label className="text-sm mb-1">{label}</label>}

      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className={`border border-white/10 rounded px-3 py-2 bg-black text-white ${className}`}
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  );
}
