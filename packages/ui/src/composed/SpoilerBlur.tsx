"use client";

import React, { useState } from "react";

interface SpoilerBlurProps {
  children: React.ReactNode;
  isSpoiler: boolean;
  label?: string;
}

export function SpoilerBlur({
  children,
  isSpoiler,
  label = "Spoiler Warning — Tap to Reveal",
}: SpoilerBlurProps) {
  const [revealed, setRevealed] = useState(false);

  if (!isSpoiler || revealed) {
    return <>{children}</>;
  }

  return (
    <div className="relative">
      <div className="blur-lg select-none pointer-events-none">{children}</div>
      <button
        onClick={() => setRevealed(true)}
        className="absolute inset-0 flex items-center justify-center bg-black/40 backdrop-blur-sm"
      >
        <span className="px-4 py-2 border border-gray-500 rounded-full text-sm text-white">
          {label}
        </span>
      </button>
    </div>
  );
}
