"use client";

import { useState, useRef, useCallback } from "react";
import { VideoReviewCard } from "./VideoReviewCard";
import { SpoilerOverlay } from "./SpoilerOverlay";

interface FeedItem {
  id: string;
  author: { id: string; username: string; avatarUrl?: string };
  movie: { id: string; title: string; posterUrl?: string };
  contentText?: string;
  videoUrl?: string;
  spoiler: { isSpoiler: boolean; score: number; spans: SpoilerSpan[] };
  watchedWith: { id: string; username: string }[];
  rating?: number;
  engagement: { likes: number; comments: number; views: number };
}

interface SpoilerSpan {
  start: number;
  end: number;
  score: number;
  text: string;
}

export function VerticalFeed() {
  const [items, setItems] = useState<FeedItem[]>([]);
  const [cursor, setCursor] = useState<string | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const loadMore = useCallback(async () => {
    // TODO: Fetch from /api/v1/feed?cursor=...
  }, [cursor]);

  if (items.length === 0) {
    return (
      <div className="feed-container flex items-center justify-center">
        <div className="text-center text-gray-400">
          <p className="text-xl mb-2">Your feed is empty</p>
          <p>Follow users and rate movies to get personalized recommendations</p>
        </div>
      </div>
    );
  }

  return (
    <div ref={containerRef} className="feed-container">
      {items.map((item) => (
        <div key={item.id} className="feed-item relative">
          <VideoReviewCard item={item} />
          {item.spoiler.isSpoiler && (
            <SpoilerOverlay spans={item.spoiler.spans} />
          )}
        </div>
      ))}
    </div>
  );
}
