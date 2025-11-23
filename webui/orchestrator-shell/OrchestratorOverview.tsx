import { useState } from "react";
import { useHeaderData } from "./useHeaderData";
import MCPROProofTile from "./MCPROProofTile";
import BrowserVerifiedBadge from "./BrowserVerifiedBadge";
import AutopilotStatusTile from "./AutopilotStatusTile";

interface Intent {
    id: number;
    text: string;
    createdAt: string;
}

export default function OrchestratorOverview() {
    const { db, lm, system } = useHeaderData();
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

            <section className="signals mb-8">
                <h2 className="text-xl font-bold mb-4">Recent Signals</h2>
                {signals.length === 0 ? (
                    <div className="text-gray-600">
                        <p className="mb-2">When exports are present, you will see DB/LM/System summaries here.</p>
                        <p className="text-sm">
                            These signals update from static JSON exports. No direct backend queries are made.
                        </p>
                    </div>
                ) : (
                    <>
                        <ul className="space-y-2 mb-4">
                            {signals.map((s) => (
                                <li key={s.label} className="flex items-center gap-2">
                                    <strong>{s.label}:</strong>
                                    <span className={`px-2 py-0.5 rounded text-sm ${s.status === 'healthy' ? 'bg-green-100 text-green-800' :
                                            s.status === 'degraded' ? 'bg-yellow-100 text-yellow-800' :
                                                'bg-red-100 text-red-800'
                                        }`}>
                                        {s.status}
                                    </span>
                                    {s.reason ? <span className="text-gray-600">— {s.reason}</span> : null}
                                </li>
                            ))}
                        </ul>
                        {signals.some(s => s.status === 'offline' || s.status === 'degraded') && (
                            <div className="text-sm text-gray-600 bg-yellow-50 border border-yellow-200 rounded p-3">
                                <strong>WHEN/THEN:</strong> When Postgres is available and DB health passes,
                                this panel will show live graph/DB stats. When LM Studio is reachable,
                                model status will appear.
                            </div>
                        )}
                    </>
                )}
            </section>

            <section className="mcp-proof mb-8">
                <MCPROProofTile />
            </section>

            <section className="autopilot-status mb-8">
                <AutopilotStatusTile />
            </section>

            <section className="autopilot bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <h2 className="text-xl font-bold mb-2">Autopilot (Local Intent Log)</h2>
                <div className="text-gray-600 mb-4 space-y-1">
                    <p>
                        <strong>Current behavior:</strong> This box does not call any backend.
                        Intents are stored only in local UI state.
                    </p>
                    <p className="text-sm">
                        <strong>Future versions</strong> may send intents to pmagent under Guarded Tool Calls,
                        but v1 is read-only/local-only. See{" "}
                        <code className="text-xs bg-gray-100 px-1 py-0.5 rounded">
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
                            className="flex-1 p-2 border rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        />
                    </div>
                    <button
                        type="submit"
                        className="mt-2 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                    >
                        Save intent (local only)
                    </button>
                </form>

                {intents.length > 0 && (
                    <div className="intent-log">
                        <h3 className="font-semibold mb-2">Recent intents</h3>
                        <ul className="space-y-2">
                            {intents.map((i) => (
                                <li key={i.id} className="text-sm text-gray-700 border-l-2 border-gray-300 pl-3">
                                    <time dateTime={i.createdAt} className="text-gray-500 text-xs block">
                                        {new Date(i.createdAt).toLocaleString()}
                                    </time>
                                    {i.text}
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
            </section>
        </div>
    );
}
