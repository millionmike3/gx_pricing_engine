"use client";

import { usePricingEngine } from "../hooks/usePricingEngine";
import ComparisonTable from "./ComparisonTable";

export default function PricingResults() {
  const { result, loading } = usePricingEngine();

  if (loading) return <p>Loading...</p>;
  if (!result) return <p>No results yet.</p>;

  return (
    <div className="mt-6">
      <ComparisonTable data={result} />
    </div>
  );
}
