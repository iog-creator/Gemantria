// PLAN-081: Graph Stats Tile — shows network metrics at a glance
import React from 'react';
import { GraphStatsSummary } from '../api';

interface GraphStatsTileProps {
  stats: GraphStatsSummary | null;
  className?: string;
}

const GraphStatsTile: React.FC<GraphStatsTileProps> = ({ stats, className = '' }) => {
  if (!stats) {
    return (
      <div className={`bg-gray-50 border border-gray-200 rounded-lg p-4 ${className}`}>
        <h3 className="text-base font-semibold mb-3 text-gray-900">Graph Stats</h3>
        <div className="text-sm text-gray-600">
          <span className="text-gray-500">Loading data…</span>
        </div>
      </div>
    );
  }

  if (!stats.ok) {
    return (
      <div className={`bg-gray-50 border border-gray-200 rounded-lg p-4 ${className}`}>
        <h3 className="text-base font-semibold mb-3 text-gray-900">Graph Stats</h3>
        <div className="text-sm text-gray-600">
          <div className="text-gray-500">Data unavailable (safe fallback).</div>
          {stats.error && (
            <p className="text-xs text-muted-foreground mt-1">{stats.error}</p>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-gray-50 border border-gray-200 rounded-lg p-4 ${className}`}>
      <h3 className="text-base font-semibold mb-3 text-gray-900">Graph Stats</h3>
      <div className="text-sm text-gray-600 space-y-2">
        <div className="flex justify-between items-center">
          <span className="text-gray-700">Nodes:</span>
          <span className="font-semibold text-gray-900">
            {stats.nodes !== null ? stats.nodes.toLocaleString() : '-'}
          </span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-gray-700">Edges:</span>
          <span className="font-semibold text-gray-900">
            {stats.edges !== null ? stats.edges.toLocaleString() : '-'}
          </span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-gray-700">Clusters:</span>
          <span className="font-semibold text-gray-900">
            {stats.clusters !== null ? stats.clusters.toLocaleString() : '-'}
          </span>
        </div>
        {stats.density !== null && (
          <div className="flex justify-between items-center pt-2 border-t border-gray-200">
            <span className="text-gray-700">Density:</span>
            <span className="text-gray-600 text-xs">
              {stats.density.toFixed(4)}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

export default GraphStatsTile;

