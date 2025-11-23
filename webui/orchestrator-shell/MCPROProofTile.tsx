import { useState, useEffect } from "react";

interface MCPROProofData {
    ok: boolean;
    proofs_count: number;
    all_ok: boolean;
    generated_at: string;
    proofs?: {
        e21_por?: { ok: boolean; generated_at: string };
        e22_schema?: { ok: boolean; generated_at: string };
        e23_gatekeeper?: { ok: boolean; generated_at: string };
        e24_tagproof?: { ok: boolean; generated_at: string };
    };
}

export default function MCPROProofTile() {
    const [data, setData] = useState<MCPROProofData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const res = await fetch("/exports/mcp/bundle_proof.json");
                if (res.ok) {
                    const json = await res.json();
                    setData(json);
                    setError(null);
                } else {
                    setError("MCP RO proof data not available");
                }
            } catch (err) {
                setError("Failed to load MCP RO proof data");
            } finally {
                setLoading(false);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 60000); // Poll every 60s
        return () => clearInterval(interval);
    }, []);

    if (loading) {
        return (
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <h3 className="text-lg font-semibold mb-2">MCP RO Proof Status</h3>
                <p className="text-gray-600 text-sm">Loading...</p>
            </div>
        );
    }

    if (error || !data) {
        return (
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <h3 className="text-lg font-semibold mb-2">MCP RO Proof Status</h3>
                <p className="text-gray-600 text-sm">{error || "Data unavailable"}</p>
            </div>
        );
    }

    const statusColor = data.all_ok ? "bg-green-100 text-green-800" : "bg-yellow-100 text-yellow-800";
    const statusText = data.all_ok ? "All Proofs OK" : "Some Proofs Failed";

    const proofCount = data.proofs_count || 0;
    const lastUpdated = data.generated_at
        ? new Date(data.generated_at).toLocaleString()
        : "Unknown";

    return (
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h3 className="text-lg font-semibold mb-3">MCP RO Proof Status</h3>
            <div className="space-y-3">
                <div className="flex items-center gap-2">
                    <span className={`px-3 py-1 rounded text-sm font-medium ${statusColor}`}>
                        {statusText}
                    </span>
                </div>
                <div className="text-sm text-gray-600">
                    <p>
                        <strong>Proofs:</strong> {proofCount} endpoint{proofCount !== 1 ? "s" : ""}
                    </p>
                    <p>
                        <strong>Last Updated:</strong> {lastUpdated}
                    </p>
                </div>
                {data.proofs && (
                    <div className="mt-3 pt-3 border-t border-gray-200">
                        <p className="text-xs font-semibold text-gray-700 mb-2">Proof Details:</p>
                        <ul className="space-y-1 text-xs text-gray-600">
                            {data.proofs.e21_por && (
                                <li className="flex items-center gap-2">
                                    <span
                                        className={`w-2 h-2 rounded-full ${
                                            data.proofs.e21_por.ok ? "bg-green-500" : "bg-red-500"
                                        }`}
                                    />
                                    E21 POR: {data.proofs.e21_por.ok ? "OK" : "Failed"}
                                </li>
                            )}
                            {data.proofs.e22_schema && (
                                <li className="flex items-center gap-2">
                                    <span
                                        className={`w-2 h-2 rounded-full ${
                                            data.proofs.e22_schema.ok ? "bg-green-500" : "bg-red-500"
                                        }`}
                                    />
                                    E22 Schema: {data.proofs.e22_schema.ok ? "OK" : "Failed"}
                                </li>
                            )}
                            {data.proofs.e23_gatekeeper && (
                                <li className="flex items-center gap-2">
                                    <span
                                        className={`w-2 h-2 rounded-full ${
                                            data.proofs.e23_gatekeeper.ok
                                                ? "bg-green-500"
                                                : "bg-red-500"
                                        }`}
                                    />
                                    E23 Gatekeeper: {data.proofs.e23_gatekeeper.ok ? "OK" : "Failed"}
                                </li>
                            )}
                            {data.proofs.e24_tagproof && (
                                <li className="flex items-center gap-2">
                                    <span
                                        className={`w-2 h-2 rounded-full ${
                                            data.proofs.e24_tagproof.ok ? "bg-green-500" : "bg-red-500"
                                        }`}
                                    />
                                    E24 Tagproof: {data.proofs.e24_tagproof.ok ? "OK" : "Failed"}
                                </li>
                            )}
                        </ul>
                    </div>
                )}
            </div>
        </div>
    );
}

