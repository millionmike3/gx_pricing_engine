"use client";

import { useState } from "react";
import { API } from "@/lib/api";

export function useAdminAPI() {
  const [result, setResult] = useState(null);

  async function runScenario() {
    const res = await fetch(`${API.admin}/test-scenario`, {
      method: "POST",
    });

    setResult(await res.json());
  }

  return { result, runScenario };
}
