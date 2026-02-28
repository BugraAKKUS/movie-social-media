"use client";

interface MessageBubbleProps {
  message: {
    id: string;
    role: "user" | "assistant";
    content: string;
    ragSources?: { movieId: string; title: string; score: number }[];
  };
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[80%] px-4 py-3 rounded-2xl ${
          isUser
            ? "bg-brand-600 text-white rounded-br-sm"
            : "bg-gray-800 text-gray-100 rounded-bl-sm"
        }`}
      >
        <p className="text-sm whitespace-pre-wrap">{message.content}</p>

        {/* RAG source references */}
        {message.ragSources && message.ragSources.length > 0 && (
          <div className="mt-2 pt-2 border-t border-gray-700 space-y-1">
            <p className="text-xs text-gray-400">Referenced:</p>
            {message.ragSources.map((source) => (
              <p key={source.movieId} className="text-xs text-gray-500">
                {source.title} (relevance: {(source.score * 100).toFixed(0)}%)
              </p>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
