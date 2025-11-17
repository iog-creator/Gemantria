// PLAN-081: MCP RO Proof Tile — shows endpoint count + last updated timestamp
import React, { useEffect, useState } from 'react';
import { fetchMcpCatalogSummary, McpCatalogSummary } from '../api';

interface MCPROProofTileProps {
  summary?: McpCatalogSummary | null;
  className?: string;
}

const MCPROProofTile: React.FC<MCPROProofTileProps> = ({ summary: propSummary, className = '' }) => {
  const [summary, setSummary] = useState<McpCatalogSummary | null>(propSummary || null);
  const [loading, setLoading] = useState(!propSummary);

  useEffect(() => {
    if (propSummary !== undefined) {
      setSummary(propSummary);
      setLoading(false);
      return;
    }

    // Load from API if no prop provided
    const loadData = async () => {
      try {
        const data = await fetchMcpCatalogSummary();
        setSummary(data);
      } catch (err) {
        console.debug('Failed to load MCP catalog summary:', err);
        setSummary({
          ok: false,
          endpoint_count: null,
          last_updated: null,
          error: 'Failed to load',
        });
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [propSummary]);

  if (loading) {
    return (
      <div className={`bg-gray-50 border border-gray-200 rounded-lg p-4 ${className}`}>
        <h3 className="text-base font-semibold mb-3 text-gray-900">MCP RO Proof</h3>
        <div className="text-sm text-gray-600">
          <span className="text-gray-500">Loading data…</span>
        </div>
      </div>
    );
  }

  if (!summary || !summary.ok) {
    return (
      <div className={`bg-gray-50 border border-gray-200 rounded-lg p-4 ${className}`}>
        <h3 className="text-base font-semibold mb-3 text-gray-900">MCP RO Proof</h3>
        <div className="text-sm text-gray-600">
          <div className="text-gray-500">Data unavailable (safe fallback).</div>
          {summary?.error && (
            <p className="text-xs text-muted-foreground mt-1">{summary.error}</p>
          )}
        </div>
      </div>
    );
  }

  const endpointCount = summary.endpoint_count ?? 0;
  const lastUpdated = summary.last_updated
    ? new Date(summary.last_updated).toLocaleString()
    : null;

  if (endpointCount === 0) {
    return (
      <div className={`bg-gray-50 border border-gray-200 rounded-lg p-4 ${className}`}>
        <h3 className="text-base font-semibold mb-3 text-gray-900">MCP RO Proof</h3>
        <div className="text-sm text-gray-600">
          <div className="text-gray-500">No MCP endpoints configured yet.</div>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-gray-50 border border-gray-200 rounded-lg p-4 ${className}`}>
      <h3 className="text-base font-semibold mb-3 text-gray-900">MCP RO Proof</h3>
      <div className="text-sm text-gray-600">
        <div className="mb-2">
          <strong className="text-gray-700">MCP endpoints:</strong>{' '}
          <span
            className={
              endpointCount > 0
                ? 'text-green-600 font-medium'
                : 'text-yellow-600 font-medium'
            }
          >
            {endpointCount}
          </span>
        </div>
        {lastUpdated && (
          <div className="text-xs text-muted-foreground">
            Last updated: {lastUpdated}
          </div>
        )}
      </div>
    </div>
  );
};

export default MCPROProofTile;

