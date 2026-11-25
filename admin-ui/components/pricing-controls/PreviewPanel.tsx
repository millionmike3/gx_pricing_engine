"use client";

import React, { useState } from "react";
import axios from "axios";
import { api } from "../../services/api";

interface PricingPreviewRequest {
  fico: number;
  ltv: number;
  loan_amount: number;
  investor: string;
  property_type: string;
  occupancy: string;
  purpose: string;
  state: string;
  product_type: string;
  rate_type: string;
  dti?: number;
  dscr?: number;
}

interface PricingPreviewResponse {
  base_rate: number;
  fico_ltv_adjustment: number;
  adjustment_source?: string;
  adjustments?: Record<string, unknown> | unknown[];
  investor_adjustment: number;
  adjusted_rate: number;
  final_rate: number;
  investor?: string;
  rate_type?: string;
  inputs?: Record<string, unknown>;
}

export default function PreviewPanel() {
  const [form, setForm] = useState<PricingPreviewRequest>({
    fico: 740,
    ltv: 75,
    loan_amount: 400000,
    investor: "SubstantialFunding",
    property_type: "single_family",
    occupancy: "primary",
    purpose: "purchase",
    state: "NY",
    product_type: "standard",
    rate_type: "30yr_fixed",
  });

  const [preview, setPreview] =
    useState<PricingPreviewResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const updateField = (
    field: keyof PricingPreviewRequest,
    value: string | number
  ) => {
    setForm(prev => ({ ...prev, [field]: value }));
  };

  const fetchPreview = async () => {
    setLoading(true);
    setError("");
    setPreview(null);

    try {
      const response = await api.post("/admin/test-scenario", form);

      if (response.data?.valid !== true || !response.data?.pricing) {
        throw new Error("The pricing engine did not return a valid preview.");
      }

      setPreview(response.data.pricing);
    } catch (err: unknown) {
      if (axios.isAxiosError(err)) {
        const detail = err.response?.data?.detail;
        setError(
          typeof detail === "string"
            ? detail
            : err.message || "Unable to calculate pricing."
        );
      } else {
        setError(
          err instanceof Error
            ? err.message
            : "Unable to calculate pricing."
        );
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 bg-[#111] rounded-xl border border-white/10">
      <h2 className="text-xl font-bold text-white mb-4">
        Matrix-Based Pricing Preview
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div>
          <label className="text-gray-400 text-sm">Credit Score (FICO)</label>
          <input
            type="number"
            min="300"
            max="850"
            value={form.fico}
            onChange={e => updateField("fico", Number(e.target.value))}
            className="w-full mt-1 p-2 bg-black border border-white/10 rounded-lg text-white"
          />
        </div>

        <div>
          <label className="text-gray-400 text-sm">Loan-to-Value (%)</label>
          <input
            type="number"
            min="1"
            max="100"
            step="0.1"
            value={form.ltv}
            onChange={e => updateField("ltv", Number(e.target.value))}
            className="w-full mt-1 p-2 bg-black border border-white/10 rounded-lg text-white"
          />
        </div>

        <div>
          <label className="text-gray-400 text-sm">Loan Amount ($)</label>
          <input
            type="number"
            min="1"
            value={form.loan_amount}
            onChange={e => updateField("loan_amount", Number(e.target.value))}
            className="w-full mt-1 p-2 bg-black border border-white/10 rounded-lg text-white"
          />
        </div>

        <div>
          <label className="text-gray-400 text-sm">Investor</label>
          <select
            value={form.investor}
            onChange={e => updateField("investor", e.target.value)}
            className="w-full mt-1 p-2 bg-black border border-white/10 rounded-lg text-white"
          >
            <option value="SubstantialFunding">Substantial Funding</option>
            <option value="Bayview">Bayview</option>
            <option value="AXA">AXA</option>
            <option value="Wealthfront">Wealthfront</option>
          </select>
        </div>

        <div>
          <label className="text-gray-400 text-sm">Property Type</label>
          <select
            value={form.property_type}
            onChange={e => updateField("property_type", e.target.value)}
            className="w-full mt-1 p-2 bg-black border border-white/10 rounded-lg text-white"
          >
            <option value="single_family">Single Family</option>
            <option value="condo">Condo</option>
            <option value="non_warrantable_condo">Non-Warrantable Condo</option>
            <option value="2_4_unit">2–4 Unit</option>
          </select>
        </div>

        <div>
          <label className="text-gray-400 text-sm">Occupancy</label>
          <select
            value={form.occupancy}
            onChange={e => updateField("occupancy", e.target.value)}
            className="w-full mt-1 p-2 bg-black border border-white/10 rounded-lg text-white"
          >
            <option value="primary">Primary Residence</option>
            <option value="second_home">Second Home</option>
            <option value="investment">Investment Property</option>
          </select>
        </div>

        <div>
          <label className="text-gray-400 text-sm">Loan Purpose</label>
          <select
            value={form.purpose}
            onChange={e => updateField("purpose", e.target.value)}
            className="w-full mt-1 p-2 bg-black border border-white/10 rounded-lg text-white"
          >
            <option value="purchase">Purchase</option>
            <option value="rate_term">Rate/Term Refinance</option>
            <option value="cash_out">Cash-Out Refinance</option>
          </select>
        </div>

        <div>
          <label className="text-gray-400 text-sm">Rate Type</label>
          <select
            value={form.rate_type}
            onChange={e => updateField("rate_type", e.target.value)}
            className="w-full mt-1 p-2 bg-black border border-white/10 rounded-lg text-white"
          >
            <option value="30yr_fixed">30-Year Fixed</option>
            <option value="15yr_fixed">15-Year Fixed</option>
            <option value="10yr_fixed">10-Year Fixed</option>
            <option value="7_1_arm">7/1 ARM</option>
            <option value="5_1_arm">5/1 ARM</option>
          </select>
        </div>

        <div>
          <label className="text-gray-400 text-sm">Pricing Program</label>
          <select
            value={form.product_type}
            onChange={e => updateField("product_type", e.target.value)}
            className="w-full mt-1 p-2 bg-black border border-white/10 rounded-lg text-white"
          >
            <option value="standard">Standard</option>
            <option value="jumbo">Jumbo</option>
            <option value="non_qm">Non-QM</option>
            <option value="dscr">DSCR</option>
            <option value="bank_statement">Bank Statement</option>
            <option value="asset_qualifier">Asset Qualifier</option>
          </select>
        </div>

        <div>
          <label className="text-gray-400 text-sm">Debt-to-Income (%)</label>
          <input
            type="number"
            min="0"
            max="100"
            step="0.1"
            placeholder="Optional"
            value={form.dti ?? ""}
            onChange={e => {
              const value = e.target.value;
              setForm(prev => {
                if (value === "") {
                  const { dti: _dti, ...rest } = prev;
                  return rest;
                }
                return { ...prev, dti: Number(value) };
              });
            }}
            className="w-full mt-1 p-2 bg-black border border-white/10 rounded-lg text-white"
          />
        </div>

        <div>
          <label className="text-gray-400 text-sm">State</label>
          <input
            type="text"
            maxLength={2}
            value={form.state}
            onChange={e => updateField("state", e.target.value.toUpperCase())}
            className="w-full mt-1 p-2 bg-black border border-white/10 rounded-lg text-white"
          />
        </div>
      </div>

      <button
        onClick={fetchPreview}
        disabled={loading}
        className="px-4 py-2 bg-[#3CF46B] text-black font-bold rounded-lg disabled:opacity-50"
      >
        {loading ? "Calculating..." : "Generate Pricing Preview"}
      </button>

      {error && (
        <div className="mt-4 p-3 rounded-lg border border-red-500/40 text-red-300">
          {error}
        </div>
      )}

      {preview && (
        <div className="mt-6 p-4 bg-black border border-white/10 rounded-lg text-white">
          <h3 className="text-lg font-semibold mb-4">
            Pricing Engine Results
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-gray-300">
            <div>
              Base Rate: {preview.base_rate?.toFixed(3)}%
            </div>
            <div>
              FICO/LTV Adjustment: {preview.fico_ltv_adjustment?.toFixed(3)}
            </div>
            <div>
              Investor Adjustment: {preview.investor_adjustment?.toFixed(3)}
            </div>
            <div>
              Adjusted Rate: {preview.adjusted_rate?.toFixed(3)}%
            </div>
          </div>

          <div className="mt-5 text-xl font-bold">
            Final Rate: {preview.final_rate?.toFixed(3)}%
          </div>

          {preview.adjustment_source && (
            <div className="mt-2 text-sm text-gray-400">
              Adjustment Source: {preview.adjustment_source}
            </div>
          )}

          {preview.adjustments && (
            <div className="mt-5">
              <h4 className="font-semibold mb-2">Adjustment Breakdown</h4>
              <pre className="p-3 overflow-x-auto whitespace-pre-wrap break-words text-sm text-gray-300 bg-[#111] rounded-lg">
                {JSON.stringify(preview.adjustments, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
