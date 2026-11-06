"use client";

export default function Button({ children, ...props }: any) {
  return (
    <button
      {...props}
      className="
        gx-btn
        px-4 py-2
        rounded-full
        font-semibold
        transition
      "
    >
      {children}
    </button>
  );
}
