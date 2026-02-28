"use client";

import { use } from "react";
import { ChatWindow } from "@/components/chat/ChatWindow";

export default function ChatPage({
  params,
}: {
  params: Promise<{ conversationId: string }>;
}) {
  const { conversationId } = use(params);

  return (
    <main className="h-screen">
      <ChatWindow conversationId={conversationId} />
    </main>
  );
}
