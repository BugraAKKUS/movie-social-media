/** 10-point granular rating system constants */
export const RATING = {
  MIN: 0.0,
  MAX: 10.0,
  STEP: 0.1,
  /** Decimal places for display */
  PRECISION: 1,
} as const;

/** Rating color thresholds */
export const RATING_COLORS = {
  EXCELLENT: { min: 8.0, color: "green" },
  GOOD: { min: 6.0, color: "yellow" },
  AVERAGE: { min: 4.0, color: "orange" },
  POOR: { min: 0.0, color: "red" },
} as const;
