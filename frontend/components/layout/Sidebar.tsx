import Link from "next/link";

export default function Sidebar() {
  return (
    <aside className="w-64 h-screen border-r border-gx-border bg-gx-bg-light p-6 flex flex-col gap-4">
      
      <h1 className="text-xl font-bold text-gx-accent-blue mb-4">
        GX Pricing Engine
      </h1>

      {/* Remove navigation here */}
      <p className="text-gray-400 text-sm">
        Unified Pricing & Underwriting OS
      </p>

    </aside>
  );
}
