import React from "react";

type EdgeClass = "strong_edges" | "weak_edges" | "very_weak_edges";

function useCorrelationData(): { stats: any; correlations: any } {
  let stats = { edge_distribution: {} };
  let correlations = { correlations: [], metadata: {} };

  try {
    stats = require("../../out/graph_stats.json");
  } catch (e) {
    console.warn("graph_stats.json not found, using defaults");
  }

  try {
    correlations = require("../../out/graph_correlations.json");
  } catch (e) {
    console.warn("graph_correlations.json not found, using defaults");
  }

  return { stats, correlations };
}

const CorrelationPanel: React.FC = () => {
  const { stats, correlations } = useCorrelationData();

  const edgeDist = stats.edge_distribution || {};
  const totalEdges = (edgeDist.strong_edges || 0) + (edgeDist.weak_edges || 0) + (edgeDist.very_weak_edges || 0);
  const blendFormula = "edge_strength = α*cosine + (1-α)*rerank_score";

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Correlation Analytics (Phase-10)</h1>

      {/* SSOT Blend Badge */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <h2 className="text-lg font-semibold text-blue-800 mb-2">SSOT Blend Configuration</h2>
        <code className="text-sm text-blue-700 font-mono">{blendFormula}</code>
        <div className="mt-2 text-xs text-blue-600">
          α = EDGE_ALPHA (default: 0.5) • Validated against Rule-045
        </div>
      </div>

      {/* Edge Distribution */}
      <div className="bg-white border rounded-lg p-4 mb-6">
        <h2 className="text-lg font-semibold mb-4">Edge Strength Distribution</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center p-3 bg-green-50 rounded">
            <div className="text-2xl font-bold text-green-700">{edgeDist.strong_edges || 0}</div>
            <div className="text-sm text-green-600">Strong Edges (≥0.90)</div>
          </div>
          <div className="text-center p-3 bg-yellow-50 rounded">
            <div className="text-2xl font-bold text-yellow-700">{edgeDist.weak_edges || 0}</div>
            <div className="text-sm text-yellow-600">Weak Edges (≥0.75)</div>
          </div>
          <div className="text-center p-3 bg-red-50 rounded">
            <div className="text-2xl font-bold text-red-700">{edgeDist.very_weak_edges || 0}</div>
            <div className="text-sm text-red-600">Very Weak Edges (&lt;0.75)</div>
          </div>
        </div>
        <div className="mt-4 text-sm text-gray-600">
          Total Edges: {totalEdges} • Density: {(stats.density || 0).toFixed(4)}
        </div>
      </div>

      {/* Correlation Metadata */}
      <div className="bg-white border rounded-lg p-4">
        <h2 className="text-lg font-semibold mb-4">Cross-Text Patterns</h2>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>Total Correlations: {correlations.metadata?.total_correlations || 0}</div>
          <div>Significant: {correlations.metadata?.significant_correlations || 0}</div>
        </div>
        {correlations.correlations?.length === 0 && (
          <div className="mt-4 text-gray-500 italic">
            No strong correlations found (≥0.4 threshold). Enable scipy for advanced correlation analysis.
          </div>
        )}
      </div>
    </div>
  );
};

export default CorrelationPanel;
