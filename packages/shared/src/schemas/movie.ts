import { z } from "zod";

export const MovieSchema = z.object({
  id: z.string().uuid(),
  tmdbId: z.number().int().optional(),
  title: z.string().min(1).max(500),
  originalTitle: z.string().max(500).optional(),
  overview: z.string().optional(),
  releaseDate: z.string().optional(),
  runtimeMinutes: z.number().int().positive().optional(),
  posterUrl: z.string().url().optional(),
  backdropUrl: z.string().url().optional(),
  genres: z.array(z.string()),
  keywords: z.array(z.string()),
  director: z.string().optional(),
  avgRating: z.number().min(0).max(10),
  ratingCount: z.number().int().min(0),
});

export const MovieSummarySchema = z.object({
  id: z.string().uuid(),
  title: z.string(),
  posterUrl: z.string().url().optional(),
  genres: z.array(z.string()),
  avgRating: z.number(),
  ratingCount: z.number(),
});

export type Movie = z.infer<typeof MovieSchema>;
export type MovieSummary = z.infer<typeof MovieSummarySchema>;
