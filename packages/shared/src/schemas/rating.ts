import { z } from "zod";
import { RATING } from "../constants/rating";

export const RatingSchema = z.object({
  id: z.string().uuid(),
  userId: z.string().uuid(),
  movieId: z.string().uuid(),
  score: z.number().min(RATING.MIN).max(RATING.MAX).multipleOf(RATING.STEP),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
});

export const CreateRatingSchema = z.object({
  movieId: z.string().uuid(),
  score: z.number().min(RATING.MIN).max(RATING.MAX).multipleOf(RATING.STEP),
});

export const MovieRatingAggregateSchema = z.object({
  avgScore: z.number().min(0).max(10),
  count: z.number().int().min(0),
  userRating: z.number().optional(),
});

export type Rating = z.infer<typeof RatingSchema>;
export type CreateRating = z.infer<typeof CreateRatingSchema>;
export type MovieRatingAggregate = z.infer<typeof MovieRatingAggregateSchema>;
