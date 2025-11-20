import React, { useState, useEffect } from 'react';
import { getDBHealth, DBHealthData } from '../dashboard/src/utils/dbData';

const SummaryTile: React.FC<{ title: string; value: string | number; subtext?: string }> = ({
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

const StatusBadge: React.FC<{ mode: string }> = ({ mode }) => {
    const getStatusColor = (m: string) => {
        switch (m) {
            case 'ready': return 'bg-green-500';
            case 'partial': return 'bg-yellow-500';
            case 'db_off': return 'bg-red-500';
            default: return 'bg-gray-500';
        }
    };

    const getStatusText = (m: string) => {
        switch (m) {
            case 'ready': return 'Ready';
            case 'partial': return 'Partial';
            case 'db_off': return 'Offline';
            default: return 'Unknown';
        }
    };

    return (
        <div className="flex items-center gap-2">
            <div className={`w-3 h-3 rounded-full ${getStatusColor(mode)}`} />
            <span className="font-medium">{getStatusText(mode)}</span>
        </div>
    );
};

const CheckBadge: React.FC<{ label: string; ok: boolean | null | undefined }> = ({ label, ok }) => {
    if (ok === null || ok === undefined) {
        return (
            <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-gray-300" />
                <span className="text-sm text-gray-500">{label}: N/A</span>
            </div>
        );
    }
    return (
        <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${ok ? 'bg-green-500' : 'bg-red-500'}`} />
            <span className={`text-sm ${ok ? 'text-green-700' : 'text-red-700'}`}>
                {label}: {ok ? 'OK' : 'Failed'}
            </span>
        </div>
    );
};

export default function DbPanel() {
    const [dbHealth, setDbHealth] = useState<DBHealthData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const loadData = async () => {
            setLoading(true);
            setError(null);
            try {
                const health = await getDBHealth();
                setDbHealth(health);
            } catch (err) {
                console.error('Failed to load DB health data:', err);
                setError('Failed to load DB health data. Ensure DB health exports are available.');
            } finally {
                setLoading(false);
            }
        };
        loadData();
    }, []);

    if (loading) {
        return <div className="p-8 text-center text-gray-500">Loading DB health data...</div>;
    }

    if (error) {
        return (
            <div className="p-8 text-center">
                <div className="text-red-600 font-medium mb-2">Error Loading Data</div>
                <div className="text-gray-500 text-sm">{error}</div>
            </div>
        );
    }

    const mode = dbHealth?.mode || 'unknown';
    const ok = dbHealth?.ok || false;
    const checks = dbHealth?.checks || {};
    const errors = dbHealth?.details?.errors || [];
    const hasData = dbHealth !== null;

    return (
        <div className="p-6 max-w-7xl mx-auto bg-gray-50 min-h-screen">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold text-gray-900">Database</h1>
            </div>

            {/* Status Card */}
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 mb-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-3">DB Status</h2>
                <div className="flex items-center gap-4">
                    <StatusBadge mode={mode} />
                    <p className="text-gray-700">
                        {mode === 'ready' && 'Database is ready and all checks passed.'}
                        {mode === 'partial' && 'Database is partially available (some checks failed).'}
                        {mode === 'db_off' && 'Database is offline or unreachable.'}
                        {mode === 'unknown' && 'Database status is unknown.'}
                    </p>
                </div>
            </div>

            {/* Checks Card */}
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 mb-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-3">Health Checks</h2>
                <div className="space-y-2">
                    <CheckBadge label="Driver Available" ok={checks.driver_available} />
                    <CheckBadge label="Connection OK" ok={checks.connection_ok} />
                    <CheckBadge label="Graph Stats Ready" ok={checks.graph_stats_ready} />
                </div>
            </div>

            {/* Metrics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
                <SummaryTile
                    title="Overall Status"
                    value={ok ? 'Healthy' : 'Unhealthy'}
                    subtext={mode}
                />
                <SummaryTile
                    title="Checks Passed"
                    value={
                        [
                            checks.driver_available,
                            checks.connection_ok,
                            checks.graph_stats_ready,
                        ].filter((v) => v === true).length
                    }
                    subtext="of 3 checks"
                />
                <SummaryTile
                    title="Errors"
                    value={errors.length}
                    subtext={errors.length > 0 ? 'See details below' : 'No errors'}
                />
            </div>

            {/* Error Details */}
            {errors.length > 0 && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
                    <h3 className="font-semibold text-red-900 mb-2">Error Details</h3>
                    <div className="text-sm text-red-800 space-y-1">
                        {errors.map((err, idx) => (
                            <p key={idx} className="font-mono text-xs">
                                {err}
                            </p>
                        ))}
                    </div>
                </div>
            )}

            {/* WHEN/THEN Messaging */}
            {(!hasData || mode === 'db_off' || mode === 'unknown') && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
                    <h3 className="font-semibold text-yellow-900 mb-2">WHEN/THEN</h3>
                    <div className="text-sm text-yellow-800 space-y-1">
                        {!hasData && (
                            <p>
                                <strong>No DB health export found.</strong> Run{' '}
                                <code className="bg-yellow-100 px-1 py-0.5 rounded text-xs">
                                    python -m scripts.system.system_health
                                </code>{' '}
                                to generate system health exports (includes DB health).
                            </p>
                        )}
                        {mode === 'db_off' && hasData && (
                            <p>
                                <strong>Database is offline or unreachable.</strong> When Postgres is available and DB
                                health passes, you'll see connection status and graph stats readiness here. Ensure
                                Postgres is running and <code className="bg-yellow-100 px-1 py-0.5 rounded text-xs">GEMATRIA_DSN</code> is
                                correctly configured.
                            </p>
                        )}
                        {mode === 'partial' && hasData && (
                            <p>
                                <strong>Database is partially available.</strong> Some checks passed, but others failed.
                                Review error details above. When all checks pass, mode will be "ready".
                            </p>
                        )}
                    </div>
                </div>
            )}

            {/* Additional Info */}
            {hasData && mode === 'ready' && (
                <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
                    <h3 className="text-sm font-semibold text-gray-700 mb-2">Additional Information</h3>
                    <div className="text-xs text-gray-600 space-y-1">
                        <p>
                            <strong>Mode:</strong> {mode}
                        </p>
                        <p>
                            <strong>All Checks:</strong> Passed
                        </p>
                        <p>
                            <strong>Graph Stats:</strong> Ready for queries
                        </p>
                    </div>
                </div>
            )}
        </div>
    );
}

