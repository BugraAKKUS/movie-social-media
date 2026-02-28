import { useQuery, useMutation } from "@tanstack/react-query";
import { apiClient } from "../generated/client";
import type { ChatConversation, Review } from "@cinesocial/shared";

export function useChat() {
  const conversations = useQuery({
    queryKey: ["chat", "conversations"],
    queryFn: () =>
      apiClient<ChatConversation[]>("/api/v1/chat/conversations"),
  });

  const createConversation = useMutation({
    mutationFn: (data: { movieId?: string; title?: string }) =>
      apiClient<ChatConversation>("/api/v1/chat/conversations", {
        method: "POST",
        body: JSON.stringify(data),
      }),
  });

  const publishToFeed = useMutation({
    mutationFn: ({
      conversationId,
      messageId,
      movieId,
    }: {
      conversationId: string;
      messageId: string;
      movieId: string;
    }) =>
      apiClient<Review>(`/api/v1/chat/${conversationId}/publish`, {
        method: "POST",
        body: JSON.stringify({ messageId, movieId }),
      }),
  });

  return { conversations, createConversation, publishToFeed };
}
