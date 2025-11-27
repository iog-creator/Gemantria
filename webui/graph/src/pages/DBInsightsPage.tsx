import React, { useState, useEffect } from 'react';

interface DBHealthSnapshot {
  generated_at: string;
  mode: 'ready' | 'partial' | 'db_off';
  notes: string;
  ok: boolean;
}

interface DBHealthTimeline {
  snapshots: DBHealthSnapshot[];
  note?: string;
}

const DBInsightsPage: React.FC = () => {
  const [timelineData, setTimelineData] = useState<DBHealthTimeline | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      const response = await fetch('/api/db/health_timeline');
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      const jsonData = await response.json();
      setTimelineData(jsonData);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch DB health timeline');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const getModeColor = (mode: string): string => {
    switch (mode) {
      case 'ready':
        return 'text-green-400';
      case 'partial':
        return 'text-yellow-400';
      case 'db_off':
        return 'text-red-400';
      default:
        return 'text-gray-400';
    }
  };

  const getModeBgColor = (mode: string): string => {
    switch (mode) {
      case 'ready':
        return 'bg-green-900/30 border-green-600';
      case 'partial':
        return 'bg-yellow-900/30 border-yellow-600';
      case 'db_off':
        return 'bg-red-900/30 border-red-600';
      default:
        return 'bg-gray-800 border-gray-700';
    }
  };

  const getModeBadge = (mode: string): string => {
    switch (mode) {
      case 'ready':
        return 'bg-green-900 text-green-200';
      case 'partial':
        return 'bg-yellow-900 text-yellow-200';
      case 'db_off':
        return 'bg-red-900 text-red-200';
      default:
        return 'bg-gray-700 text-gray-300';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 text-white p-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold mb-2 text-white">DB Health Insights</h1>
          <p className="text-gray-300 mb-6">Loading DB health data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-900 text-white p-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold mb-2 text-white">DB Health Insights</h1>
          <div className="bg-red-900 border border-red-700 rounded-lg p-4 text-red-100">
            <strong>Error:</strong> {error}
          </div>
        </div>
      </div>
    );
  }

  if (!timelineData || timelineData.snapshots.length === 0) {
    return (
      <div className="min-h-screen bg-gray-900 text-white p-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold mb-2 text-white">DB Health Insights</h1>
          <div className="bg-gray-800 rounded-lg border border-gray-700 p-12 text-center">
            <div className="text-gray-400 text-lg mb-2">No DB health data available</div>
            <div className="text-gray-500 text-sm">
              {timelineData?.note || 'Run `make pm.snapshot` to populate this chart.'}
            </div>
          </div>
        </div>
      </div>
    );
  }

  const latestSnapshot = timelineData.snapshots[timelineData.snapshots.length - 1];
  const modeCounts = timelineData.snapshots.reduce(
    (acc, snap) => {
      acc[snap.mode] = (acc[snap.mode] || 0) + 1;
      return acc;
    },
    {} as Record<string, number>
  );

  return (
    <div className="min-h-full bg-gray-900 text-white p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold mb-2 text-white">DB Health Insights</h1>
            <p className="text-gray-300 text-sm">
              Database health timeline and status • Updated every 30 seconds
            </p>
          </div>
          {latestSnapshot.generated_at && (
            <div className="text-sm text-gray-400">
              {new Date(latestSnapshot.generated_at).toLocaleString()}
            </div>
          )}
        </div>

        {/* Current Status Card */}
        <div className={`mb-6 rounded-lg border-2 p-6 ${getModeBgColor(latestSnapshot.mode)}`}>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className={`w-3 h-3 rounded-full ${latestSnapshot.ok ? 'bg-green-400' : 'bg-red-400'} ${latestSnapshot.ok ? '' : 'animate-pulse'}`}></div>
              <h2 className="text-xl font-semibold text-white">Current Status</h2>
            </div>
            <span className={`px-3 py-1 rounded text-sm font-medium ${getModeBadge(latestSnapshot.mode)}`}>
              {latestSnapshot.mode.toUpperCase()}
            </span>
          </div>
          <div className="space-y-2">
            <div className={`text-lg font-medium ${getModeColor(latestSnapshot.mode)}`}>
              {latestSnapshot.notes}
            </div>
            <div className="text-sm text-gray-400">
              Last updated: {latestSnapshot.generated_at ? new Date(latestSnapshot.generated_at).toLocaleString() : 'Unknown'}
            </div>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
            <div className="text-sm text-gray-400 mb-1">Total Snapshots</div>
            <div className="text-4xl font-bold text-white">{timelineData.snapshots.length}</div>
            <div className="text-xs text-gray-500 mt-1">health checks recorded</div>
          </div>
          <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
            <div className="text-sm text-gray-400 mb-1">Ready Status</div>
            <div className="text-4xl font-bold text-green-400">{modeCounts['ready'] || 0}</div>
            <div className="text-xs text-gray-500 mt-1">times database was ready</div>
          </div>
          <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
            <div className="text-sm text-gray-400 mb-1">Issues Detected</div>
            <div className="text-4xl font-bold text-red-400">
              {(modeCounts['partial'] || 0) + (modeCounts['db_off'] || 0)}
            </div>
            <div className="text-xs text-gray-500 mt-1">partial or offline states</div>
          </div>
        </div>

        {/* Timeline History */}
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
          <h2 className="text-lg font-semibold mb-4 text-white">Health Timeline</h2>
          {timelineData.snapshots.length > 0 ? (
            <div className="space-y-3">
              {[...timelineData.snapshots].reverse().map((snapshot, index) => (
                <div
                  key={index}
                  className={`bg-gray-900 rounded-lg border p-4 ${snapshot.ok ? 'border-green-600/50' : 'border-red-600/50'}`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${getModeBadge(snapshot.mode)}`}>
                          {snapshot.mode}
                        </span>
                        <span className={`text-sm font-medium ${getModeColor(snapshot.mode)}`}>
                          {snapshot.ok ? '✓ Healthy' : '✗ Unhealthy'}
                        </span>
                      </div>
                      <div className="text-sm text-gray-300 mb-1">{snapshot.notes}</div>
                      <div className="text-xs text-gray-500">
                        {new Date(snapshot.generated_at).toLocaleString()}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center text-gray-400 py-8">
              No timeline data available
            </div>
          )}
        </div>

        {/* Mode Distribution */}
        {Object.keys(modeCounts).length > 0 && (
          <div className="bg-gray-800 rounded-lg border border-gray-700 p-6 mt-6">
            <h2 className="text-lg font-semibold mb-4 text-white">Status Distribution</h2>
            <div className="space-y-2">
              {Object.entries(modeCounts)
                .sort(([, a], [, b]) => b - a)
                .map(([mode, count]) => {
                  const percentage = ((count / timelineData.snapshots.length) * 100).toFixed(1);
                  return (
                    <div key={mode} className="flex items-center gap-4">
                      <div className="w-24 text-sm text-gray-400 capitalize">{mode}</div>
                      <div className="flex-1 bg-gray-900 rounded-full h-6 relative overflow-hidden">
                        <div
                          className={`h-full ${getModeBgColor(mode).split(' ')[0]} flex items-center justify-end pr-2`}
                          style={{ width: `${percentage}%` }}
                        >
                          <span className="text-xs font-medium text-white">{count}</span>
                        </div>
                      </div>
                      <div className="w-16 text-sm text-gray-300 text-right">{percentage}%</div>
                    </div>
                  );
                })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DBInsightsPage;


