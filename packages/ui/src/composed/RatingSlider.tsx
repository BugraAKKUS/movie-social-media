"use client";

import React, { useState, useCallback } from "react";

interface RatingSliderProps {
  value?: number;
  onChange: (value: number) => void;
  disabled?: boolean;
  showLabel?: boolean;
}

export function RatingSlider({
  value = 5.0,
  onChange,
  disabled = false,
  showLabel = true,
}: RatingSliderProps) {
  const [current, setCurrent] = useState(value);

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const newVal = parseFloat(e.target.value);
      setCurrent(newVal);
      onChange(newVal);
    },
    [onChange],
  );

  const getLabel = (val: number): string => {
    if (val >= 9.0) return "Masterpiece";
    if (val >= 8.0) return "Excellent";
    if (val >= 7.0) return "Great";
    if (val >= 6.0) return "Good";
    if (val >= 5.0) return "Average";
    if (val >= 4.0) return "Below Average";
    if (val >= 3.0) return "Poor";
    return "Terrible";
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <input
          type="range"
          min={0}
          max={10}
          step={0.1}
          value={current}
          onChange={handleChange}
          disabled={disabled}
          className="flex-1 mr-4"
        />
        <span className="text-2xl font-bold tabular-nums min-w-[4ch] text-right">
          {current.toFixed(1)}
        </span>
      </div>
      {showLabel && (
        <p className="text-sm text-gray-400 text-center">{getLabel(current)}</p>
      )}
    </div>
  );
}
