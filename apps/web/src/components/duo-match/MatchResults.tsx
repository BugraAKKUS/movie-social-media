"use client";

interface Recommendation {
  movie: { id: string; title: string; posterUrl?: string; genres: string[] };
  jointScore: number;
  compatibilityReason: string;
  user1PredictedRating: number;
  user2PredictedRating: number;
}

interface MatchResultsProps {
  recommendations: Recommendation[];
  user1Username: string;
  user2Username: string;
  onRevoke: () => void;
}

export function MatchResults({
  recommendations,
  user1Username,
  user2Username,
  onRevoke,
}: MatchResultsProps) {
  return (
    <div className="p-6 space-y-6">
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold">Your Duo-Match Results</h2>
        <p className="text-gray-400">
          Movies @{user1Username} and @{user2Username} would both enjoy
        </p>
      </div>

      <div className="space-y-4">
        {recommendations.map((rec, idx) => (
          <div
            key={rec.movie.id}
            className="bg-gray-900 rounded-xl p-4 flex gap-4"
          >
            <div className="text-2xl font-bold text-gray-600 w-8">
              {idx + 1}
            </div>

            {/* Poster placeholder */}
            <div className="w-16 h-24 bg-gray-800 rounded-lg flex-shrink-0" />

            <div className="flex-1 space-y-2">
              <div className="flex items-center gap-2">
                <h3 className="font-bold">{rec.movie.title}</h3>
                <span className="px-2 py-0.5 bg-green-900/50 text-green-400 rounded-full text-xs font-bold">
                  {rec.jointScore.toFixed(1)} match
                </span>
              </div>

              <p className="text-sm text-gray-400">
                {rec.compatibilityReason}
              </p>

              <div className="flex gap-4 text-xs text-gray-500">
                <span>
                  @{user1Username}: {rec.user1PredictedRating.toFixed(1)}/10
                </span>
                <span>
                  @{user2Username}: {rec.user2PredictedRating.toFixed(1)}/10
                </span>
              </div>

              <div className="flex gap-1">
                {rec.movie.genres.map((g) => (
                  <span
                    key={g}
                    className="px-2 py-0.5 bg-gray-800 rounded-full text-xs text-gray-400"
                  >
                    {g}
                  </span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="text-center space-y-2">
        <p className="text-xs text-gray-600">
          Results expire in 24 hours. All temporary data will be deleted.
        </p>
        <button
          onClick={onRevoke}
          className="text-sm text-gray-500 hover:text-red-400 transition-colors"
        >
          Revoke Consent &amp; Delete Data Now
        </button>
      </div>
    </div>
  );
}
