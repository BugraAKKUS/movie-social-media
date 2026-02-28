"use client";

import { use } from "react";
import { GranularRating } from "@/components/rating/GranularRating";

export default function MoviePage({
  params,
}: {
  params: Promise<{ movieId: string }>;
}) {
  const { movieId } = use(params);

  return (
    <main className="min-h-screen p-8 max-w-2xl mx-auto space-y-6">
      {/* Movie header */}
      <div className="flex gap-6">
        <div className="w-48 h-72 bg-gray-800 rounded-xl flex-shrink-0" />
        <div className="space-y-3">
          <h1 className="text-3xl font-bold">Loading...</h1>
          <p className="text-gray-400">2024 &middot; 120 min</p>
          <div className="flex gap-2">
            <span className="px-3 py-1 bg-gray-800 rounded-full text-sm">Genre</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-3xl font-bold text-brand-500">0.0</span>
            <span className="text-gray-400">/10 (0 ratings)</span>
          </div>
        </div>
      </div>

      {/* Your rating */}
      <div className="bg-gray-900 p-4 rounded-xl space-y-3">
        <h2 className="font-bold">Your Rating</h2>
        <GranularRating
          value={5.0}
          onChange={(val) => {
            // TODO: POST /api/v1/ratings
          }}
        />
      </div>

      {/* Overview */}
      <div>
        <h2 className="font-bold mb-2">Overview</h2>
        <p className="text-gray-400">Loading...</p>
      </div>

      {/* Reviews */}
      <div>
        <h2 className="font-bold mb-3">Reviews</h2>
        <p className="text-gray-500">No reviews yet</p>
      </div>
    </main>
  );
}
