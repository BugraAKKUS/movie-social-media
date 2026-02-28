"use client";

import { useState, useRef, useEffect } from "react";
import { MessageBubble } from "./MessageBubble";
import { PublishToFeedButton } from "./PublishToFeedButton";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  ragSources?: { movieId: string; title: string; score: number }[];
  publishedReviewId?: string;
}

interface ChatWindowProps {
  conversationId: string;
  movieId?: string;
}

export function ChatWindow({ conversationId, movieId }: ChatWindowProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    // TODO: Connect WebSocket to /api/v1/chat/ws/{conversationId}
    return () => wsRef.current?.close();
  }, [conversationId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = () => {
    if (!input.trim() || !wsRef.current) return;

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: input,
    };
    setMessages((prev) => [...prev, userMessage]);
    wsRef.current.send(JSON.stringify({ type: "message", content: input }));
    setInput("");
    setIsTyping(true);
  };

  return (
    <div className="flex flex-col h-full bg-gray-950">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-800 flex items-center gap-3">
        <div className="w-8 h-8 bg-brand-600 rounded-full flex items-center justify-center text-sm font-bold">
          AI
        </div>
        <div>
          <p className="font-semibold">Film Companion</p>
          <p className="text-xs text-gray-500">AI-powered film discussions</p>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => (
          <div key={msg.id}>
            <MessageBubble message={msg} />
            {msg.role === "assistant" && !msg.publishedReviewId && (
              <PublishToFeedButton
                conversationId={conversationId}
                messageId={msg.id}
                movieId={movieId}
              />
            )}
          </div>
        ))}
        {isTyping && (
          <div className="flex items-center gap-2 text-gray-500">
            <div className="flex gap-1">
              <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" />
              <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce [animation-delay:150ms]" />
              <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce [animation-delay:300ms]" />
            </div>
            <span className="text-sm">Thinking...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-800">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            placeholder="Ask about any film..."
            className="flex-1 px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-brand-500"
          />
          <button
            onClick={sendMessage}
            className="px-4 py-2 bg-brand-600 rounded-lg hover:bg-brand-700 transition-colors"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
