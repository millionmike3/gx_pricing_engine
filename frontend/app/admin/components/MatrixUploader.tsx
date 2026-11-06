"use client";

import { useState } from "react";
import { API } from "@/lib/api";

export default function MatrixUploader() {
  const [file, setFile] = useState<File | null>(null);

  async function upload() {
    if (!file) return;

    const form = new FormData();
    form.append("file", file);

    await fetch(`${API.admin}/matrix/upload`, {
      method: "POST",
      body: form,
    });

    alert("Matrix uploaded!");
  }

  return (
    <div className="p-4 border rounded-lg space-y-4">
      <input
        type="file"
        onChange={(e) => setFile(e.target.files?.[0] || null)}
      />
      <button
        onClick={upload}
        className="bg-blue-600 text-white px-4 py-2 rounded"
      >
        Upload Matrix
      </button>
    </div>
  );
}
