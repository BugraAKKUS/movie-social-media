import { z } from "zod";

export const SpoilerSpanSchema = z.object({
  start: z.number().int().min(0),
  end: z.number().int().min(0),
  score: z.number().min(0).max(1),
  text: z.string(),
});

export const ReviewSchema = z.object({
  id: z.string().uuid(),
  userId: z.string().uuid(),
  movieId: z.string().uuid(),
  ratingId: z.string().uuid().optional(),
  contentText: z.string().optional(),
  videoUrl: z.string().url().optional(),
  videoThumbnail: z.string().url().optional(),
  spoilerScore: z.number().min(0).max(1),
  isSpoiler: z.boolean(),
  spoilerSpans: z.array(SpoilerSpanSchema),
  publishedFromChat: z.boolean(),
  likeCount: z.number().int().min(0),
  commentCount: z.number().int().min(0),
  viewCount: z.number().int().min(0),
  createdAt: z.string().datetime(),
});

export const CreateReviewSchema = z.object({
  movieId: z.string().uuid(),
  contentText: z.string().optional(),
  videoUrl: z.string().url().optional(),
  watchedWithUserIds: z.array(z.string().uuid()).optional(),
});

export type SpoilerSpan = z.infer<typeof SpoilerSpanSchema>;
export type Review = z.infer<typeof ReviewSchema>;
export type CreateReview = z.infer<typeof CreateReviewSchema>;
