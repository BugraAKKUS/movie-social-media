"use client";

import { useState, useCallback } from "react";

interface GranularRatingProps {
  value?: number;
  onChange: (value: number) => void;
  min?: number;
  max?: number;
  step?: number;
  disabled?: boolean;
}

export function GranularRating({
  value = 5.0,
  onChange,
  min = 0.0,
  max = 10.0,
  step = 0.1,
  disabled = false,
}: GranularRatingProps) {
  const [displayValue, setDisplayValue] = useState(value);

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const newValue = parseFloat(e.target.value);
      setDisplayValue(newValue);
      onChange(newValue);
    },
    [onChange],
  );

  const getColor = (val: number): string => {
    if (val >= 8.0) return "text-green-400";
    if (val >= 6.0) return "text-yellow-400";
    if (val >= 4.0) return "text-orange-400";
    return "text-red-400";
  };

  return (
    <div className="flex items-center gap-4">
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={displayValue}
        onChange={handleChange}
        disabled={disabled}
        className="flex-1 h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-brand-500"
      />
      <span className={`text-2xl font-bold tabular-nums ${getColor(displayValue)}`}>
        {displayValue.toFixed(1)}
      </span>
    </div>
  );
}
