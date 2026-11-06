"use client";

import ScenarioTester from "./components/ScenarioTester";
import MatrixUploader from "./components/MatrixUploader";
import AdminDashboard from "./components/AdminDashboard";

export default function AdminPage() {
  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold">Admin Dashboard</h1>
        <p className="text-gray-600">
          Upload matrices, run scenarios, and monitor system health.
        </p>
      </div>

      {/* Main Admin Modules */}
      <AdminDashboard />
      <ScenarioTester />
      <MatrixUploader />
    </div>
  );
}
