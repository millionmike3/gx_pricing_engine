import "./globals.css";

export default function InvestorLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-[#050505] text-white">
        <header className="p-4 border-b border-white/10 flex justify-between">
          <div className="font-bold">GenXBaby Investor Portal</div>
        </header>
        <main className="p-6">{children}</main>
      </body>
    </html>
  );
}
