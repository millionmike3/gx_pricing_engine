"use client";

import { useState } from "react";
import PricingForm from "./components/PricingForm";
import PricingResults from "./components/PricingResults";

export default function PricingPage() {
  const [loanAmount, setLoanAmount] = useState(300000);

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold mb-4">Pricing Engine</h1>

      {/* Top-level loan amount input */}
      <div className="space-y-2">
        <label className="font-medium">Loan Amount</label>
        <input
          type="number"
          value={loanAmount}
          onChange={(e) => setLoanAmount(Number(e.target.value))}
          className="border p-2 rounded w-full"
        />
      </div>

      {/* Pricing form (self-contained) */}
      <PricingForm />

      {/* Results */}
      <PricingResults />
    </div>
  );
}
