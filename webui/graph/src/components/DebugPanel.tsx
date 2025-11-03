import React, { useState } from 'react';
import { usePerformance } from '../hooks/usePerformance';
import { theme } from '../styles/theme';

/**
 * Phase 4: Debug Panel for Performance Monitoring
 * Detailed performance metrics display with collapsible sections
 * ARIA-compliant with keyboard navigation
 */
interface DebugPanelProps {
  /** Show/hide toggle from parent */
  isVisible: boolean;
  /** Callback to hide panel */
  onClose: () => void;
  /** Additional metrics from GraphView */
  graphMetrics?: {
    visibleNodes: number;
    totalNodes: number;
    visibleEdges: number;
    totalEdges: number;
    zoomLevel: number;
    isLargeDataset: boolean;
  };
}

const DebugPanel: React.FC<DebugPanelProps> = ({
  isVisible,
  onClose,
  graphMetrics
}) => {
  const { metrics, recommendations } = usePerformance();
  const [activeTab, setActiveTab] = useState<'metrics' | 'recommendations' | 'graph'>('metrics');

  if (!isVisible) return null;

  const formatMetric = (value: number | undefined, unit: string = '', decimals: number = 1): string => {
    if (value === undefined) return 'N/A';
    return `${value.toFixed(decimals)}${unit}`;
  };

  const getStatusColor = (value: number, thresholds: { good: number; warn: number }): string => {
    if (value <= thresholds.good) return theme.colors.status.success;
    if (value <= thresholds.warn) return theme.colors.status.warning;
    return theme.colors.status.error;
  };

  const getStatusIcon = (value: number, thresholds: { good: number; warn: number }): string => {
    if (value <= thresholds.good) return '✅';
    if (value <= thresholds.warn) return '⚠️';
    return '❌';
  };

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      role="dialog"
      aria-modal="true"
      aria-labelledby="debug-panel-title"
      onKeyDown={(e) => {
        if (e.key === 'Escape') onClose();
      }}
    >
      <div
        className="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[80vh] overflow-hidden"
        style={{
          background: theme.colors.gradients.card,
          boxShadow: theme.shadows.xl
        }}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2
            id="debug-panel-title"
            className="text-xl font-semibold text-gray-900"
            style={{ color: theme.colors.text.primary }}
          >
            Performance Debug Panel
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
            style={{
              transition: `color ${theme.animations.duration.fast} ${theme.animations.easing.ease}`
            }}
            aria-label="Close debug panel"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-gray-200" role="tablist">
          {[
            { id: 'metrics', label: 'Core Metrics', count: 8 },
            { id: 'recommendations', label: 'Recommendations', count: recommendations.length },
            { id: 'graph', label: 'Graph Stats', count: graphMetrics ? 6 : 0 }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as typeof activeTab)}
              className={`flex-1 py-3 px-4 text-sm font-medium transition-colors ${
                activeTab === tab.id
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
              role="tab"
              aria-selected={activeTab === tab.id}
              aria-controls={`${tab.id}-panel`}
            >
              {tab.label}
              {tab.count > 0 && (
                <span className="ml-2 bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full text-xs">
                  {tab.count}
                </span>
              )}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="p-6 overflow-y-auto max-h-96">
          {/* Metrics Tab */}
          {activeTab === 'metrics' && (
            <div id="metrics-panel" role="tabpanel" aria-labelledby="metrics-tab">
              <h3 className="text-lg font-medium mb-4" style={{ color: theme.colors.text.primary }}>
                Core Performance Metrics
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* TTI */}
                <div className="bg-white p-4 rounded-lg border">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-600">Time to Interactive</span>
                    <span className="text-lg">
                      {getStatusIcon(metrics.tti, { good: 500, warn: 1000 })}
                    </span>
                  </div>
                  <div
                    className="text-2xl font-bold"
                    style={{ color: getStatusColor(metrics.tti, { good: 500, warn: 1000 }) }}
                  >
                    {formatMetric(metrics.tti, 'ms', 0)}
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    Target: &lt;500ms (good), &lt;1000ms (acceptable)
                  </div>
                </div>

                {/* FPS */}
                <div className="bg-white p-4 rounded-lg border">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-600">Frames per Second</span>
                    <span className="text-lg">
                      {getStatusIcon(metrics.fps, { good: 50, warn: 30 })}
                    </span>
                  </div>
                  <div
                    className="text-2xl font-bold"
                    style={{ color: getStatusColor(metrics.fps, { good: 50, warn: 30 }) }}
                  >
                    {formatMetric(metrics.fps, ' FPS')}
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    Target: &gt;50 FPS (smooth), &gt;30 FPS (acceptable)
                  </div>
                </div>

                {/* Memory */}
                {metrics.memoryUsage && (
                  <div className="bg-white p-4 rounded-lg border">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-600">Memory Usage</span>
                      <span className="text-lg">
                        {getStatusIcon(metrics.memoryUsage, { good: 100, warn: 150 })}
                      </span>
                    </div>
                    <div
                      className="text-2xl font-bold"
                      style={{ color: getStatusColor(metrics.memoryUsage, { good: 100, warn: 150 }) }}
                    >
                      {formatMetric(metrics.memoryUsage, ' MB')}
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      Target: &lt;100MB (good), &lt;150MB (acceptable)
                    </div>
                  </div>
                )}

                {/* DOM Nodes */}
                <div className="bg-white p-4 rounded-lg border">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-600">DOM Nodes</span>
                    <span className="text-lg">
                      {getStatusIcon(metrics.domNodes, { good: 5000, warn: 10000 })}
                    </span>
                  </div>
                  <div
                    className="text-2xl font-bold"
                    style={{ color: getStatusColor(metrics.domNodes, { good: 5000, warn: 10000 }) }}
                  >
                    {metrics.domNodes.toLocaleString()}
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    Target: &lt;5K (good), &lt;10K (acceptable)
                  </div>
                </div>

                {/* Render Time */}
                <div className="bg-white p-4 rounded-lg border">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-600">Render Time</span>
                    <span className="text-lg">
                      {getStatusIcon(metrics.renderTime, { good: 16, warn: 33 })}
                    </span>
                  </div>
                  <div
                    className="text-2xl font-bold"
                    style={{ color: getStatusColor(metrics.renderTime, { good: 16, warn: 33 }) }}
                  >
                    {formatMetric(metrics.renderTime, 'ms', 1)}
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    Target: &lt;16ms (60 FPS), &lt;33ms (30 FPS)
                  </div>
                </div>

                {/* Timestamp */}
                <div className="bg-white p-4 rounded-lg border md:col-span-2">
                  <div className="text-sm font-medium text-gray-600 mb-2">Last Updated</div>
                  <div className="text-lg font-bold" style={{ color: theme.colors.text.primary }}>
                    {new Date(metrics.timestamp).toLocaleTimeString()}
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    Metrics refresh automatically during interaction
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Recommendations Tab */}
          {activeTab === 'recommendations' && (
            <div id="recommendations-panel" role="tabpanel" aria-labelledby="recommendations-tab">
              <h3 className="text-lg font-medium mb-4" style={{ color: theme.colors.text.primary }}>
                Performance Recommendations
              </h3>
              {recommendations.length === 0 ? (
                <div className="text-center py-8">
                  <div className="text-green-500 text-4xl mb-4">✅</div>
                  <p className="text-gray-600">No performance issues detected!</p>
                  <p className="text-sm text-gray-500 mt-2">
                    All metrics are within acceptable ranges.
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  {recommendations.map((rec, index) => (
                    <div
                      key={index}
                      className={`p-4 rounded-lg border ${
                        rec.priority === 'high' ? 'border-red-200 bg-red-50' :
                        rec.priority === 'medium' ? 'border-yellow-200 bg-yellow-50' :
                        'border-blue-200 bg-blue-50'
                      }`}
                    >
                      <div className="flex items-start">
                        <div className="flex-shrink-0 mr-3">
                          {rec.priority === 'high' ? '🔴' :
                           rec.priority === 'medium' ? '🟡' : '🔵'}
                        </div>
                        <div className="flex-1">
                          <h4 className="font-medium text-gray-900 mb-2">{rec.message}</h4>
                          <div className="text-sm text-gray-700 mb-3">
                            <strong>Priority:</strong> {rec.priority.charAt(0).toUpperCase() + rec.priority.slice(1)}
                          </div>
                          <div className="space-y-1">
                            <div className="text-sm font-medium text-gray-700">Recommended Actions:</div>
                            <ul className="text-sm text-gray-600 space-y-1 ml-4">
                              {rec.actions.map((action, actionIndex) => (
                                <li key={actionIndex} className="flex items-start">
                                  <span className="text-gray-400 mr-2">•</span>
                                  {action}
                                </li>
                              ))}
                            </ul>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Graph Stats Tab */}
          {activeTab === 'graph' && (
            <div id="graph-panel" role="tabpanel" aria-labelledby="graph-tab">
              <h3 className="text-lg font-medium mb-4" style={{ color: theme.colors.text.primary }}>
                Graph Rendering Statistics
              </h3>
              {graphMetrics ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Node Stats */}
                  <div className="bg-white p-4 rounded-lg border">
                    <div className="text-sm font-medium text-gray-600 mb-2">Node Rendering</div>
                    <div className="text-2xl font-bold" style={{ color: theme.colors.text.primary }}>
                      {graphMetrics.visibleNodes.toLocaleString()} / {graphMetrics.totalNodes.toLocaleString()}
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      Visible / Total nodes ({((graphMetrics.visibleNodes / graphMetrics.totalNodes) * 100).toFixed(1)}%)
                    </div>
                    {graphMetrics.isLargeDataset && (
                      <div className="mt-2 text-xs text-blue-600 font-medium">
                        Large dataset mode active
                      </div>
                    )}
                  </div>

                  {/* Edge Stats */}
                  <div className="bg-white p-4 rounded-lg border">
                    <div className="text-sm font-medium text-gray-600 mb-2">Edge Rendering</div>
                    <div className="text-2xl font-bold" style={{ color: theme.colors.text.primary }}>
                      {graphMetrics.visibleEdges.toLocaleString()} / {graphMetrics.totalEdges.toLocaleString()}
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      Visible / Total edges ({((graphMetrics.visibleEdges / graphMetrics.totalEdges) * 100).toFixed(1)}%)
                    </div>
                  </div>

                  {/* Zoom Level */}
                  <div className="bg-white p-4 rounded-lg border">
                    <div className="text-sm font-medium text-gray-600 mb-2">Zoom Level</div>
                    <div className="text-2xl font-bold" style={{ color: theme.colors.text.primary }}>
                      {graphMetrics.zoomLevel.toFixed(2)}x
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      {graphMetrics.zoomLevel < 1 ? 'Zoomed out' :
                       graphMetrics.zoomLevel > 1 ? 'Zoomed in' : 'Default zoom'}
                    </div>
                  </div>

                  {/* Performance Impact */}
                  <div className="bg-white p-4 rounded-lg border">
                    <div className="text-sm font-medium text-gray-600 mb-2">Rendering Efficiency</div>
                    <div className="text-2xl font-bold" style={{
                      color: graphMetrics.visibleNodes / graphMetrics.totalNodes < 0.1 ?
                        theme.colors.status.success : theme.colors.status.warning
                    }}>
                      {((graphMetrics.visibleNodes / graphMetrics.totalNodes) * 100).toFixed(1)}%
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      {graphMetrics.visibleNodes / graphMetrics.totalNodes < 0.1 ?
                        'Excellent culling efficiency' :
                        'Consider zoom for better performance'}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <div className="text-gray-400 text-4xl mb-4">📊</div>
                  <p className="text-gray-600">Graph metrics not available</p>
                  <p className="text-sm text-gray-500 mt-2">
                    Graph statistics will appear here when a graph is rendered.
                  </p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex justify-end gap-3 p-6 border-t border-gray-200">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
            style={{
              transition: `all ${theme.animations.duration.fast} ${theme.animations.easing.ease}`
            }}
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default DebugPanel;
