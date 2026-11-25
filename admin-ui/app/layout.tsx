import "./globals.css";
import type { Metadata } from "next";
import AdminShell from "../components/layout/AdminShell";
import { AdminGuard, AuthProvider } from "../services/AuthProvider";

export const metadata: Metadata = {
  title: "GenXBaby | Admin Control Center",
  description:
    "GenXBaby pricing intelligence, owner intelligence, and execution workspace.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <AuthProvider>
          <AdminGuard>
            <AdminShell>{children}</AdminShell>
          </AdminGuard>
        </AuthProvider>
      </body>
    </html>
  );
}
