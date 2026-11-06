"use client";

import React from "react";

interface InputProps {
  label?: string;
  value: string | number;
  onChange: (value: string) => void;
  type?: string;
  className?: string;
}

export default function Input({
  label,
  value,
  onChange,
  type = "text",
  className = "",
}: InputProps) {
  return (
    <div className="flex flex-col mb-3">
      {label && <label className="text-sm mb-1">{label}</label>}
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className={`border border-white/10 rounded px-3 py-2 bg-black text-white ${className}`}
      />
    </div>
  );
}
