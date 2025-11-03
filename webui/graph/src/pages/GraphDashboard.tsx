import { useState, useEffect } from "react";
import GraphView from "../components/GraphView";
import NodeDetails from "../components/NodeDetails";
import GraphStats from "../components/GraphStats";
import GraphPreview from "../components/GraphPreview";
import { useGraphData } from "../hooks/useGraphData";
import { usePerformance } from "../hooks/usePerformance";
import { GraphNode } from "../types/graph";

export default function GraphDashboard() {
  const { data, loading, error } = useGraphData();
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [showEscalationModal, setShowEscalationModal] = useState(false);

  // Performance monitoring for escalation decisions
  const { metrics, recommendations, measureTTI, needsWebGL } = usePerformance({
    thresholds: {
      tti: 3000, // 3s threshold for WebGL escalation
      fps: 20,   // Lower FPS threshold
      memory: 200, // Higher memory threshold
      renderTime: 16, // 16ms for 60fps
    }
  });

  // Check for escalation conditions
  useEffect(() => {
    if (!data.nodes) return;

    const nodeCount = data.nodes.length;
    const shouldEscalate =
      nodeCount > 50000 || // Large dataset
      (metrics.tti > 3000 && nodeCount > 10000) || // Slow TTI + medium dataset
      needsWebGL; // Performance hook recommends WebGL

    if (shouldEscalate && !showEscalationModal) {
      // Check if escalation.json exists and what it says
      fetch('/var/ui/escalation.json')
        .then(res => res.ok ? res.json() : null)
        .then(escalationData => {
          const alreadyEscalated = escalationData?.webgl_enabled;
          if (!alreadyEscalated) {
            setShowEscalationModal(true);
          }
        })
        .catch(() => {
          // No escalation.json, show modal
          setShowEscalationModal(true);
        });
    }
  }, [data.nodes, metrics.tti, needsWebGL, showEscalationModal]);

  // Measure TTI on data load
  useEffect(() => {
    if (data.nodes && !loading) {
      measureTTI();
    }
  }, [data.nodes, loading, measureTTI]);

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
            {/* Graph Preview for large datasets */}
            <GraphPreview data={data} />

            {/* Stats Panel */}
            <div className="bg-white rounded-lg shadow-lg p-4">
              <h2 className="text-xl font-semibold mb-4">Network Statistics</h2>
              <GraphStats />
            </div>

            {/* Graph Visualization */}
            <div className="bg-white rounded-lg shadow-lg p-4">
              <h2 className="text-xl font-semibold mb-4">
                Network Visualization
                {data.nodes?.length > 10000 && (
                  <span className="ml-2 text-sm font-normal text-gray-600">
                    (Large dataset mode enabled)
                  </span>
                )}
              </h2>
              <div className="h-96 lg:h-[600px]">
                <GraphView
                  nodes={data.nodes}
                  edges={data.edges}
                  width={800}
                  height={600}
                  onNodeSelect={setSelectedNode}
                />
              </div>
            </div>
          </div>

          {/* Node Details - Takes up 1/4 of the space */}
          <div className="lg:col-span-1">
            <NodeDetails node={selectedNode} />
          </div>
        </main>

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

      {/* WebGL Escalation Modal */}
      {showEscalationModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" role="dialog" aria-modal="true">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
            <div className="flex items-center mb-4">
              <div className="flex-shrink-0">
                <svg className="h-6 w-6 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
              </div>
              <h3 className="ml-3 text-lg font-medium text-gray-900">
                Performance Optimization Available
              </h3>
            </div>

            <div className="mb-4">
              <p className="text-sm text-gray-600 mb-2">
                This dataset ({data.nodes?.length.toLocaleString()} nodes) may perform better with WebGL rendering.
              </p>

              {metrics.tti > 1000 && (
                <p className="text-sm text-gray-600">
                  Current TTI: {metrics.tti.toFixed(0)}ms
                  {metrics.tti > 3000 && " (Slow)"}
                </p>
              )}

              {recommendations.length > 0 && (
                <div className="mt-3">
                  <p className="text-sm font-medium text-gray-700 mb-1">Recommendations:</p>
                  <ul className="text-sm text-gray-600 space-y-1">
                    {recommendations.slice(0, 2).map((rec, i) => (
                      <li key={i} className="flex items-start">
                        <span className="text-yellow-500 mr-1">•</span>
                        {rec.message}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => {
                  // Enable WebGL mode (create escalation.json)
                  fetch('/api/escalation', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                      webgl_enabled: true,
                      timestamp: new Date().toISOString(),
                      reason: 'user_escalation',
                      node_count: data.nodes?.length,
                      performance_metrics: metrics
                    })
                  }).catch(() => {
                    // Fallback: create local escalation stub
                    console.log('WebGL escalation requested');
                  });

                  setShowEscalationModal(false);
                  // TODO: Trigger WebGL renderer switch
                }}
                className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              >
                Enable WebGL Mode
              </button>

              <button
                onClick={() => setShowEscalationModal(false)}
                className="flex-1 bg-gray-300 text-gray-700 px-4 py-2 rounded-md text-sm font-medium hover:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
              >
                Continue with SVG
              </button>
            </div>

            <p className="text-xs text-gray-500 mt-3 text-center">
              WebGL provides hardware-accelerated graphics for better performance with large datasets.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
