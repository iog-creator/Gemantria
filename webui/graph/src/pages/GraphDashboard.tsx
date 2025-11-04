import { useState, useEffect } from "react";
import { ErrorBoundary } from 'react-error-boundary';
import GraphView from "../components/GraphView";
import NodeDetails from "../components/NodeDetails";
import GraphStats from "../components/GraphStats";
import { useGraphData } from "../hooks/useGraphData";
import { GraphNode } from "../types/graph";
// Import dashboard components for integration
import TemporalExplorer from "../../../dashboard/src/components/TemporalExplorer";
import ForecastPanel from "../../../dashboard/src/components/ForecastPanel";
import MetricsPanel from "../../../dashboard/src/components/MetricsPanel";
import PatternExplorer from "../../../dashboard/src/components/PatternExplorer";

const Fallback = ({error}: {error: Error}) => (
  <div className="p-8 text-red-600 border-2 border-red-200 rounded-lg bg-red-50">
    <h2 className="text-xl font-bold mb-4">Oops – graph failed to render</h2>
    <pre className="bg-red-100 p-4 rounded text-sm mb-4 overflow-auto">{error.message}</pre>
    <button
      onClick={() => window.location.reload()}
      className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
    >
      Reload Page
    </button>
  </div>
);

export default function GraphDashboard() {
  const { data, loading, error } = useGraphData();
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [showEscalation, setShowEscalation] = useState(false);
  const [viewMode, setViewMode] = useState<'user' | 'dev'>('user'); // Toggle between user and dev views

  useEffect(() => {
    if (!data.nodes?.length) return;
    const dataSizeMB = JSON.stringify(data).length / (1024 * 1024);
    const canUseWebGL = () => {
      try {
        const canvas = document.createElement('canvas');
        return !!(canvas.getContext('webgl') || canvas.getContext('experimental-webgl'));
      } catch (e) {
        return false;
      }
    };
    if (dataSizeMB > 100 || !canUseWebGL()) {
      setShowEscalation(true);
    }
  }, [data]);

  if (showEscalation) {
    const dataSizeMB = JSON.stringify(data).length / (1024 * 1024);
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white p-8 rounded-lg shadow-xl max-w-md mx-4">
          <h2 className="text-xl font-bold mb-4 text-gray-800">Large Dataset Detected</h2>
          <p className="text-gray-600 mb-6">
            Enable WebGL for better performance? (Memory: {dataSizeMB.toFixed(1)}MB)
          </p>
          <div className="flex gap-3">
            <button
              onClick={() => {
                localStorage.setItem('enable_webgl', 'true');
                setShowEscalation(false);
              }}
              className="flex-1 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            >
              Enable WebGL
            </button>
            <button
              onClick={() => setShowEscalation(false)}
              className="flex-1 bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
            >
              Continue
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading graph data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="bg-white p-6 rounded-lg shadow-lg max-w-md">
          <h2 className="text-xl font-semibold text-red-600 mb-2">
            Error Loading Graph
          </h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Skip to main content link for accessibility */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 bg-blue-600 text-white px-4 py-2 rounded z-50"
      >
        Skip to main content
      </a>

      <div className="p-6">
      <div className="max-w-7xl mx-auto">
          {/* Header with navigation landmark */}
          <header className="mb-6">
            <nav aria-label="Main navigation">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Gematria Concept Network
          </h1>
            </nav>
            <div className="flex gap-4 text-sm text-gray-600" aria-label="Dataset summary">
            <span>Nodes: {data.nodes.length}</span>
            <span>Edges: {data.edges.length}</span>
            <span>
              Clusters:{" "}
              {new Set(data.nodes.map((n) => n.cluster).filter(Boolean)).size}
            </span>
          </div>
          </header>

        {/* Main Content */}
          <main id="main-content" className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Graph View - Takes up 3/4 of the space */}
          <div className="lg:col-span-3 space-y-6">
            {/* Stats Panel */}
            <div className="bg-white rounded-lg shadow-lg p-4">
              <h2 className="text-xl font-semibold mb-4">Network Statistics</h2>
              <GraphStats />
            </div>

            {/* Graph Visualization */}
            <div className="bg-white rounded-lg shadow-lg p-4">
              <h2 className="text-xl font-semibold mb-4">
                Network Visualization
              </h2>
              <div className="h-96 lg:h-[600px]">
                <ErrorBoundary FallbackComponent={Fallback}>
                  <GraphView
                    nodes={data.nodes}
                    edges={data.edges}
                    width={800}
                    height={600}
                    onNodeSelect={setSelectedNode}
                  />
                </ErrorBoundary>
              </div>
            </div>
          </div>

          {/* Node Details - Takes up 1/4 of the space */}
          <div className="lg:col-span-1">
            <NodeDetails node={selectedNode} />
          </div>
        </main>

        {/* Integrated Dashboard Components */}
        <div className="mt-8 max-w-7xl mx-auto">
          {/* View Mode Toggle */}
          <div className="mb-6 text-center">
            <div className="inline-flex rounded-lg bg-gray-100 p-1">
              <button
                onClick={() => setViewMode('user')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  viewMode === 'user'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                User Analytics
              </button>
              <button
                onClick={() => setViewMode('dev')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  viewMode === 'dev'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                Developer Metrics
              </button>
            </div>
          </div>

          {/* Conditional Dashboard Content */}
          <div className="space-y-6">
            {viewMode === 'user' ? (
              <>
                {/* Phase 8: Temporal Analytics */}
                <div className="bg-white rounded-lg shadow-lg p-6">
                  <h2 className="text-2xl font-bold mb-4">Temporal Pattern Analysis</h2>
                  <TemporalExplorer />
                </div>

                {/* Phase 8: Forecasting */}
                <div className="bg-white rounded-lg shadow-lg p-6">
                  <h2 className="text-2xl font-bold mb-4">Predictive Forecasting</h2>
                  <ForecastPanel />
                </div>
              </>
            ) : (
              <>
                {/* Developer Metrics */}
                <div className="bg-white rounded-lg shadow-lg p-6">
                  <h2 className="text-2xl font-bold mb-4">Advanced Metrics Dashboard</h2>
                  <MetricsPanel />
                </div>

                {/* Pattern Exploration */}
                <div className="bg-white rounded-lg shadow-lg p-6">
                  <h2 className="text-2xl font-bold mb-4">Cross-Book Pattern Analysis</h2>
                  <PatternExplorer />
                </div>
              </>
            )}
          </div>
        </div>

        {/* Footer */}
        <footer className="mt-6 text-center text-sm text-gray-500" role="contentinfo">
          <p>
            Graph data exported on{" "}
            {data.metadata?.export_timestamp
              ? new Date(data.metadata.export_timestamp).toLocaleString()
              : "Unknown"}
          </p>
        </footer>
        </div>
      </div>
    </div>
  );
}
