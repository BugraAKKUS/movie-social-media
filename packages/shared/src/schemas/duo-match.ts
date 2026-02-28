import { z } from "zod";
import { DUO_MATCH_STATES } from "../constants/spoiler";

export const DuoMatchSessionSchema = z.object({
  id: z.string().uuid(),
  initiatorId: z.string().uuid(),
  partnerId: z.string().uuid(),
  state: z.enum(DUO_MATCH_STATES),
  initiatorConsentedAt: z.string().datetime().optional(),
  partnerConsentedAt: z.string().datetime().optional(),
  dataExpiryAt: z.string().datetime().optional(),
  recommendationsGeneratedAt: z.string().datetime().optional(),
  createdAt: z.string().datetime(),
});

export const DuoMatchRecommendationSchema = z.object({
  movie: z.object({
    id: z.string().uuid(),
    title: z.string(),
    posterUrl: z.string().url().optional(),
    genres: z.array(z.string()),
  }),
  jointScore: z.number().min(0).max(10),
  compatibilityReason: z.string(),
  user1PredictedRating: z.number().min(0).max(10),
  user2PredictedRating: z.number().min(0).max(10),
});

export const InitiateDuoMatchSchema = z.object({
  partnerId: z.string().uuid(),
});

export const DuoMatchConsentSchema = z.object({
  consent: z.boolean(),
});

export type DuoMatchSession = z.infer<typeof DuoMatchSessionSchema>;
export type DuoMatchRecommendation = z.infer<typeof DuoMatchRecommendationSchema>;
export type InitiateDuoMatch = z.infer<typeof InitiateDuoMatchSchema>;
export type DuoMatchConsent = z.infer<typeof DuoMatchConsentSchema>;
