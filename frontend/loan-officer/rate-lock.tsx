"use client";

import React, { useEffect, useState } from "react";
import axios, { AxiosResponse } from "axios";

interface RateLock {
  locked_rate: number;
  locked_at: string;
  expires_at: string;
}

export default function LoanOfficerRateLockPage({
  params,
}: {
  params: { loanId: string };
}) {
  const [lock, setLock] = useState<RateLock | null>(null);
  const [finalRate, setFinalRate] = useState<number>(6.25);

  useEffect(() => {
    axios
      .get<RateLock>(
        `${process.env.NEXT_PUBLIC_API_URL}/loan-officers/rate-lock/${params.loanId}`
      )
      .then((res: AxiosResponse<RateLock>) => {
        setLock(res.data);
      })
      .catch(() => setLock(null));
  }, [params.loanId]);

  const lockRate = async () => {
    const res: AxiosResponse<RateLock> = await axios.post(
      `${process.env.NEXT_PUBLIC_API_URL}/loan-officers/rate-lock/${params.loanId}`,
      { finalRate }
    );
    setLock(res.data);
  };

  return (
    <div className="p-6 bg-[#050505] min-h-screen text-white">
      <h1 className="text-2xl font-bold mb-4">Loan Officer Rate Lock</h1>

      <div className="mb-4">
        <label className="text-sm text-gray-400">Final Rate</label>
        <input
          type="number"
          step="0.001"
          value={finalRate}
          onChange={e => setFinalRate(Number(e.target.value))}
          className="mt-1 p-2 bg-black border border-white/10 rounded-lg text-white"
        />
      </div>

      <button
        onClick={lockRate}
        className="px-4 py-2 bg-[#3CF46B] text-black font-bold rounded-lg"
      >
        Lock Rate
      </button>

      {lock && (
        <div className="mt-4 p-4 bg-black border border-white/10 rounded-lg">
          <div className="text-sm text-gray-400">Locked Rate</div>
          <div className="text-xl font-bold">{lock.locked_rate.toFixed(3)}%</div>

          <div className="mt-2 text-sm text-gray-400">Locked At</div>
          <div>{new Date(lock.locked_at).toLocaleString()}</div>

          <div className="mt-2 text-sm text-gray-400">Expires At</div>
          <div>{new Date(lock.expires_at).toLocaleString()}</div>
        </div>
      )}
    </div>
  );
}
