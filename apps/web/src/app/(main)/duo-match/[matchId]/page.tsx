"use client";

import { use, useState } from "react";
import { ConsentFlow } from "@/components/duo-match/ConsentFlow";
import { MatchResults } from "@/components/duo-match/MatchResults";

export default function DuoMatchPage({
  params,
}: {
  params: Promise<{ matchId: string }>;
}) {
  const { matchId } = use(params);

  // TODO: Fetch session state from /api/v1/duo-match/{matchId}

  return (
    <main className="min-h-screen p-8 max-w-xl mx-auto">
      <h1 className="text-2xl font-bold text-center mb-6">Duo-Match</h1>
      <p className="text-center text-gray-400 mb-8">
        Find movies you&apos;ll both love, powered by AI
      </p>
      {/* ConsentFlow or MatchResults rendered based on session state */}
    </main>
  );
}
