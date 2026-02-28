import React from "react";

interface WatchedWithTagProps {
  username: string;
  confirmed?: boolean;
  onClick?: () => void;
}

export function WatchedWithTag({
  username,
  confirmed = false,
  onClick,
}: WatchedWithTagProps) {
  return (
    <button
      onClick={onClick}
      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs ${
        confirmed
          ? "bg-brand-900/30 text-brand-400 border border-brand-800"
          : "bg-gray-800 text-gray-400 border border-gray-700"
      }`}
    >
      <span>@{username}</span>
      {!confirmed && <span className="text-gray-600">(pending)</span>}
    </button>
  );
}
