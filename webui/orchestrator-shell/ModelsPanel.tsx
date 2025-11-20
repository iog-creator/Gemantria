import React, { useState, useEffect } from 'react';
import {
    getLMIndicator,
    getLMUsage7d,
    getLMHealth7d,
    getLMInsights7d,
    LMIndicatorData,
    LMUsage7dData,
    LMHealth7dData,
    LMInsights7dData
} from '../dashboard/src/utils/modelsData';

const SummaryTile: React.FC<{ title: string; value: number | string; subtext?: string }> = ({
    title,
    value,
    subtext,
}) => (
    <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100">
        <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">{title}</h3>
        <div className="mt-1 text-2xl font-bold text-gray-900">{value}</div>
        {subtext && <div className="mt-1 text-xs text-gray-400">{subtext}</div>}
    </div>
);

const StatusBadge: React.FC<{ status: string }> = ({ status }) => {
    const getStatusColor = (s: string) => {
        switch (s) {
            case 'healthy': return 'bg-green-500';
            case 'degraded': return 'bg-yellow-500';
            case 'offline': return 'bg-red-500';
            default: return 'bg-gray-500';
        }
    };

    const getStatusText = (s: string) => {
        switch (s) {
            case 'healthy': return 'Healthy';
            case 'degraded': return 'Degraded';
            case 'offline': return 'Offline';
            default: return 'Unknown';
        }
    };

    return (
        <div className="flex items-center gap-2">
            <div className={`w-3 h-3 rounded-full ${getStatusColor(status)}`} />
            <span className="font-medium">{getStatusText(status)}</span>
        </div>
    );
};

export default function ModelsPanel() {
    const [indicator, setIndicator] = useState<LMIndicatorData | null>(null);
    const [usage, setUsage] = useState<LMUsage7dData | null>(null);
    const [health, setHealth] = useState<LMHealth7dData | null>(null);
    const [insights, setInsights] = useState<LMInsights7dData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const loadData = async () => {
            setLoading(true);
            setError(null);
            try {
                const [ind, usg, hlt, ins] = await Promise.all([
                    getLMIndicator(),
                    getLMUsage7d(),
                    getLMHealth7d(),
                    getLMInsights7d(),
                ]);
                setIndicator(ind);
                setUsage(usg);
                setHealth(hlt);
                setInsights(ins);
            } catch (err) {
                console.error('Failed to load models data:', err);
                setError('Failed to load models data. Ensure "make atlas.lm.indicator" has been run.');
            } finally {
                setLoading(false);
            }
        };
        loadData();
    }, []);

    if (loading) {
        return <div className="p-8 text-center text-gray-500">Loading Models data...</div>;
    }

    if (error) {
        return (
            <div className="p-8 text-center">
                <div className="text-red-600 font-medium mb-2">Error Loading Data</div>
                <div className="text-gray-500 text-sm">{error}</div>
            </div>
        );
    }

    // Determine status (prefer indicator, fallback to health/usage)
    const status = indicator?.status || (health?.ok === false ? 'offline' : 'unknown');
    const dbOff = indicator?.db_off || insights?.db_off || false;
    const hasData = indicator !== null || usage !== null || health !== null || insights !== null;

    // Extract metrics with fallbacks
    const totalCalls = indicator?.total_calls ?? usage?.total_calls ?? health?.total_calls ?? null;
    const successRate = indicator?.success_rate ?? health?.success_rate ?? null;
    const errorRate = indicator?.error_rate ?? health?.error_rate ?? null;
    const avgLatency = usage?.avg_latency_ms ?? health?.avg_latency_ms ?? null;

    // Get latest generated_at timestamp
    const generatedAt = indicator?.generated_at || usage?.generated_at || health?.generated_at || insights?.generated_at || null;

    // Format helpers
    const formatPercent = (val: number | null) => {
        if (val === null || val === undefined) return 'N/A';
        return `${(val * 100).toFixed(1)}%`;
    };

    const formatNumber = (val: number | null) => {
        if (val === null || val === undefined) return 'N/A';
        return val.toLocaleString();
    };

    const formatLatency = (val: number | null) => {
        if (val === null || val === undefined) return 'N/A';
        return `${val.toFixed(0)} ms`;
    };

    return (
        <div className="p-6 max-w-7xl mx-auto bg-gray-50 min-h-screen">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold text-gray-900">Models</h1>
                {generatedAt && (
                    <div className="text-xs text-gray-400">
                        Last Updated: {new Date(generatedAt).toLocaleString()}
                    </div>
                )}
            </div>

            {/* Status Card */}
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 mb-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-3">LM Status</h2>
                <div className="flex items-center gap-4">
                    <StatusBadge status={status} />
                    <p className="text-gray-700">
                        {status === 'healthy' && 'LM is healthy and operational.'}
                        {status === 'degraded' && 'LM is operational but experiencing issues.'}
                        {status === 'offline' && 'LM Studio appears offline or unreachable.'}
                        {status === 'unknown' && 'LM status is unknown.'}
                    </p>
                </div>
            </div>

            {/* Metrics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                <SummaryTile
                    title="Total Calls"
                    value={formatNumber(totalCalls)}
                    subtext="Last 7 days"
                />
                <SummaryTile
                    title="Success Rate"
                    value={formatPercent(successRate)}
                    subtext="Successful requests"
                />
                <SummaryTile
                    title="Error Rate"
                    value={formatPercent(errorRate)}
                    subtext="Failed requests"
                />
                <SummaryTile
                    title="Avg Latency"
                    value={formatLatency(avgLatency)}
                    subtext="Response time"
                />
            </div>

            {/* WHEN/THEN Messaging */}
            {(!hasData || status === 'offline' || dbOff) && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
                    <h3 className="font-semibold text-yellow-900 mb-2">WHEN/THEN</h3>
                    <div className="text-sm text-yellow-800 space-y-1">
                        {!hasData && (
                            <p>
                                <strong>No recent LM exports found.</strong> Run{' '}
                                <code className="bg-yellow-100 px-1 py-0.5 rounded text-xs">make atlas.lm.indicator</code>{' '}
                                to generate LM status exports.
                            </p>
                        )}
                        {(status === 'offline' || dbOff) && hasData && (
                            <p>
                                <strong>LM Studio appears offline or unreachable.</strong> When LM is healthy, you'll see
                                model usage and health metrics here. When Postgres is available and LM exports are
                                generated, this panel will show live metrics.
                            </p>
                        )}
                        {indicator?.error && (
                            <p className="text-xs text-yellow-700 mt-2">
                                <strong>Error:</strong> {indicator.error}
                            </p>
                        )}
                    </div>
                </div>
            )}

            {/* Additional Info */}
            {hasData && status !== 'offline' && !dbOff && (
                <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
                    <h3 className="text-sm font-semibold text-gray-700 mb-2">Additional Information</h3>
                    <div className="text-xs text-gray-600 space-y-1">
                        {indicator?.top_error_reason && (
                            <p>
                                <strong>Top Error:</strong> {indicator.top_error_reason}
                            </p>
                        )}
                        {insights?.lm_studio_usage_ratio !== null && insights?.lm_studio_usage_ratio !== undefined && (
                            <p>
                                <strong>LM Studio Usage Ratio:</strong>{' '}
                                {(insights.lm_studio_usage_ratio * 100).toFixed(1)}%
                            </p>
                        )}
                        {indicator?.window_days && (
                            <p>
                                <strong>Window:</strong> Last {indicator.window_days} days
                            </p>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}

