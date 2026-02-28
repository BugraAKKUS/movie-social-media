/** Spoiler detection thresholds */
export const SPOILER = {
  /** Minimum sequence-level probability to flag as spoiler */
  SEQUENCE_THRESHOLD: 0.7,
  /** Minimum per-token probability for span detection */
  TOKEN_THRESHOLD: 0.5,
  /** Minimum character length for a spoiler span */
  MIN_SPAN_LENGTH: 3,
} as const;

/** Duo-Match session states */
export const DUO_MATCH_STATES = [
  "pending_partner_consent",
  "both_consented",
  "analyzing",
  "recommendations_ready",
  "viewed",
  "expired",
  "declined",
  "revoked",
] as const;

export type DuoMatchState = (typeof DUO_MATCH_STATES)[number];
