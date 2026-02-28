"use client";

import { useState } from "react";

interface SpoilerSpan {
  start: number;
  end: number;
  score: number;
  text: string;
}

interface SpoilerOverlayProps {
  spans: SpoilerSpan[];
}

export function SpoilerOverlay({ spans }: SpoilerOverlayProps) {
  const [revealed, setRevealed] = useState(false);

  if (revealed || spans.length === 0) return null;

  return (
    <div className="absolute inset-0 z-20 flex items-center justify-center backdrop-blur-xl bg-black/60">
      <div className="text-center space-y-4">
        <div className="text-4xl">&#9888;</div>
        <p className="text-xl font-bold">Spoiler Warning</p>
        <p className="text-sm text-gray-400 max-w-xs">
          This review contains potential spoilers ({spans.length} section
          {spans.length > 1 ? "s" : ""} detected)
        </p>
        <button
          onClick={() => setRevealed(true)}
          className="px-6 py-2 border border-gray-600 rounded-full hover:bg-gray-800 transition-colors"
        >
          Tap to Reveal
        </button>
      </div>
    </div>
  );
}
