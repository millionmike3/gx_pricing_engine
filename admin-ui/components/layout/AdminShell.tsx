"use client";

import type { ReactNode } from "react";
import { useAuth } from "../../services/AuthProvider";

const navigation = [
  {
    heading: "COMMAND CENTER",
    links: [{ label: "Admin Overview", href: "/" }],
  },
  {
    heading: "OWNER INTELLIGENCE",
    links: [
      { label: "Revenue Intelligence", href: "/owners/revenue" },
      { label: "Fraud Intelligence", href: "/owners/fraud" },
      { label: "Behavioral Intelligence", href: "/owners/behavior" },
      { label: "Secondary-Market Execution", href: "/owners/execution" },
    ],
  },
  {
    heading: "PRICING INTELLIGENCE",
    links: [
      { label: "Matrix & Base Rates", href: "/pricing/base-rates" },
      { label: "Pricing Audit Log", href: "/pricing/audit-log" },
      { label: "Credit Tiers", href: "/credit-tiers" },
      { label: "Lending Types", href: "/lending-types" },
      { label: "Macro Weights", href: "/macro-weights" },
      { label: "Margin Profiles", href: "/margin-profiles" },
      { label: "Property Adjustments", href: "/property-adjustments" },
    ],
  },
];

export default function AdminShell({ children }: { children: ReactNode }) {
  const { role, logout } = useAuth();

  return (
    <div className="gb-shell">
      <aside className="gb-sidebar">
        <a href="/" className="gb-brand" aria-label="GenXBaby Admin home">
          <span className="gb-brand-mark">GX</span>
          <span>
            <span className="gb-brand-name">GenXBaby</span>
            <span className="gb-brand-caption">ADMIN CONTROL CENTER</span>
          </span>
        </a>

        <div className="gb-sidebar-divider" />

        <nav className="gb-nav" aria-label="Admin navigation">
          {navigation.map((group) => (
            <section className="gb-nav-group" key={group.heading}>
              <h2>{group.heading}</h2>
              {group.links.map((link) => (
                <a className="gb-nav-link" href={link.href} key={link.href}>
                  <span className="gb-nav-indicator" />
                  {link.label}
                </a>
              ))}
            </section>
          ))}
        </nav>

        <div className="gb-sidebar-footer">
          <span className="gb-status-dot" />
          <span>Pricing engine workspace</span>
        </div>
      </aside>

      <div className="gb-main-column">
        <header className="gb-topbar">
          <div>
            <p className="gb-eyebrow">GENXBABY / ADMINISTRATION</p>
            <p className="gb-topbar-title">Intelligence & Execution</p>
          </div>
          <div className="gb-topbar-right">
            <span className="gb-environment">
              <span className="gb-status-dot" />
              ENGINE WORKSPACE
            </span>
            <span className="gb-environment">{role}</span>
            <button
              type="button"
              onClick={() => void logout()}
              className="gb-logout-button"
              style={{
                padding: "8px 12px",
                border: "1px solid rgba(255,255,255,.18)",
                borderRadius: 8,
                background: "transparent",
                color: "inherit",
                cursor: "pointer",
              }}
            >
              Sign out
            </button>
          </div>
        </header>

        <nav className="gb-mobile-nav" aria-label="Mobile admin navigation">
          {navigation.flatMap((group) => group.links).map((link) => (
            <a href={link.href} key={link.href}>
              {link.label}
            </a>
          ))}
        </nav>

        <main className="gb-content">
          <div className="gb-content-inner">{children}</div>
        </main>

        <footer className="gb-footer">
          <span>GENXBABY</span>
          <span>Pricing intelligence workspace</span>
        </footer>
      </div>
    </div>
  );
}
