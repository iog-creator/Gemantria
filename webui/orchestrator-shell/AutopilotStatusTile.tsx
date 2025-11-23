import { useState, useEffect } from "react";

interface AutopilotSummaryData {
    schema: string;
    generated_at: string;
    ok: boolean;
    connection_ok?: boolean;
    stats: {
        [tool: string]: {
            total: number;
            success: number;
            error: number;
        };
    };
    window_days: number;
    error?: string;
}

export default function AutopilotStatusTile() {
    const [data, setData] = useState<AutopilotSummaryData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const res = await fetch("/exports/control-plane/autopilot_summary.json");
                if (res.ok) {
                    const json = await res.json();
                    setData(json);
                    setError(null);
                } else {
                    setError("Autopilot summary data not available");
                }
            } catch (err) {
                setError("Failed to load autopilot summary data");
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
                <h3 className="text-lg font-semibold mb-2">Autopilot Status</h3>
                <p className="text-gray-600 text-sm">Loading...</p>
            </div>
        );
    }

    if (error || !data) {
        return (
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <h3 className="text-lg font-semibold mb-2">Autopilot Status</h3>
                <p className="text-gray-600 text-sm">{error || "Data unavailable"}</p>
            </div>
        );
    }

    const connectionStatus = data.ok && data.connection_ok !== false;
    const statusColor = connectionStatus ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800";
    const statusText = connectionStatus ? "Connected" : data.error || "Disconnected";

    const lastUpdated = data.generated_at
        ? new Date(data.generated_at).toLocaleString()
        : "Unknown";

    // Aggregate stats across all tools
    const totalRuns = Object.values(data.stats).reduce((sum, tool) => sum + tool.total, 0);
    const totalSuccess = Object.values(data.stats).reduce((sum, tool) => sum + tool.success, 0);
    const totalError = Object.values(data.stats).reduce((sum, tool) => sum + tool.error, 0);

    return (
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h3 className="text-lg font-semibold mb-3">Autopilot Status</h3>
            <div className="space-y-3">
                <div className="flex items-center gap-2">
                    <span className={`px-3 py-1 rounded text-sm font-medium ${statusColor}`}>
                        {statusText}
                    </span>
                </div>
                <div className="text-sm text-gray-600">
                    <p>
                        <strong>Total Runs:</strong> {totalRuns} (last {data.window_days} days)
                    </p>
                    <p>
                        <strong>Success:</strong> {totalSuccess}
                    </p>
                    <p>
                        <strong>Errors:</strong> {totalError}
                    </p>
                    <p>
                        <strong>Last Updated:</strong> {lastUpdated}
                    </p>
                </div>
                {Object.keys(data.stats).length > 0 && (
                    <div className="mt-3 pt-3 border-t border-gray-200">
                        <p className="text-xs font-semibold text-gray-700 mb-2">By Tool:</p>
                        <ul className="space-y-1 text-xs text-gray-600">
                            {Object.entries(data.stats).map(([tool, stats]) => (
                                <li key={tool} className="flex items-center justify-between">
                                    <span className="font-medium">{tool}:</span>
                                    <span>
                                        {stats.total} total ({stats.success} success, {stats.error} error)
                                    </span>
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>
        </div>
    );
}

