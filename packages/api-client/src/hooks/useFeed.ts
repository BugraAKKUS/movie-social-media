import { useInfiniteQuery } from "@tanstack/react-query";
import { apiClient } from "../generated/client";

interface FeedResponse {
  items: unknown[];
  nextCursor: string | null;
}

export function useFeed(type: "algorithmic" | "chronological" = "algorithmic") {
  return useInfiniteQuery({
    queryKey: ["feed", type],
    queryFn: async ({ pageParam }) => {
      const params = new URLSearchParams({ type, limit: "20" });
      if (pageParam) params.set("cursor", pageParam);
      return apiClient<FeedResponse>(`/api/v1/feed?${params}`);
    },
    initialPageParam: null as string | null,
    getNextPageParam: (lastPage) => lastPage.nextCursor,
  });
}
