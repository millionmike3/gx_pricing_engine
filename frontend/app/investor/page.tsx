"use client";

import InvestorDashboard from "./components/InvestorDashboard";

export default function InvestorPage() {
  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold">Investor Dashboard</h1>
        <p className="text-gray-600">
          Portfolio performance, yield charts, and risk exposure.
        </p>
      </div>

      {/* Main Investor Module */}
      <InvestorDashboard />
    </div>
  );
}
