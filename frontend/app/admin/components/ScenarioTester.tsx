"use client";

import { useAdminAPI } from "../hooks/useAdminAPI";

export default function ScenarioTester() {
  const { runScenario, result } = useAdminAPI();

  return (
    <div className="p-4 border rounded-lg space-y-4">
      <button
        onClick={runScenario}
        className="bg-green-600 text-white px-4 py-2 rounded"
      >
        Run Scenario Test
      </button>

      {result && (
        <pre className="bg-gray-100 p-4 rounded">{JSON.stringify(result, null, 2)}</pre>
      )}
    </div>
  );
}
