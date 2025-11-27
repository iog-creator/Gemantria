import React, { useState } from "react";
import { useHeaderData } from "./useHeaderData";
import MCPROProofTile from "./MCPROProofTile";
import BrowserVerifiedBadge from "./BrowserVerifiedBadge";
import AutopilotStatusTile from "./AutopilotStatusTile";

interface Intent {
    id: number;
    text: string;
    createdAt: string;
    planId?: string;
    summary?: string;
    status?: string;
    accepted?: boolean;
}

export default function OrchestratorOverview() {
    const { db, lm, system } = useHeaderData();
    const [intentText, setIntentText] = useState("");
    const [intents, setIntents] = useState<Intent[]>([]);

    async function addIntent(event: React.FormEvent) {
        event.preventDefault();
        const trimmed = intentText.trim();
        if (!trimmed) return;
        const now = new Date().toISOString();

        // Create intent entry immediately (optimistic UI)
        const newIntent: Intent = {
            id: Date.now(),
            text: trimmed,
            createdAt: now,
            status: "pending",
        };
        setIntents((prev) => [newIntent, ...prev]);
        setIntentText("");

        // Call backend API
        try {
            const response = await fetch("/api/autopilot/intent", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    intent_text: trimmed,
                    context: {
                        dry_run: false, // Default to false to "get things going"
                    },
                }),
            });

            if (!response.ok) {
                throw new Error(`API error: ${response.statusText}`);
            }

            const data = await response.json();

            // Update the intent with backend response
            setIntents((prev) =>
                prev.map((intent) =>
                    intent.id === newIntent.id
                        ? {
                            ...intent,
                            planId: data.plan_id,
                            summary: data.summary,
                            status: data.status,
                            accepted: data.accepted,
                        }
                        : intent
                )
            );
        } catch (error) {
            console.error("Failed to send intent to backend:", error);
            // Update intent to show error
            setIntents((prev) =>
                prev.map((intent) =>
                    intent.id === newIntent.id
                        ? {
                            ...intent,
                            status: "error",
                            summary: `Error: ${error instanceof Error ? error.message : "Unknown error"}`,
                        }
                        : intent
                )
            );
        }
    }

    const signals = [
        db && { label: "DB", status: db.status, reason: db.reason },
        lm && { label: "LM", status: lm.status, reason: lm.reason },
        system && { label: "System", status: system.status, reason: system.reason },
    ].filter(Boolean) as { label: string; status: string; reason?: string }[];

    return (
        <div className="orchestrator-overview p-8">
            <section className="header-badges mb-6">
                <div className="flex items-center gap-4">
                    <BrowserVerifiedBadge />
                </div>
            </section>

            <section className="signals mb-8 nanobanna-glass p-6 rounded-lg">
                <h2 className="text-xl font-bold mb-4">Recent Signals</h2>
                {signals.length === 0 ? (
                    <div className="text-gray-300">
                        <p className="mb-2">When exports are present, you will see DB/LM/System summaries here.</p>
                        <p className="text-sm text-gray-400">
                            These signals update from static JSON exports. No direct backend queries are made.
                        </p>
                    </div>
                ) : (
                    <>
                        <ul className="space-y-2 mb-4">
                            {signals.map((s) => (
                                <li key={s.label} className="flex items-center gap-2 text-gray-200">
                                    <strong>{s.label}:</strong>
                                    <span className={`px-2 py-0.5 rounded text-sm ${s.status === 'healthy' ? 'bg-green-900 text-green-100 border border-green-700' :
                                        s.status === 'degraded' ? 'bg-yellow-900 text-yellow-100 border border-yellow-700' :
                                            'bg-red-900 text-red-100 border border-red-700'
                                        }`}>
                                        {s.status}
                                    </span>
                                    {s.reason ? <span className="text-gray-400">— {s.reason}</span> : null}
                                </li>
                            ))}
                        </ul>
                        {signals.some(s => s.status === 'offline' || s.status === 'degraded') && (
                            <div className="text-sm text-gray-300 bg-yellow-900/30 border border-yellow-700 rounded p-3">
                                <strong>WHEN/THEN:</strong> When Postgres is available and DB health passes,
                                this panel will show live graph/DB stats. When LM Studio is reachable,
                                model status will appear.
                            </div>
                        )}
                    </>
                )}
            </section>

            <section className="mcp-proof mb-8 nanobanna-glass p-6 rounded-lg">
                <MCPROProofTile />
            </section>

            <section className="autopilot-status mb-8">
                <AutopilotStatusTile />
            </section>

            <section className="autopilot nanobanna-glass p-6 rounded-lg">
                <h2 className="text-xl font-bold mb-2">Autopilot (Local Intent Log)</h2>
                <div className="text-gray-200 mb-4 space-y-1">
                    <p>
                        <strong>Current behavior:</strong> Intents are sent to the pmagent backend
                        and executed when <code className="text-xs bg-gray-700 px-1 py-0.5 rounded">dry_run: false</code>.
                    </p>
                    <p className="text-sm">
                        Phase C: Guarded execution enabled. Only whitelisted intents are executed.
                        See{" "}
                        <code className="text-xs bg-gray-700 px-1 py-0.5 rounded">
                            docs/SSOT/AUTOPILOT_ORCHESTRATOR_PLAN.md
                        </code>
                    </p>
                </div>
                <form onSubmit={addIntent} className="mb-6">
                    <div className="flex gap-2">
                        <textarea
                            value={intentText}
                            onChange={(e) => setIntentText(e.target.value)}
                            placeholder="Example: Show me what my models and docs are doing."
                            rows={3}
                            className="flex-1 p-2 border border-gray-600 bg-gray-800 text-white rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        />
                    </div>
                    <button
                        type="submit"
                        className="mt-2 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 shadow-lg border border-blue-400"
                    >
                        Send intent to Autopilot
                    </button>
                </form>

                {intents.length > 0 && (
                    <div className="intent-log">
                        <h3 className="font-semibold mb-2 text-white">Recent intents</h3>
                        <ul className="space-y-2">
                            {intents.map((i) => (
                                <li key={i.id} className="text-sm text-gray-200 border-l-2 border-blue-400 pl-3 bg-gray-800/50 p-2 rounded">
                                    <time dateTime={i.createdAt} className="text-gray-400 text-xs block">
                                        {new Date(i.createdAt).toLocaleString()}
                                    </time>
                                    <div className="font-medium mb-1 text-white">{i.text}</div>
                                    {i.planId && (
                                        <div className="text-xs text-gray-300 space-y-1">
                                            <div>
                                                <strong>Plan ID:</strong> {i.planId}
                                            </div>
                                            {i.status && (
                                                <div>
                                                    <strong>Status:</strong>{" "}
                                                    <span
                                                        className={`px-1.5 py-0.5 rounded ${i.status === "completed"
                                                            ? "bg-green-900 text-green-100 border border-green-700"
                                                            : i.status === "failed" || i.status === "error"
                                                                ? "bg-red-900 text-red-100 border border-red-700"
                                                                : i.status === "planned"
                                                                    ? "bg-yellow-900 text-yellow-100 border border-yellow-700"
                                                                    : "bg-gray-700 text-gray-100"
                                                            }`}
                                                    >
                                                        {i.status}
                                                    </span>
                                                </div>
                                            )}
                                            {i.accepted !== undefined && (
                                                <div>
                                                    <strong>Accepted:</strong> {i.accepted ? "Yes" : "No"}
                                                </div>
                                            )}
                                            {i.summary && (
                                                <div className="mt-1 p-2 bg-gray-900 rounded text-xs border border-gray-700">
                                                    <strong>Summary:</strong> {i.summary}
                                                </div>
                                            )}
                                        </div>
                                    )}
                                    {i.status === "pending" && (
                                        <div className="text-xs text-gray-400 italic">Processing...</div>
                                    )}
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
            </section>
        </div>
    );
}
