"use client";

import { useState } from "react";

type SessionState =
  | "pending_partner_consent"
  | "both_consented"
  | "analyzing"
  | "recommendations_ready"
  | "viewed"
  | "expired"
  | "declined"
  | "revoked";

interface ConsentFlowProps {
  sessionId: string;
  partnerUsername: string;
  currentState: SessionState;
  isInitiator: boolean;
  onConsent: (consent: boolean) => void;
  onRevoke: () => void;
}

export function ConsentFlow({
  sessionId,
  partnerUsername,
  currentState,
  isInitiator,
  onConsent,
  onRevoke,
}: ConsentFlowProps) {
  const [showDetails, setShowDetails] = useState(false);

  if (currentState === "declined") {
    return (
      <div className="p-6 bg-gray-900 rounded-xl text-center">
        <p className="text-gray-400">This Duo-Match was declined.</p>
      </div>
    );
  }

  if (currentState === "revoked" || currentState === "expired") {
    return (
      <div className="p-6 bg-gray-900 rounded-xl text-center">
        <p className="text-gray-400">
          This session has {currentState === "revoked" ? "been revoked" : "expired"}.
          All temporary data has been deleted.
        </p>
      </div>
    );
  }

  if (currentState === "pending_partner_consent" && !isInitiator) {
    return (
      <div className="p-6 bg-gray-900 rounded-xl space-y-4">
        <h3 className="text-lg font-bold">Duo-Match Request</h3>
        <p className="text-gray-300">
          @{partnerUsername} wants to find movies you&apos;d both enjoy. The AI
          will analyze your shared chat history to generate recommendations.
        </p>

        <button
          onClick={() => setShowDetails(!showDetails)}
          className="text-sm text-brand-500 underline"
        >
          {showDetails ? "Hide" : "What data is processed?"}
        </button>

        {showDetails && (
          <div className="p-4 bg-gray-800 rounded-lg text-sm space-y-2">
            <p className="text-gray-300">The AI will:</p>
            <ul className="list-disc pl-5 text-gray-400 space-y-1">
              <li>Extract genre preferences and mood keywords from your DMs</li>
              <li>Identify movies mentioned in conversation</li>
              <li>Compare your rating histories</li>
            </ul>
            <p className="text-gray-300 mt-2">Privacy guarantees:</p>
            <ul className="list-disc pl-5 text-gray-400 space-y-1">
              <li>Raw messages are never stored — only preference signals</li>
              <li>All temporary data auto-deletes within 24 hours</li>
              <li>You can revoke consent at any time</li>
            </ul>
          </div>
        )}

        <div className="flex gap-3">
          <button
            onClick={() => onConsent(true)}
            className="flex-1 py-3 bg-brand-600 rounded-lg hover:bg-brand-700 transition-colors"
          >
            Allow Analysis
          </button>
          <button
            onClick={() => onConsent(false)}
            className="flex-1 py-3 border border-gray-700 rounded-lg hover:bg-gray-800 transition-colors"
          >
            Decline
          </button>
        </div>
      </div>
    );
  }

  if (currentState === "pending_partner_consent" && isInitiator) {
    return (
      <div className="p-6 bg-gray-900 rounded-xl text-center space-y-3">
        <div className="animate-pulse text-brand-500 text-3xl">&#9679;</div>
        <p>Waiting for @{partnerUsername} to accept...</p>
        <button onClick={onRevoke} className="text-sm text-gray-500 hover:text-red-400">
          Cancel Request
        </button>
      </div>
    );
  }

  if (currentState === "analyzing") {
    return (
      <div className="p-6 bg-gray-900 rounded-xl text-center space-y-3">
        <div className="animate-spin w-8 h-8 border-2 border-brand-500 border-t-transparent rounded-full mx-auto" />
        <p>Analyzing your shared preferences...</p>
        <p className="text-xs text-gray-500">This usually takes a few seconds</p>
        <button onClick={onRevoke} className="text-sm text-gray-500 hover:text-red-400">
          Revoke Consent
        </button>
      </div>
    );
  }

  return null;
}
