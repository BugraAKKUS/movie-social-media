import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "../generated/client";
import type {
  DuoMatchSession,
  DuoMatchRecommendation,
} from "@cinesocial/shared";

export function useDuoMatch(sessionId?: string) {
  const queryClient = useQueryClient();

  const session = useQuery({
    queryKey: ["duo-match", sessionId],
    queryFn: () =>
      apiClient<DuoMatchSession>(`/api/v1/duo-match/${sessionId}`),
    enabled: !!sessionId,
    refetchInterval: (query) => {
      const state = query.state.data?.state;
      if (state === "analyzing" || state === "pending_partner_consent") {
        return 3000; // Poll every 3s while waiting
      }
      return false;
    },
  });

  const recommendations = useQuery({
    queryKey: ["duo-match", sessionId, "recommendations"],
    queryFn: () =>
      apiClient<DuoMatchRecommendation[]>(
        `/api/v1/duo-match/${sessionId}/recommendations`,
      ),
    enabled: session.data?.state === "recommendations_ready",
  });

  const initiate = useMutation({
    mutationFn: (partnerId: string) =>
      apiClient<DuoMatchSession>("/api/v1/duo-match/initiate", {
        method: "POST",
        body: JSON.stringify({ partnerId }),
      }),
  });

  const consent = useMutation({
    mutationFn: (consentValue: boolean) =>
      apiClient<DuoMatchSession>(`/api/v1/duo-match/${sessionId}/consent`, {
        method: "POST",
        body: JSON.stringify({ consent: consentValue }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["duo-match", sessionId] });
    },
  });

  const revoke = useMutation({
    mutationFn: () =>
      apiClient<DuoMatchSession>(`/api/v1/duo-match/${sessionId}/revoke`, {
        method: "POST",
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["duo-match", sessionId] });
    },
  });

  return { session, recommendations, initiate, consent, revoke };
}
