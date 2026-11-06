"use client";

import React, { useState } from "react";
import axios from "axios";

interface PricingPreviewRequest {
  product_type: string;
  property_type: string;
  lending_type: string;
  credit_score: number;
}

interface PricingPreviewResponse {
  base_rate: number;
  macro_adj_bps: number;
  bank_adj_bps: number;
  property_adj_bps: number;
  credit_adj_bps: number;
  lending_type_adj_bps: number;
  margin_bps: number;
  final_rate: number;
}

export default function PreviewPanel() {
  const [form, setForm] = useState<PricingPreviewRequest>({
    product_type: "30Y_FIXED",
    property_type: "SFR",
    lending_type: "PURCHASE",
    credit_score: 740,
  });

  const [preview, setPreview] = useState<PricingPreviewResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (field: keyof PricingPreviewRequest, value: any) => {
    setForm(prev => ({ ...prev, [field]: value }));
  };

  const fetchPreview = async () => {
    try {
      setLoading(true);

      const res = await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/pricing/preview`,
        form,
        {
          headers: {
            "x-admin-key": process.env.ADMIN_API_KEY,
          },
        }
      );

      setPreview(res.data);
    } catch (err) {
      console.error("Preview error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 bg-[#111] rounded-xl border border-white/10">
      <h2 className="text-xl font-bold text-white mb-4">Pricing Preview</h2>

      {/* INPUT FORM */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div>
          <label className="text-gray-400 text-sm">Product Type</label>
          <select
            value={form.product_type}
            onChange={e => handleChange("product_type", e.target.value)}
            className="w-full mt-1 p-2 bg-black border border-white/10 rounded-lg text-white"
          >
            <option value="30Y_FIXED">30Y Fixed</option>
            <option value="15Y_FIXED">15Y Fixed</option>
            <option value="5_1_ARM">5/1 ARM</option>
          </select>
        </div>

        <div>
          <label className="text-gray-400 text-sm">Property Type</label>
          <select
            value={form.property_type}
            onChange={e => handleChange("property_type", e.target.value)}
            className="w-full mt-1 p-2 bg-black border border-white/10 rounded-lg text-white"
          >
            <option value="SFR">Single Family</option>
            <option value="CONDO">Condo</option>
            <option value="MULTI">Multi‑Family</option>
          </select>
        </div>

        <div>
          <label className="text-gray-400 text-sm">Lending Type</label>
          <select
            value={form.lending_type}
            onChange={e => handleChange("lending_type", e.target.value)}
            className="w-full mt-1 p-2 bg-black border border-white/10 rounded-lg text-white"
          >
            <option value="PURCHASE">Purchase</option>
            <option value="REFI_RATE_TERM">Rate/Term Refi</option>
            <option value="REFI_CASH_OUT">Cash‑Out Refi</option>
          </select>
        </div>

        <div>
          <label className="text-gray-400 text-sm">Credit Score</label>
          <input
            type="number"
            value={form.credit_score}
            onChange={e => handleChange("credit_score", Number(e.target.value))}
            className="w-full mt-1 p-2 bg-black border border-white/10 rounded-lg text-white"
          />
        </div>
      </div>

      <button
        onClick={fetchPreview}
        disabled={loading}
        className="px-4 py-2 bg-[#3CF46B] text-black font-bold rounded-lg hover:bg-[#2ac95a] transition"
      >
        {loading ? "Calculating..." : "Generate Preview"}
      </button>

      {/* PREVIEW RESULTS */}
      {preview && (
        <div className="mt-6 p-4 bg-black border border-white/10 rounded-lg">
          <h3 className="text-lg font-semibold text-white mb-3">
            Pricing Breakdown
          </h3>

          <div className="grid grid-cols-2 gap-4 text-gray-300">
            <div>Base Rate: {preview.base_rate.toFixed(3)}%</div>
            <div>Macro Adj: {preview.macro_adj_bps} bps</div>
            <div>Bank Adj: {preview.bank_adj_bps} bps</div>
            <div>Property Adj: {preview.property_adj_bps} bps</div>
            <div>Credit Adj: {preview.credit_adj_bps} bps</div>
            <div>Lending Type Adj: {preview.lending_type_adj_bps} bps</div>
            <div>Margin: {preview.margin_bps} bps</div>
          </div>

          <div className="mt-4 text-white text-xl font-bold">
            Final Rate: {preview.final_rate.toFixed(3)}%
          </div>
        </div>
      )}
    </div>
  );
}
