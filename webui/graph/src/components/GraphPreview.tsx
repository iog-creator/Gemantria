import React, { useState, useMemo } from 'react';

/**
 * Phase 2.2: Lightweight preview for large datasets (>10k nodes)
 * Shows summary statistics and lazy-loaded paginated chunks
 */
interface GraphPreviewProps {
  /**
   * Unified envelope: { nodes, edges, temporal_patterns?, forecasts?, correlations? }
   * Per webui-contract.md; summaries computed from these.
   */
  data: any; // TODO: Type from contract
}

const GraphPreview: React.FC<GraphPreviewProps> = ({ data }) => {
  const [page, setPage] = useState(0);
  const [showDetails, setShowDetails] = useState(false);
  const pageSize = 1000; // Chunk for lazy load

  const totalNodes = data.nodes?.length ?? 0;
  const totalEdges = data.edges?.length ?? 0;
  const isLarge = totalNodes > 10000;

  // Only show for large datasets
  if (!isLarge) return null;

  // Lazy load: fetch page chunk (in real: API, here: slice mock)
  const loadPage = (p: number) => {
    // Sim: slice nodes; real: fetch `/graph/chunk?page=${p}`
    const chunk = data.nodes.slice(p * pageSize, (p + 1) * pageSize);
    return chunk;
  };

  const currentChunk = loadPage(page);
  const totalPages = Math.ceil(totalNodes / pageSize);

  // Summary stats: basic counts; add clusters/correlations later
  const stats = useMemo(() => ({
    nodes: totalNodes,
    edges: totalEdges,
    avgDegree: totalEdges * 2 / totalNodes || 0,
    temporalPatterns: data.temporal_patterns?.length ?? 0,
    forecasts: data.forecasts?.length ?? 0,
    correlations: data.correlations?.length ?? 0,
    clusters: new Set(data.nodes?.map((n: any) => n.cluster).filter(Boolean)).size,
  }), [data, totalNodes, totalEdges]);

  // Performance metrics
  const estimatedMemoryMB = (totalNodes * 0.1 + totalEdges * 0.05).toFixed(1);
  const estimatedTTI = Math.max(200, Math.min(3000, totalNodes * 0.01 + totalEdges * 0.005));

  return (
    <div className="graph-preview bg-white border border-gray-200 rounded-lg p-4 mb-4 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          Graph Preview (Large Dataset Mode)
        </h3>
        <div className="flex gap-2">
          <button
            onClick={() => setShowDetails(!showDetails)}
            className="px-3 py-1 text-sm bg-blue-50 text-blue-700 rounded hover:bg-blue-100 transition-colors"
          >
            {showDetails ? 'Hide Details' : 'Show Details'}
          </button>
        </div>
      </div>

      {/* Summary Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
        {Object.entries(stats).map(([key, val]) => (
          <div key={key} className="bg-gray-50 p-3 rounded-lg">
            <div className="text-sm text-gray-600 capitalize">
              {key.replace(/([A-Z])/g, ' $1').trim()}
            </div>
            <div className="text-lg font-semibold text-gray-900">
              {typeof val === 'number' ? val.toLocaleString() : val}
            </div>
          </div>
        ))}
      </div>

      {/* Performance Estimates */}
      {showDetails && (
        <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
          <h4 className="text-sm font-medium text-yellow-800 mb-2">Performance Estimates</h4>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-600">Estimated Memory:</span>
              <span className="ml-2 font-medium">~{estimatedMemoryMB} MB</span>
            </div>
            <div>
              <span className="text-gray-600">Estimated TTI:</span>
              <span className="ml-2 font-medium">~{estimatedTTI.toFixed(0)}ms</span>
            </div>
          </div>
          <p className="text-xs text-yellow-700 mt-2">
            Full render may be slow. Use GraphView for detailed exploration with viewport culling.
          </p>
        </div>
      )}

      {/* Pagination Controls */}
      <div className="flex items-center justify-between mb-4">
        <div className="text-sm text-gray-600">
          Showing nodes {(page * pageSize) + 1}-{Math.min((page + 1) * pageSize, totalNodes)} of {totalNodes.toLocaleString()}
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setPage(Math.max(0, page - 1))}
            disabled={page === 0}
            className="px-3 py-1 text-sm border border-gray-300 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
          >
            Previous
          </button>
          <span className="px-3 py-1 text-sm bg-gray-100 rounded">
            Page {page + 1} of {totalPages}
          </span>
          <button
            onClick={() => setPage(Math.min(totalPages - 1, page + 1))}
            disabled={page >= totalPages - 1}
            className="px-3 py-1 text-sm border border-gray-300 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
          >
            Next
          </button>
        </div>
      </div>

      {/* Chunk Preview */}
      {showDetails && (
        <div className="border border-gray-200 rounded-lg p-3 max-h-60 overflow-y-auto">
          <h4 className="text-sm font-medium text-gray-700 mb-2">Node Sample (Page {page + 1})</h4>
          <div className="space-y-1 text-xs font-mono">
            {currentChunk.slice(0, 10).map((node: any, i: number) => (
              <div key={i} className="bg-gray-50 p-2 rounded text-gray-800">
                <span className="font-medium">Node {node.id}:</span> {JSON.stringify({
                  label: node.label,
                  cluster: node.cluster,
                  degree: node.degree,
                  gematria: node.gematria_value
                }, null, 0)}
              </div>
            ))}
            {currentChunk.length > 10 && (
              <div className="text-center text-gray-500 py-2">
                ... and {currentChunk.length - 10} more nodes
              </div>
            )}
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="mt-4 flex gap-2">
        <button
          onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
          className="px-4 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors"
        >
          View Full Graph
        </button>
        <button
          onClick={() => {/* TODO: Export summary */}}
          className="px-4 py-2 border border-gray-300 text-gray-700 text-sm rounded hover:bg-gray-50 transition-colors"
        >
          Export Summary
        </button>
      </div>
    </div>
  );
};

export default GraphPreview;
