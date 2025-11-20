import React from 'react';
import { useInsightsData } from './useInsightsData';

const StatusBadge: React.FC<{ level: 'OK' | 'WARN' | 'ERROR' | null }> = ({ level }) => {
    const getStatusColor = (l: string | null) => {
        switch (l) {
            case 'OK': return 'bg-green-500';
            case 'WARN': return 'bg-yellow-500';
            case 'ERROR': return 'bg-red-500';
            default: return 'bg-gray-500';
        }
    };

    const getStatusText = (l: string | null) => {
        switch (l) {
            case 'OK': return 'All systems go';
            case 'WARN': return 'Degraded';
            case 'ERROR': return 'Attention needed';
            default: return 'Unknown';
        }
    };

    return (
        <div className="flex items-center gap-2">
            <div className={`w-3 h-3 rounded-full ${getStatusColor(level)}`} />
            <span className="font-semibold text-lg">{getStatusText(level)}</span>
        </div>
    );
};

export default function InsightsPanel() {
    const insights = useInsightsData();

    // Determine if we have any data
    const hasData = insights.overallLevel !== null || insights.hints.length > 0;

    return (
        <div className="p-6 max-w-7xl mx-auto bg-gray-50 min-h-screen">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold text-gray-900">Insights</h1>
                {insights.lastUpdated && (
                    <div className="text-xs text-gray-400">
                        Last Updated: {new Date(insights.lastUpdated).toLocaleString()}
                    </div>
                )}
            </div>

            {!hasData ? (
                // Empty/offline state
                <div className="bg-white p-8 rounded-lg shadow-sm border border-gray-200 text-center">
                    <h2 className="text-lg font-semibold text-gray-700 mb-2">Waiting for data</h2>
                    <p className="text-gray-600 mb-4">Insights are not available yet.</p>
                    <div className="text-sm text-gray-500 space-y-1">
                        <p>Check <code className="bg-gray-100 px-2 py-1 rounded text-xs">make reality.green</code> and see</p>
                        <p><code className="bg-gray-100 px-2 py-1 rounded text-xs">DB_HEALTH.md</code> / LM runbooks if this persists.</p>
                    </div>
                </div>
            ) : (
                <div className="space-y-6">
                    {/* System Health Card */}
                    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                        <h2 className="text-lg font-semibold text-gray-900 mb-4">System Health</h2>
                        <div className="mb-4">
                            <StatusBadge level={insights.overallLevel} />
                        </div>
                        <div className="text-sm text-gray-700 space-y-2">
                            <p>
                                <strong>DB:</strong> {insights.dbSummary}
                            </p>
                            {insights.overallLevel === 'ERROR' && (
                                <p className="text-red-600 text-xs mt-2">
                                    <strong>Note:</strong> When DB is offline, no operations should be considered valid.
                                </p>
                            )}
                        </div>
                    </div>

                    {/* LM Stack Card */}
                    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                        <h2 className="text-lg font-semibold text-gray-900 mb-4">LM Stack</h2>
                        <div className="text-sm text-gray-700 mb-4">
                            <p>{insights.lmSummary}</p>
                        </div>
                        {insights.slots.length > 0 ? (
                            <div className="mt-4 space-y-2">
                                <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
                                    Model Slots
                                </h3>
                                {insights.slots.map((slot) => (
                                    <div key={slot.name} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
                                        <div className="flex items-center gap-3">
                                            <span className="font-medium text-gray-900 capitalize">{slot.name.replace('_', ' ')}</span>
                                            <span className="text-xs text-gray-500">{slot.model}</span>
                                        </div>
                                        <div className="flex items-center gap-2">
                                            <div className={`w-2 h-2 rounded-full ${
                                                slot.status === 'healthy' ? 'bg-green-500' :
                                                slot.status === 'degraded' ? 'bg-yellow-500' :
                                                'bg-red-500'
                                            }`} />
                                            <span className="text-xs text-gray-600 capitalize">{slot.status}</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="mt-4 text-xs text-gray-500">
                                <p>Per-slot model details will appear here when available.</p>
                                <p className="mt-1">See <strong>Models</strong> panel for detailed LM metrics.</p>
                            </div>
                        )}
                    </div>

                    {/* Signals / Insights List */}
                    {insights.hints.length > 0 && (
                        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                            <h2 className="text-lg font-semibold text-gray-900 mb-4">Signals</h2>
                            <ul className="space-y-2">
                                {insights.hints.map((hint, idx) => (
                                    <li key={idx} className="flex items-start gap-2 text-sm text-gray-700">
                                        <span className="text-gray-400 mt-0.5">•</span>
                                        <span>{hint}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}

                    {/* WHEN/THEN messaging for missing data */}
                    {insights.overallLevel === 'WARN' && insights.hints.some(h => h.includes('missing') || h.includes('not available')) && (
                        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                            <h3 className="font-semibold text-yellow-900 mb-2">WHEN/THEN</h3>
                            <div className="text-sm text-yellow-800 space-y-1">
                                <p>
                                    <strong>Some data is missing.</strong> When exports are available, this panel will show live system insights.
                                </p>
                                <p className="text-xs mt-2">
                                    Run <code className="bg-yellow-100 px-1 py-0.5 rounded">make reality.green</code> to verify system state and exports.
                                </p>
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

