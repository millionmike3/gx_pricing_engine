"use client";

import React from "react";

interface CardProps {
  children: React.ReactNode;
  className?: string;
}

export default function Card({ children, className = "" }: CardProps) {
  return (
    <div
      className={`border border-white/10 rounded-lg p-4 bg-black shadow-sm ${className}`}
    >
      {children}
    </div>
  );
}
