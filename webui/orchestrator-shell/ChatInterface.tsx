import React, { useState } from "react";

interface Intent {
    id: number;
    text: string;
    createdAt: string;
}

interface ChatInterfaceProps {
    onTileCommand?: (tileId: string) => void;
}

export default function ChatInterface({ onTileCommand }: ChatInterfaceProps) {
    const [intentText, setIntentText] = useState("");
    const [intents, setIntents] = useState<Intent[]>([]);

    function addIntent(event: React.FormEvent) {
        event.preventDefault();
        const trimmed = intentText.trim();
        if (!trimmed) return;
        const now = new Date().toISOString();
        setIntents((prev) => [
            { id: prev.length + 1, text: trimmed, createdAt: now },
            ...prev,
        ]);
        setIntentText("");

        // Simple intent parsing for tile commands (future: more sophisticated)
        const lowerText = trimmed.toLowerCase();
        if (onTileCommand) {
            if (lowerText.includes("db") || lowerText.includes("database")) {
                onTileCommand("db");
            } else if (lowerText.includes("lm") || lowerText.includes("model")) {
                onTileCommand("lm");
            } else if (lowerText.includes("system")) {
                onTileCommand("system");
            } else if (lowerText.includes("graph")) {
                onTileCommand("graph");
            } else if (lowerText.includes("docs")) {
                onTileCommand("docs");
            }
        }
    }

    return (
        <div className="chat-interface">
            <div className="max-w-4xl">
                <div className="mb-3">
                    <h2 className="text-lg font-semibold text-white mb-1">Orchestrator Chat</h2>
                    <p className="text-sm text-gray-300">
                        Describe what you want, and the system adapts. This is local-only in v1.
                    </p>
                </div>
                <form onSubmit={addIntent} className="mb-4">
                    <div className="flex gap-2">
                        <textarea
                            value={intentText}
                            onChange={(e) => setIntentText(e.target.value)}
                            placeholder="Example: Show me what my models and docs are doing."
                            rows={2}
                            aria-label="Orchestrator intent input"
                        />
                        <button
                            type="submit"
                            aria-label="Submit intent"
                        >
                            Send
                        </button>
                    </div>
                </form>

                {intents.length > 0 && (
                    <div className="intent-log max-h-32 overflow-y-auto mt-4">
                        <h3 className="text-sm font-semibold text-gray-300 mb-2">Recent Intents</h3>
                        <ul className="space-y-1">
                            {intents.slice(0, 3).map((i) => (
                                <li
                                    key={i.id}
                                    className="text-sm text-gray-200 border-l-2 border-blue-400 pl-3 py-1 bg-white/5 rounded mb-1"
                                >
                                    <time
                                        dateTime={i.createdAt}
                                        className="text-gray-400 text-xs block mb-1"
                                    >
                                        {new Date(i.createdAt).toLocaleTimeString()}
                                    </time>
                                    {i.text}
                                </li>
                            ))}
                        </ul>
                    </div>
                )}

                <div className="mt-3 text-xs text-gray-400 bg-white/5 border border-white/10 rounded p-2">
                    <strong>Current behavior:</strong> Intents are stored only in local UI state. Future
                    versions may send intents to pmagent under Guarded Tool Calls. See{" "}
                    <code className="text-xs bg-white/10 px-1 py-0.5 rounded">docs/SSOT/AUTOPILOT_ORCHESTRATOR_PLAN.md</code>
                </div>
            </div>
        </div>
    );
}

