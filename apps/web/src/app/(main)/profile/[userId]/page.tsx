"use client";

import { use } from "react";

export default function ProfilePage({
  params,
}: {
  params: Promise<{ userId: string }>;
}) {
  const { userId } = use(params);

  return (
    <main className="min-h-screen p-8 max-w-2xl mx-auto">
      <div className="space-y-6">
        {/* Profile header */}
        <div className="flex items-center gap-4">
          <div className="w-20 h-20 bg-gray-700 rounded-full" />
          <div>
            <h1 className="text-2xl font-bold">Loading...</h1>
            <p className="text-gray-400">@username</p>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 text-center">
          <div className="bg-gray-900 p-4 rounded-xl">
            <p className="text-2xl font-bold">0</p>
            <p className="text-sm text-gray-400">Reviews</p>
          </div>
          <div className="bg-gray-900 p-4 rounded-xl">
            <p className="text-2xl font-bold">0</p>
            <p className="text-sm text-gray-400">Ratings</p>
          </div>
          <div className="bg-gray-900 p-4 rounded-xl">
            <p className="text-2xl font-bold">0</p>
            <p className="text-sm text-gray-400">Watched With</p>
          </div>
        </div>

        {/* Recent ratings */}
        <div>
          <h2 className="text-lg font-bold mb-3">Recent Ratings</h2>
          <p className="text-gray-500">No ratings yet</p>
        </div>
      </div>
    </main>
  );
}
