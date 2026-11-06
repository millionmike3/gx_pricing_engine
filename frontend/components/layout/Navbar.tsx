"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Navbar() {
  const pathname = usePathname();

  const navItems = [
    { name: "Home | ", href: "/" },
    { name: "Pricing |   ", href: "/pricing" },
    { name: "Admin |  ", href: "/admin" },
    { name: "Investor |   ", href: "/investor" },
    { name: "Borrower", href: "/borrower" },
  ];

  return (
    <nav className="w-full bg-gx-bg-light border-b border-gx-border px-6 py-4 shadow-lg">
      <div className="flex items-center justify-between">

        {/* Navigation Buttons */}
        <div className="flex items-center gap-10 whitespace-nowrap">

          {navItems.map((item) => {
            const isActive = pathname === item.href;

            return (
              <Link
                key={item.href}
                href={item.href}
                className={`
                  px-4 py-2 rounded-full font-semibold transition-transform
                  hover:scale-105
                  ${isActive
                    ? "bg-gradient-to-r from-violet-500 to-blue-600 text-white shadow-md"
                    : "bg-gradient-to-r from-purple-600 to-indigo-700 text-white opacity-80 hover:opacity-100"}
                `}
              >
                {item.name}
              </Link>
            );
          })}

        </div>
      </div>
    </nav>
  );
}
