"use client";

import BorrowerDashboard from "./components/BorrowerDashboard";

export default function BorrowerPage() {
  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold">Borrower Portal</h1>
        <p className="text-gray-600">
          Loan application, eligibility, and document upload.
        </p>
      </div>

      {/* Main Borrower Module */}
      <BorrowerDashboard />
    </div>
  );
}
