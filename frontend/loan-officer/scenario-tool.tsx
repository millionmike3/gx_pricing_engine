"use client";

import React, { useState } from "react";
import axios, { AxiosResponse } from "axios";

interface ScenarioResult {
  scenario: string;
  scenario_adj_bps: number;
}

export default function LoanOfficerScenarioToolPage() {
  const [scenario, setScenario] = useState<string>("RECESSION");
  const [result, setResult] = useState<ScenarioResult | null>(null);

  const runScenario = async () => {
    const res: AxiosResponse<ScenarioResult> = await axios.get(
      `${process.env.NEXT_PUBLIC_API_URL}/loan-officers/scenario-tool/run`,
      { params: { scenario } }
    );
    setResult(res.data);
  };

  return (
    <div className="p-6 bg-[#050505] min-h-screen text-white">
      <h1 className="text-2xl font-bold mb-4">Loan Officer Scenario Pricing Tool</h1>

      <div className="mb-4">
        <label className="text-sm text-gray-400">Scenario</label>
        <select
          value={scenario}
          onChange={e => setScenario(e.target.value)}
          className="mt-1 p-2 bg-black border border-white/10 rounded-lg text-white"
        >
          <option value="RECESSION">Recession</option>
          <option value="HIGH_INFLATION">High Inflation</option>
          <option value="STRONG_GROWTH">Strong Growth</option>
        </select>
      </div>

      <button
        onClick={runScenario}
        className="px-4 py-2 bg-[#3CF46B] text-black font-bold rounded-lg"
      >
        Run Scenario
      </button>

      {result && (
        <div className="mt-4 p-4 bg-black border border-white/10 rounded-lg">
          <div className="text-sm text-gray-400">Scenario</div>
          <div className="text-lg font-semibold">{result.scenario}</div>

          <div className="mt-2 text-sm text-gray-400">Adjustment (bps)</div>
          <div className="text-xl font-bold">{result.scenario_adj_bps}</div>
        </div>
      )}
    </div>
  );
}
