"use client";

import { useState } from "react";
import { API } from "@/lib/api";

let globalState: any = {
  loading: false,
  result: null,
};

export function usePricingEngine() {
  const [loading, setLoading] = useState(globalState.loading);
  const [result, setResult] = useState(globalState.result);

  async function getQuote(payload: any) {
    setLoading(true);
    globalState.loading = true;

    const res = await fetch(`${API.pricing}/quote/compare`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await res.json();
    setResult(data);
    globalState.result = data;

    setLoading(false);
    globalState.loading = false;
  }

  return { loading, result, getQuote };
}
