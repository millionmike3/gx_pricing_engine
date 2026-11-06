"use client";

import React, { useEffect, useState } from "react";
import axios, { AxiosResponse } from "axios";

interface PricingRow {
  product_type: string;
  property_type: string;
  lending_type: string;
  credit_tier: string;
  base_rate: number;
  final_rate: number;
  margin_bps: number;
}

interface RiskSnapshot {
  fraud_risk_tier: string;
  fraud_score: number;
  health_tier: string;
  health_score: number;
}

interface BehaviorSnapshot {
  behavior_tier: string;
  behavior_score: number;
}

interface RateLock {
  locked_rate: number;
  locked_at: string;
  expires_at: string;
}

interface PricingSummaryResponse {
  pricing: PricingRow | null;
  risk: RiskSnapshot | null;
  behavior: BehaviorSnapshot | null;
  lock: RateLock | null;
}

export default function LoanOfficerPricingSummaryPage({
  params,
}: {
  params: { loanId: string };
}) {
  const [data, setData] = useState<PricingSummaryResponse | null>(null);

  useEffect(() => {
    axios
      .get<PricingSummaryResponse>(
        `${process.env.NEXT_PUBLIC_API_URL}/loan-officers/pricing-summary/${params.loanId}`
      )
      .then((res: AxiosResponse<PricingSummaryResponse>) => {
        setData(res.data);
      })
      .catch(console.error);
  }, [params.loanId]);

  if (!data) {
    return <div className="p-6 text-white">Loading pricing summary…</div>;
  }

  const { pricing, risk, behavior, lock } = data;

  return (
    <div className="p-6 bg-[#050505] min-h-screen text-white">
      <h1 className="text-2xl font-bold mb-4">Loan Officer Pricing Summary</h1>

      {pricing && (
        <div className="mb-4 p-4 bg-black border border-white/10 rounded-lg">
          <h2 className="text-lg font-semibold mb-2">Pricing</h2>
          <div>Product: {pricing.product_type}</div>
          <div>Property: {pricing.property_type}</div>
          <div>Lending: {pricing.lending_type}</div>
          <div>Credit Tier: {pricing.credit_tier}</div>
          <div>Base Rate: {pricing.base_rate.toFixed(3)}%</div>
          <div>Final Rate: {pricing.final_rate.toFixed(3)}%</div>
          <div>Margin: {pricing.margin_bps} bps</div>
        </div>
      )}

      {risk && (
        <div className="mb-4 p-4 bg-black border border-white/10 rounded-lg">
          <h2 className="text-lg font-semibold mb-2">Risk</h2>
          <div>Fraud Tier: {risk.fraud_risk_tier}</div>
          <div>Fraud Score: {risk.fraud_score}</div>
          <div>Health Tier: {risk.health_tier}</div>
          <div>Health Score: {risk.health_score}</div>
        </div>
      )}

      {behavior && (
        <div className="mb-4 p-4 bg-black border border-white/10 rounded-lg">
          <h2 className="text-lg font-semibold mb-2">Behavior</h2>
          <div>Behavior Tier: {behavior.behavior_tier}</div>
          <div>Behavior Score: {behavior.behavior_score}</div>
        </div>
      )}

      {lock && (
        <div className="mb-4 p-4 bg-black border border-white/10 rounded-lg">
          <h2 className="text-lg font-semibold mb-2">Rate Lock</h2>
          <div>Locked Rate: {lock.locked_rate.toFixed(3)}%</div>
          <div>Locked At: {new Date(lock.locked_at).toLocaleString()}</div>
          <div>Expires At: {new Date(lock.expires_at).toLocaleString()}</div>
        </div>
      )}
    </div>
  );
}
