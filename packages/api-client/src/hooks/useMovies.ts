import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../generated/client";
import type { Movie } from "@cinesocial/shared";

export function useMovies(query?: string) {
  return useQuery({
    queryKey: ["movies", query],
    queryFn: () => {
      const params = new URLSearchParams();
      if (query) params.set("q", query);
      return apiClient<Movie[]>(`/api/v1/movies?${params}`);
    },
  });
}

export function useMovie(movieId: string) {
  return useQuery({
    queryKey: ["movies", movieId],
    queryFn: () => apiClient<Movie>(`/api/v1/movies/${movieId}`),
    enabled: !!movieId,
  });
}
