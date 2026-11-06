import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "GenXBaby Admin",
  description: "Administrative dashboard for pricing, intelligence, and execution.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="bg-[#050505] text-white min-h-screen">
        <div className="flex min-h-screen">
          {/* Sidebar */}
          <aside className="w-64 bg-black border-r border-white/10 p-4">
            <div className="text-xl font-bold mb-6">GenXBaby Admin</div>

            <nav className="space-y-2 text-sm">
              {/* Owner Intelligence */}
              <a href="/owners/revenue" className="block hover:text-[#3CF46B]">
                Owner Revenue
              </a>
              <a href="/owners/fraud" className="block hover:text-[#3CF46B]">
                Fraud Intelligence
              </a>
              <a href="/owners/behavior" className="block hover:text-[#3CF46B]">
                Behavioral Intelligence
              </a>
              <a href="/owners/execution" className="block hover:text-[#3CF46B]">
                Secondary‑Market Execution
              </a>

              {/* Pricing Intelligence */}
              <a
                href="/pricing/base-rates"
                className="block hover:text-[#3CF46B]"
              >
                Base Rate Editor
              </a>
              <a
                href="/pricing/investor-sheets"
                className="block hover:text-[#3CF46B]"
              >
                Investor Rate Sheets
              </a>
              <a href="/pricing/overlays" className="block hover:text-[#3CF46B]">
                Pricing Overlays
              </a>
              <a href="/pricing/margins" className="block hover:text-[#3CF46B]">
                Margin Controls
              </a>
              <a
                href="/pricing/exceptions"
                className="block hover:text-[#3CF46B]"
              >
                Pricing Exceptions
              </a>
              <a
                href="/pricing/audit-log"
                className="block hover:text-[#3CF46B]"
              >
                Pricing Audit Log
              </a>
            </nav>
          </aside>

          {/* Main Content */}
          <main className="flex-1">
            <div className="max-w-6xl mx-auto p-6">{children}</div>
          </main>
        </div>
      </body>
    </html>
  );
}
