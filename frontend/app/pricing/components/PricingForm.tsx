"use client";

import { useState } from "react";
import { usePricingEngine } from "../hooks/usePricingEngine";

export default function PricingForm() {
  const { getQuote } = usePricingEngine();

  const [form, setForm] = useState({
    loanAmount: "",
    creditScore: "",
    propertyType: "",
  });

  function handleChange(e: any) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  function submit() {
    getQuote(form);
  }

  return (
    <div className="p-4 border rounded-lg space-y-4">
      <input
        name="loanAmount"
        placeholder="Loan Amount"
        className="border p-2 w-full"
        onChange={handleChange}
      />

      <input
        name="creditScore"
        placeholder="Credit Score"
        className="border p-2 w-full"
        onChange={handleChange}
      />

      <input
        name="propertyType"
        placeholder="Property Type"
        className="border p-2 w-full"
        onChange={handleChange}
      />

      <button
        onClick={submit}
        className="bg-blue-600 text-white px-4 py-2 rounded"
      >
        Get Pricing
      </button>
    </div>
  );
}
