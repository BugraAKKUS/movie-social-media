"use client";

import { useState } from "react";

interface PublishToFeedButtonProps {
  conversationId: string;
  messageId: string;
  movieId?: string;
}

export function PublishToFeedButton({
  conversationId,
  messageId,
  movieId,
}: PublishToFeedButtonProps) {
  const [isPublished, setIsPublished] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handlePublish = async () => {
    if (!movieId) return;
    setIsLoading(true);
    try {
      // TODO: POST /api/v1/chat/{conversationId}/publish
      setIsPublished(true);
    } catch {
      // TODO: Error handling
    } finally {
      setIsLoading(false);
    }
  };

  if (isPublished) {
    return (
      <span className="text-xs text-green-400 ml-12 mt-1 block">
        Published to feed
      </span>
    );
  }

  return (
    <button
      onClick={handlePublish}
      disabled={isLoading || !movieId}
      className="text-xs text-gray-500 hover:text-brand-500 ml-12 mt-1 transition-colors disabled:opacity-50"
    >
      {isLoading ? "Publishing..." : "Publish to Feed"}
    </button>
  );
}
