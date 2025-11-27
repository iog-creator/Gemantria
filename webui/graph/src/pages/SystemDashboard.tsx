import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

interface SystemStatus {
  db: {
    reachable: boolean;
    mode: string;
    notes: string;
  };
  lm: {
    slots: Array<{
      name: string;
      provider: string;
      model: string;
      service: string;
    }>;
    notes: string;
  };
  ai_tracking?: {
    ok: boolean;
    mode: string;
    summary?: any;
  };
  share_manifest?: {
    ok: boolean;
    count: number;
    items?: any[];
  };
  kb_doc_health?: {
    available: boolean;
    total?: number;
    by_subsystem?: { [key: string]: number };
    metrics?: {
      kb_fresh_ratio?: { overall: number };
      kb_fixes_applied_last_7d?: number;
      kb_missing_count?: number;
      kb_stale_count_by_subsystem?: { [key: string]: number };
    };
  };
}

interface StatusExplain {
  level: string;
  headline: string;
  details: string;
}

interface LMIndicator {
  status: string;
  reason: string;
  metrics?: {
    total_calls?: number;
    success_rate?: number;
    avg_latency_ms?: number;
  };
}

const SystemDashboard: React.FC = () => {
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [statusExplain, setStatusExplain] = useState<StatusExplain | null>(null);
  const [lmIndicator, setLmIndicator] = useState<LMIndicator | null>(null);
  const [inferenceData, setInferenceData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const fetchDashboardData = async () => {
    try {
      setError(null);

      // Fetch all endpoints in parallel
      const [statusRes, explainRes, lmRes, inferenceRes] = await Promise.all([
        fetch('/api/status/system'),
        fetch('/api/status/explain'),
        fetch('/api/lm/indicator'),
        fetch('/api/inference/models').catch(() => null), // Optional, don't fail if unavailable
      ]);

      if (!statusRes.ok || !explainRes.ok || !lmRes.ok) {
        throw new Error('Failed to fetch dashboard data');
      }

      const [statusData, explainData, lmData, inferenceData] = await Promise.all([
        statusRes.json(),
        explainRes.json(),
        lmRes.json(),
        inferenceRes?.ok ? inferenceRes.json() : Promise.resolve(null),
      ]);

      setSystemStatus(statusData);
      setStatusExplain(explainData);
      setLmIndicator(lmData);
      setInferenceData(inferenceData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load dashboard data');
      console.error('Dashboard fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Initial fetch
    fetchDashboardData();

    // Auto-refresh every 30 seconds
    const interval = setInterval(() => {
      fetchDashboardData();
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  const getStatusBadgeClass = (level: string) => {
    switch (level.toLowerCase()) {
      case 'ok':
        return 'bg-green-500';
      case 'warn':
        return 'bg-yellow-500';
      case 'error':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getLMStatusBadgeClass = (status: string | null | undefined) => {
    if (!status) return 'bg-gray-500';
    switch (status.toLowerCase()) {
      case 'healthy':
        return 'bg-green-500';
      case 'degraded':
        return 'bg-yellow-500';
      case 'offline':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  if (loading && !systemStatus && !statusExplain && !lmIndicator) {
    return (
      <div className="bg-gray-50 p-8 h-full overflow-auto">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-3xl font-bold mb-2">System Dashboard</h1>
          <p className="text-gray-800 mb-6">Overview of system health and LM activity.</p>
          <div className="text-gray-800">Loading dashboard data...</div>
        </div>
      </div>
    );
  }

  const handleTileClick = (tileId: string) => {
    if (tileId === 'lm-insights') {
      navigate('/lm-insights');
    }
  };



  return (
    <div className="bg-gray-50 p-8 h-full overflow-auto">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold mb-2 text-gray-900">System Dashboard</h1>
        <p className="text-gray-800 mb-6">Overview of system health and LM activity. Click a tile to expand.</p>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            Error: {error}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* System Health Card */}
          <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
            <h2 className="text-xl font-semibold mb-4">System Health</h2>

            {statusExplain && systemStatus ? (
              <>
                <div className="mb-4">
                  <div
                    className={`inline-block px-3 py-1 rounded-full text-white font-semibold text-sm mb-2 ${getStatusBadgeClass(
                      statusExplain.level
                    )}`}
                  >
                    {statusExplain.level.toUpperCase()}
                  </div>
                  <div className="text-lg font-medium text-gray-800 mb-2">
                    {statusExplain.headline}
                  </div>
                </div>

                <div className="space-y-2 text-sm">
                  <div className="text-gray-700">
                    <span className="font-medium">DB Mode:</span>{' '}
                    {systemStatus.db?.mode || 'unknown'}
                    {systemStatus.db?.reachable && (
                      <span className="ml-2 text-green-600">✓</span>
                    )}
                  </div>
                  <div className="text-gray-700">
                    <span className="font-medium">LM Slots:</span>{' '}
                    {systemStatus.lm?.slots?.length || 0} configured
                  </div>
                  {systemStatus.db?.notes && (
                    <div className="text-xs text-gray-600 mt-2">
                      {systemStatus.db.notes}
                    </div>
                  )}
                </div>

                <div className="mt-4 pt-4 border-t border-gray-200">
                  <a
                    href="/status"
                    className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                  >
                    View details →
                  </a>
                </div>
              </>
            ) : (
              <div className="text-sm text-gray-700">Data unavailable</div>
            )}
          </div>

          {/* LM Insights Card - Clickable Tile */}
          <div
            onClick={() => handleTileClick('lm-insights')}
            className="bg-white rounded-lg shadow p-6 border border-gray-200 cursor-pointer hover:shadow-lg transition-shadow"
          >
            <h2 className="text-xl font-semibold mb-1 text-gray-900">Inference Models Insight</h2>
            <p className="text-xs text-gray-700 mb-4 italic">
              Real-time inference activity monitoring
            </p>

            {lmIndicator ? (
              <>
                <div className="mb-4">
                  <div
                    className={`inline-block px-3 py-1 rounded-full text-white font-semibold text-sm mb-2 ${getLMStatusBadgeClass(
                      lmIndicator.status
                    )}`}
                  >
                    {lmIndicator.status?.toUpperCase() || 'UNKNOWN'}
                  </div>
                  {lmIndicator.metrics && (
                    <div className="text-sm text-gray-700 space-y-1">
                      {lmIndicator.metrics.total_calls !== undefined && (
                        <div>
                          <span className="font-medium">Total Calls:</span>{' '}
                          {lmIndicator.metrics.total_calls}
                        </div>
                      )}
                      {lmIndicator.metrics.success_rate !== undefined && (
                        <div>
                          <span className="font-medium">Success Rate:</span>{' '}
                          {Math.round(lmIndicator.metrics.success_rate * 100)}%
                        </div>
                      )}
                    </div>
                  )}
                </div>

                <div className="mt-4 pt-4 border-t border-gray-200">
                  <div className="text-blue-600 hover:text-blue-800 text-sm font-medium">
                    Click to expand →
                  </div>
                </div>
              </>
            ) : inferenceData ? (
              <>
                <div className="mb-4">
                  {(() => {
                    const activeCount = inferenceData.ollama?.active_requests?.length || 0;
                    const recentCount = (inferenceData.ollama?.recent_requests?.length || 0) +
                      (inferenceData.lmstudio?.recent_activity?.length || 0);
                    return (
                      <>
                        <div className="flex items-center gap-3 mb-2">
                          <div className={`text-3xl font-bold ${activeCount > 0 ? 'text-yellow-500' : 'text-gray-400'}`}>
                            {activeCount}
                          </div>
                          <div>
                            <div className="text-sm font-medium text-gray-900">
                              Active Inference{activeCount !== 1 ? 's' : ''}
                            </div>
                            <div className="text-xs text-gray-600">
                              {recentCount} recent request{recentCount !== 1 ? 's' : ''}
                            </div>
                          </div>
                        </div>
                        {activeCount > 0 && (
                          <div className="flex items-center gap-2 text-xs text-yellow-600">
                            <div className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse"></div>
                            <span>Models processing requests</span>
                          </div>
                        )}
                      </>
                    );
                  })()}
                </div>

                <div className="mt-4 pt-4 border-t border-gray-200">
                  <div className="text-blue-600 hover:text-blue-800 text-sm font-medium">
                    Click to expand →
                  </div>
                </div>
              </>
            ) : (
              <div className="text-sm text-gray-700">Loading inference data...</div>
            )}
          </div>

          {/* Governance Health Card */}
          <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
            <h2 className="text-xl font-semibold mb-4">Governance Health</h2>

            {systemStatus?.kb_doc_health?.available ? (
              <>
                <div className="space-y-2 text-sm">
                  <div className="text-gray-700">
                    <span className="font-medium">Total Docs:</span>{' '}
                    {systemStatus.kb_doc_health.total || 0}
                  </div>
                  {systemStatus.kb_doc_health.by_subsystem && (
                    <div className="text-gray-700">
                      <span className="font-medium">Subsystems:</span>{' '}
                      {Object.keys(systemStatus.kb_doc_health.by_subsystem).length}
                    </div>
                  )}
                  {systemStatus.kb_doc_health.metrics && (
                    <div className="mt-3 pt-3 border-t border-gray-200">
                      <div className="text-xs text-gray-600 space-y-1">
                        {systemStatus.kb_doc_health.metrics.kb_fresh_ratio?.overall !== undefined && (
                          <div>
                            <span className="font-medium">Freshness:</span>{' '}
                            {Math.round(systemStatus.kb_doc_health.metrics.kb_fresh_ratio.overall)}%
                          </div>
                        )}
                        {systemStatus.kb_doc_health.metrics.kb_fixes_applied_last_7d !== undefined && (
                          <div>
                            <span className="font-medium">Fixes (7d):</span>{' '}
                            {systemStatus.kb_doc_health.metrics.kb_fixes_applied_last_7d}
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </>
            ) : systemStatus?.ai_tracking ? (
              <>
                <div className="space-y-2 text-sm">
                  <div className="text-gray-700">
                    <span className="font-medium">AI Tracking:</span>{' '}
                    <span className={systemStatus.ai_tracking.ok ? 'text-green-600' : 'text-yellow-600'}>
                      {systemStatus.ai_tracking.mode || 'unknown'}
                    </span>
                  </div>
                  {systemStatus.share_manifest && (
                    <div className="text-gray-700">
                      <span className="font-medium">Share Manifest:</span>{' '}
                      {systemStatus.share_manifest.count || 0} items
                    </div>
                  )}
                </div>
              </>
            ) : (
              <div className="text-sm text-gray-700">Data unavailable</div>
            )}
          </div>
        </div>

        {/* Auto-refresh indicator */}
        <div className="mt-6 text-xs text-gray-700 text-center">
          Auto-refreshing every 30 seconds
        </div>
      </div>
    </div>
  );
};

export default SystemDashboard;

