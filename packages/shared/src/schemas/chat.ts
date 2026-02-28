import { z } from "zod";

export const ChatMessageSchema = z.object({
  id: z.string().uuid(),
  conversationId: z.string().uuid(),
  role: z.enum(["user", "assistant", "system"]),
  content: z.string(),
  ragSources: z.array(
    z.object({
      movieId: z.string().uuid(),
      title: z.string(),
      score: z.number(),
    }),
  ),
  publishedReviewId: z.string().uuid().optional(),
  createdAt: z.string().datetime(),
});

export const ChatConversationSchema = z.object({
  id: z.string().uuid(),
  userId: z.string().uuid(),
  movieId: z.string().uuid().optional(),
  title: z.string().optional(),
  createdAt: z.string().datetime(),
});

export const PublishChatSchema = z.object({
  messageId: z.string().uuid(),
  movieId: z.string().uuid(),
});

export type ChatMessage = z.infer<typeof ChatMessageSchema>;
export type ChatConversation = z.infer<typeof ChatConversationSchema>;
export type PublishChat = z.infer<typeof PublishChatSchema>;
