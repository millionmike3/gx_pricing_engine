"use client";

import Link from "next/link";

export default function HomePage() {
  return (
    <div className="p-10 space-y-20">

      {/* HERO SECTION */}
      <section className="text-center space-y-6">
        <h1 className="text-6xl font-extrabold text-gx-accent-blue animate-pulse">
          GenXBaby OS
        </h1>

        <p className="text-gray-400 text-xl max-w-3xl mx-auto leading-relaxed">
          The unified pricing, underwriting, investor intelligence, and borrower automation platform.
          Built for modern lenders who demand precision, speed, and transparency.
        </p>

        {/* CTA BUTTON */}
        <div className="pt-4">
          <Link
            href="/pricing"
            className="gx-btn px-8 py-4 text-lg rounded-full shadow-lg hover:scale-105 transition-transform"
          >
            Get Started
          </Link>
        </div>

        {/* Animated Subtext */}
        <p className="text-gray-500 animate-bounce pt-4">
          Real‑time pricing. Real‑time underwriting. Real‑time intelligence.
        </p>
      </section>

      {/* FEATURE GRID */}
      <section className="space-y-10">
        <h2 className="text-3xl font-bold text-gx-accent-blue text-center">
          Why GenXBaby OS?
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">

          <div className="gx-card p-6 space-y-3">
            <div className="text-4xl">⚡</div>
            <h3 className="text-xl font-semibold text-gx-accent-blue">Real‑Time Pricing</h3>
            <p className="text-gray-400">
              LLPA logic, investor overlays, risk‑based adjustments, and borrower intelligence — all computed instantly.
            </p>
          </div>

          <div className="gx-card p-6 space-y-3">
            <div className="text-4xl">📊</div>
            <h3 className="text-xl font-semibold text-gx-accent-blue">Investor Analytics</h3>
            <p className="text-gray-400">
              Yield curves, risk exposure, delivery optimization, and portfolio intelligence built for institutional investors.
            </p>
          </div>

          <div className="gx-card p-6 space-y-3">
            <div className="text-4xl">🧩</div>
            <h3 className="text-xl font-semibold text-gx-accent-blue">Underwriting Engine</h3>
            <p className="text-gray-400">
              Automated eligibility, borrower scoring, document intelligence, and compliance‑ready audit trails.
            </p>
          </div>

        </div>
      </section>

      {/* PRICING ENGINE DEEP DIVE */}
      <section className="gx-card p-10 space-y-6">
        <h2 className="text-3xl font-bold text-gx-accent-blue">
          The GenXBaby Pricing Engine
        </h2>

        <p className="text-gray-300 leading-relaxed">
          The GenXBaby Pricing Engine is engineered to outperform legacy PPE systems like Optimal Blue,
          Encompass PPE, and investor rate sheets. It merges market data, LLPA rules, investor overlays,
          borrower intelligence, and risk scoring into one unified pricing brain.
        </p>

        <ul className="list-disc list-inside text-gray-400 space-y-2">
          <li>Real‑time pricing with investor‑specific margin controls</li>
          <li>LLPA engine with credit, LTV, occupancy, and property‑type adjustments</li>
          <li>Scenario testing for underwriting, pricing, and investor delivery</li>
          <li>Matrix ingestion for investor rate sheets and overlays</li>
          <li>Risk‑based pricing using borrower intelligence and behavioral scoring</li>
          <li>Full audit trail for compliance and secondary market delivery</li>
        </ul>

        <p className="text-gray-300">
          Every quote is transparent, auditable, and aligned with investor delivery rules.
        </p>
      </section>

      {/* MODULE OVERVIEW */}
      <section className="space-y-10">
        <h2 className="text-3xl font-bold text-gx-accent-blue text-center">
          System Modules
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">

          <div className="gx-card p-6 space-y-3">
            <div className="text-4xl">💰</div>
            <h3 className="text-xl font-semibold text-gx-accent-blue">Pricing Engine</h3>
            <p className="text-gray-400">
              Run borrower‑specific pricing scenarios, investor overlays, and LLPA adjustments in real time.
            </p>
          </div>

          <div className="gx-card p-6 space-y-3">
            <div className="text-4xl">🛠️</div>
            <h3 className="text-xl font-semibold text-gx-accent-blue">Admin Dashboard</h3>
            <p className="text-gray-400">
              Upload matrices, manage investor rules, configure pricing margins, and monitor system health.
            </p>
          </div>

          <div className="gx-card p-6 space-y-3">
            <div className="text-4xl">📈</div>
            <h3 className="text-xl font-semibold text-gx-accent-blue">Investor Portal</h3>
            <p className="text-gray-400">
              View portfolio performance, yield curves, risk exposure, and delivery optimization analytics.
            </p>
          </div>

          <div className="gx-card p-6 space-y-3">
            <div className="text-4xl">🏠</div>
            <h3 className="text-xl font-semibold text-gx-accent-blue">Borrower Portal</h3>
            <p className="text-gray-400">
              Borrowers can apply, upload documents, check eligibility, and receive real‑time pricing updates.
            </p>
          </div>

        </div>
      </section>

      {/* CLOSING */}
      <section className="text-center space-y-4">
        <h2 className="text-3xl font-bold text-gx-accent-blue">
          Built for Modern Lending
        </h2>
        <p className="text-gray-400 max-w-3xl mx-auto">
          GenXBaby OS delivers speed, accuracy, and compliance at scale — empowering lenders, brokers,
          investors, and fintech operators with a unified, intelligent pricing + underwriting ecosystem.
        </p>
      </section>

    </div>
  );
}
