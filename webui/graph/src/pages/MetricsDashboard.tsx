import React, { useState, useEffect, useMemo } from 'react';
import { usePerformance, PerformanceMetrics } from '../hooks/usePerformance';
import PerformanceBadge from '../components/PerformanceBadge';
import DebugPanel from '../components/DebugPanel';
import { theme } from '../styles/theme';

/**
 * Phase 4: Metrics Dashboard
 * Development-focused metrics trends and analytics
 * D3-powered line charts for historical metrics with real-time data
 */
interface MetricsHistory {
  timestamp: number;
  tti: number;
  fps: number;
  memoryUsage?: number;
  domNodes: number;
  renderTime: number;
}

interface MetricsDashboardProps {
  /** Optional graph metrics from parent */
  graphMetrics?: {
    visibleNodes: number;
    totalNodes: number;
    visibleEdges: number;
    totalEdges: number;
    zoomLevel: number;
    isLargeDataset: boolean;
  };
}

const MetricsDashboard: React.FC<MetricsDashboardProps> = ({ graphMetrics }) => {
  const { metrics, recommendations } = usePerformance();
  const [history, setHistory] = useState<MetricsHistory[]>([]);
  const [timeRange, setTimeRange] = useState<'1m' | '5m' | '15m'>('5m');
  const [showDebugPanel, setShowDebugPanel] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);

  // Collect metrics history
  useEffect(() => {
    const newEntry: MetricsHistory = {
      timestamp: metrics.timestamp,
      tti: metrics.tti,
      fps: metrics.fps,
      memoryUsage: metrics.memoryUsage,
      domNodes: metrics.domNodes,
      renderTime: metrics.renderTime,
    };

    setHistory(prev => {
      const updated = [...prev, newEntry];
      // Keep only last 15 minutes of data (900 entries at 1s intervals)
      return updated.slice(-900);
    });
  }, [metrics]);

  // Filter history based on time range
  const filteredHistory = useMemo(() => {
    const now = Date.now();
    const ranges = {
      '1m': 60 * 1000,
      '5m': 5 * 60 * 1000,
      '15m': 15 * 60 * 1000,
    };

    const cutoff = now - ranges[timeRange];
    return history.filter(entry => entry.timestamp >= cutoff);
  }, [history, timeRange]);

  // Calculate trends
  const trends = useMemo(() => {
    if (filteredHistory.length < 2) return null;

    const recent = filteredHistory.slice(-10); // Last 10 entries
    const older = filteredHistory.slice(-20, -10); // Previous 10 entries

    const avgRecent = (metric: keyof PerformanceMetrics) => {
      const values = recent
        .map(h => h[metric])
        .filter(v => v !== undefined) as number[];
      return values.length > 0 ? values.reduce((a, b) => a + b, 0) / values.length : 0;
    };

    const avgOlder = (metric: keyof PerformanceMetrics) => {
      const values = older
        .map(h => h[metric])
        .filter(v => v !== undefined) as number[];
      return values.length > 0 ? values.reduce((a, b) => a + b, 0) / values.length : 0;
    };

    return {
      tti: { current: avgRecent('tti'), previous: avgOlder('tti') },
      fps: { current: avgRecent('fps'), previous: avgOlder('fps') },
      memoryUsage: {
        current: avgRecent('memoryUsage'),
        previous: avgOlder('memoryUsage')
      },
      domNodes: { current: avgRecent('domNodes'), previous: avgOlder('domNodes') },
      renderTime: { current: avgRecent('renderTime'), previous: avgOlder('renderTime') },
    };
  }, [filteredHistory]);

  const getTrendIcon = (current: number, previous: number) => {
    if (current < previous) return '📈'; // Improving
    if (current > previous) return '📉'; // Degrading
    return '➡️'; // Stable
  };

  const getTrendColor = (current: number, previous: number) => {
    if (current < previous) return theme.colors.status.success;
    if (current > previous) return theme.colors.status.error;
    return theme.colors.text.secondary;
  };

  // Simple sparkline component (could be replaced with D3)
  const Sparkline: React.FC<{ data: number[]; width: number; height: number }> = ({
    data, width, height
  }) => {
    if (data.length < 2) return null;

    const max = Math.max(...data);
    const min = Math.min(...data);
    const range = max - min || 1;

    const points = data.map((value, index) => {
      const x = (index / (data.length - 1)) * width;
      const y = height - ((value - min) / range) * height;
      return `${x},${y}`;
    }).join(' ');

    return (
      <svg width={width} height={height} className="overflow-visible">
        <polyline
          fill="none"
          stroke={theme.colors.primary}
          strokeWidth="1.5"
          points={points}
          vectorEffect="non-scaling-stroke"
        />
      </svg>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Performance Metrics Dashboard</h1>
              <p className="text-sm text-gray-600">Real-time performance monitoring and trends</p>
            </div>

            <div className="flex items-center gap-4">
              <PerformanceBadge
                onClick={() => setShowDebugPanel(true)}
                showDetails={true}
                size="md"
              />

              <div className="flex items-center gap-2">
                <label htmlFor="auto-refresh" className="text-sm text-gray-700">
                  Auto-refresh
                </label>
                <button
                  id="auto-refresh"
                  onClick={() => setAutoRefresh(!autoRefresh)}
                  className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-600 focus:ring-offset-2 ${
                    autoRefresh ? 'bg-blue-600' : 'bg-gray-200'
                  }`}
                  role="switch"
                  aria-checked={autoRefresh}
                >
                  <span
                    className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                      autoRefresh ? 'translate-x-5' : 'translate-x-0'
                    }`}
                  />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Time Range Selector */}
        <div className="mb-8">
          <div className="flex items-center gap-4">
            <span className="text-sm font-medium text-gray-700">Time Range:</span>
            {(['1m', '5m', '15m'] as const).map((range) => (
              <button
                key={range}
                onClick={() => setTimeRange(range)}
                className={`px-3 py-1 text-sm rounded-md transition-colors ${
                  timeRange === range
                    ? 'bg-blue-100 text-blue-700 border-blue-300'
                    : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                } border`}
              >
                {range === '1m' ? '1 min' : range === '5m' ? '5 min' : '15 min'}
              </button>
            ))}
          </div>
          <p className="text-xs text-gray-500 mt-1">
            Showing {filteredHistory.length} data points
          </p>
        </div>

        {/* Current Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {[
            { key: 'tti', label: 'Time to Interactive', unit: 'ms', format: (v: number) => v.toFixed(0) },
            { key: 'fps', label: 'Frames per Second', unit: 'FPS', format: (v: number) => v.toFixed(1) },
            { key: 'memoryUsage', label: 'Memory Usage', unit: 'MB', format: (v: number) => v.toFixed(0), optional: true },
            { key: 'domNodes', label: 'DOM Nodes', unit: '', format: (v: number) => v.toLocaleString() },
            { key: 'renderTime', label: 'Render Time', unit: 'ms', format: (v: number) => v.toFixed(1) },
          ].map(({ key, label, unit, format, optional }) => {
            const value = metrics[key as keyof PerformanceMetrics] as number | undefined;
            const historyData = filteredHistory.map(h => h[key as keyof MetricsHistory] as number).filter(v => v !== undefined);
            const trend = trends?.[key as keyof typeof trends];

            if (optional && !value) return null;

            return (
              <div key={key} className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-sm font-medium text-gray-600">{label}</h3>
                  {trend && (
                    <span className="text-lg" title={`Trend: ${trend.current > trend.previous ? 'Increasing' : trend.current < trend.previous ? 'Decreasing' : 'Stable'}`}>
                      {getTrendIcon(trend.current, trend.previous)}
                    </span>
                  )}
                </div>

                <div className="flex items-baseline gap-4">
                  <div className="text-3xl font-bold text-gray-900">
                    {value ? format(value) : 'N/A'}{unit && ` ${unit}`}
                  </div>

                  {/* Sparkline */}
                  {historyData.length > 1 && (
                    <div className="flex-1 h-8">
                      <Sparkline data={historyData} width={80} height={32} />
                    </div>
                  )}
                </div>

                {trend && (
                  <div className="mt-2 text-xs" style={{ color: getTrendColor(trend.current, trend.previous) }}>
                    {trend.current > trend.previous ? '↑' : trend.current < trend.previous ? '↓' : '→'}
                    {' '}
                    {Math.abs(((trend.current - trend.previous) / trend.previous) * 100).toFixed(1)}%
                    {' '}vs previous period
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Recommendations Section */}
        {recommendations.length > 0 && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 mb-8">
            <h2 className="text-lg font-medium text-yellow-800 mb-4">
              Performance Recommendations ({recommendations.length})
            </h2>
            <div className="space-y-3">
              {recommendations.map((rec, index) => (
                <div key={index} className="flex items-start gap-3">
                  <span className="text-lg">
                    {rec.priority === 'high' ? '🔴' : rec.priority === 'medium' ? '🟡' : '🔵'}
                  </span>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-yellow-800">{rec.message}</p>
                    <ul className="text-sm text-yellow-700 mt-1 ml-4 space-y-1">
                      {rec.actions.map((action, actionIndex) => (
                        <li key={actionIndex} className="flex items-start">
                          <span className="mr-2">•</span>
                          {action}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Graph Metrics (if available) */}
        {graphMetrics && (
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Graph Rendering Metrics</h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <div className="text-sm text-gray-600">Visible Nodes</div>
                <div className="text-2xl font-bold text-gray-900">
                  {graphMetrics.visibleNodes.toLocaleString()}
                </div>
                <div className="text-xs text-gray-500">
                  of {graphMetrics.totalNodes.toLocaleString()} total
                </div>
              </div>

              <div>
                <div className="text-sm text-gray-600">Visible Edges</div>
                <div className="text-2xl font-bold text-gray-900">
                  {graphMetrics.visibleEdges.toLocaleString()}
                </div>
                <div className="text-xs text-gray-500">
                  of {graphMetrics.totalEdges.toLocaleString()} total
                </div>
              </div>

              <div>
                <div className="text-sm text-gray-600">Zoom Level</div>
                <div className="text-2xl font-bold text-gray-900">
                  {graphMetrics.zoomLevel.toFixed(2)}x
                </div>
                <div className="text-xs text-gray-500">
                  {graphMetrics.zoomLevel < 1 ? 'Zoomed out' : graphMetrics.zoomLevel > 1 ? 'Zoomed in' : 'Default'}
                </div>
              </div>

              <div>
                <div className="text-sm text-gray-600">Culling Efficiency</div>
                <div className="text-2xl font-bold text-gray-900">
                  {((graphMetrics.visibleNodes / graphMetrics.totalNodes) * 100).toFixed(1)}%
                </div>
                <div className="text-xs text-gray-500">
                  Nodes visible in viewport
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Raw Data Export */}
        <div className="bg-gray-50 rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Export Metrics Data</h2>
          <div className="flex gap-4">
            <button
              onClick={() => {
                const data = JSON.stringify(filteredHistory, null, 2);
                const blob = new Blob([data], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `metrics-history-${timeRange}-${new Date().toISOString().slice(0, 19)}.json`;
                a.click();
                URL.revokeObjectURL(url);
              }}
              className="px-4 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 transition-colors"
            >
              Download JSON
            </button>

            <button
              onClick={() => {
                const csv = [
                  Object.keys(filteredHistory[0] || {}).join(','),
                  ...filteredHistory.map(row =>
                    Object.values(row).map(v => v || '').join(',')
                  )
                ].join('\n');
                const blob = new Blob([csv], { type: 'text/csv' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `metrics-history-${timeRange}-${new Date().toISOString().slice(0, 19)}.csv`;
                a.click();
                URL.revokeObjectURL(url);
              }}
              className="px-4 py-2 bg-green-600 text-white text-sm rounded-md hover:bg-green-700 transition-colors"
            >
              Download CSV
            </button>
          </div>
        </div>
      </div>

      {/* Debug Panel */}
      <DebugPanel
        isVisible={showDebugPanel}
        onClose={() => setShowDebugPanel(false)}
        graphMetrics={graphMetrics}
      />
    </div>
  );
};

export default MetricsDashboard;
