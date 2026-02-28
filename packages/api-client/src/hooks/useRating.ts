import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "../generated/client";
import type { Rating, MovieRatingAggregate } from "@cinesocial/shared";

export function useRating(movieId: string) {
  const queryClient = useQueryClient();

  const aggregate = useQuery({
    queryKey: ["ratings", "movie", movieId],
    queryFn: () =>
      apiClient<MovieRatingAggregate>(`/api/v1/ratings/movie/${movieId}`),
  });

  const submitRating = useMutation({
    mutationFn: (score: number) =>
      apiClient<Rating>("/api/v1/ratings", {
        method: "POST",
        body: JSON.stringify({ movieId, score }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["ratings", "movie", movieId] });
    },
  });

  return { aggregate, submitRating };
}
