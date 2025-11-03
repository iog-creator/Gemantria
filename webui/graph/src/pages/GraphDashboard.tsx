import { useState } from "react";
import GraphView from "../components/GraphView";
import NodeDetails from "../components/NodeDetails";
import GraphStats from "../components/GraphStats";
import { useGraphData } from "../hooks/useGraphData";
import { GraphNode } from "../types/graph";

export default function GraphDashboard() {
  const { data, loading, error } = useGraphData();
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);

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
    </div>
  );
}
