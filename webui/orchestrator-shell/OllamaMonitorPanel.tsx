import React, { useState, useEffect } from 'react';
import type { OllamaMonitorSnapshot, OllamaRequestLog } from './types/ollamaMonitor';

function statusColor(status: OllamaRequestLog["status"]): string {
  switch (status) {
    case "success":
      return "text-green-600";
    case "error":
      return "text-red-600";
    case "pending":
    default:
      return "text-yellow-600";
  }
}

function statusBgColor(status: OllamaRequestLog["status"]): string {
  switch (status) {
    case "success":
      return "bg-green-50";
    case "error":
      return "bg-red-50";
    case "pending":
    default:
      return "bg-yellow-50";
  }
}

export default function OllamaMonitorPanel() {
  const [data, setData] = useState<OllamaMonitorSnapshot | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function fetchData() {
    try {
      setIsLoading(true);
      const res = await fetch("/api/ollama/monitor");
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();
      setData(json);
      setError(null);
    } catch (err: any) {
      setError(err?.message ?? "Failed to load monitor data");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    fetchData();
    const id = setInterval(fetchData, 2000); // Poll every 2 seconds
    return () => clearInterval(id);
  }, []);

  // Calculate summary stats
  const stats = data ? {
    totalRecent: data.recentRequests.length,
    errors: data.recentRequests.filter(r => r.status === "error").length,
    avgDuration: data.recentRequests.length > 0
      ? Math.round(
          data.recentRequests
            .filter(r => r.durationMs != null)
            .reduce((sum, r) => sum + (r.durationMs || 0), 0) /
          data.recentRequests.filter(r => r.durationMs != null).length
        )
      : 0,
  } : null;

  return (
    <div className="rounded-2xl border border-gray-200 p-4 space-y-4 bg-white">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">Ollama Monitor</h2>
        <button
          onClick={fetchData}
          disabled={isLoading}
          className="text-sm px-3 py-1 rounded border border-gray-300 hover:bg-gray-50 disabled:opacity-50"
        >
          {isLoading ? "Loading..." : "Refresh"}
        </button>
      </div>

      {isLoading && !data && (
        <div className="text-sm text-gray-500">Loading...</div>
      )}

      {error && (
        <div className="text-sm text-red-600 bg-red-50 p-2 rounded">
          Error: {error}
        </div>
      )}

      {data && (
        <>
          <div className="text-xs text-gray-500">
            Last updated: {new Date(data.lastUpdated).toLocaleTimeString()}
          </div>

          {/* Summary Stats */}
          {stats && (
            <div className="grid grid-cols-3 gap-2">
              <div className="bg-gray-50 p-2 rounded text-center">
                <div className="text-xs text-gray-500">Recent</div>
                <div className="text-lg font-semibold">{stats.totalRecent}</div>
              </div>
              <div className="bg-gray-50 p-2 rounded text-center">
                <div className="text-xs text-gray-500">Errors</div>
                <div className="text-lg font-semibold text-red-600">{stats.errors}</div>
              </div>
              <div className="bg-gray-50 p-2 rounded text-center">
                <div className="text-xs text-gray-500">Avg Duration</div>
                <div className="text-lg font-semibold">{stats.avgDuration}ms</div>
              </div>
            </div>
          )}

          {/* Active Requests */}
          <div className="space-y-2">
            <h3 className="text-sm font-medium text-gray-900">Active Requests</h3>
            {data.activeRequests.length === 0 ? (
              <div className="text-xs text-gray-500 bg-gray-50 p-2 rounded">
                No active requests.
              </div>
            ) : (
              <div className="max-h-60 overflow-auto border border-gray-200 rounded">
                <table className="min-w-full text-xs">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-2 py-1 text-left text-gray-700">Status</th>
                      <th className="px-2 py-1 text-left text-gray-700">Model</th>
                      <th className="px-2 py-1 text-left text-gray-700">Endpoint</th>
                      <th className="px-2 py-1 text-left text-gray-700">Started</th>
                      <th className="px-2 py-1 text-left text-gray-700">Preview</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.activeRequests.map((r) => (
                      <tr key={r.id} className="border-t border-gray-100">
                        <td className={`px-2 py-1 ${statusColor(r.status)} font-medium`}>
                          {r.status}
                        </td>
                        <td className="px-2 py-1 text-gray-700">{r.model ?? "—"}</td>
                        <td className="px-2 py-1 text-gray-700">{r.endpoint}</td>
                        <td className="px-2 py-1 text-gray-700">
                          {new Date(r.timestamp).toLocaleTimeString()}
                        </td>
                        <td className="px-2 py-1 max-w-xs truncate text-gray-600">
                          {r.promptPreview ?? "—"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Recent Requests */}
          <div className="space-y-2">
            <h3 className="text-sm font-medium text-gray-900">Recent Requests</h3>
            {data.recentRequests.length === 0 ? (
              <div className="text-xs text-gray-500 bg-gray-50 p-2 rounded">
                No recent requests.
              </div>
            ) : (
              <div className="max-h-64 overflow-auto border border-gray-200 rounded">
                <table className="min-w-full text-xs">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-2 py-1 text-left text-gray-700">Status</th>
                      <th className="px-2 py-1 text-left text-gray-700">Model</th>
                      <th className="px-2 py-1 text-left text-gray-700">Endpoint</th>
                      <th className="px-2 py-1 text-left text-gray-700">Duration</th>
                      <th className="px-2 py-1 text-left text-gray-700">HTTP</th>
                      <th className="px-2 py-1 text-left text-gray-700">Tokens</th>
                      <th className="px-2 py-1 text-left text-gray-700">Prompt</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.recentRequests.map((r) => (
                      <tr
                        key={r.id}
                        className={`border-t border-gray-100 ${statusBgColor(r.status)}`}
                      >
                        <td className={`px-2 py-1 ${statusColor(r.status)} font-medium`}>
                          {r.status}
                        </td>
                        <td className="px-2 py-1 text-gray-700">{r.model ?? "—"}</td>
                        <td className="px-2 py-1 text-gray-700">{r.endpoint}</td>
                        <td className="px-2 py-1 text-gray-700">
                          {r.durationMs != null
                            ? `${Math.round(r.durationMs)} ms`
                            : "—"}
                        </td>
                        <td className="px-2 py-1 text-gray-700">
                          {r.httpStatus ?? "—"}
                        </td>
                        <td className="px-2 py-1 text-gray-700">
                          {r.outputTokens != null ? r.outputTokens : "—"}
                        </td>
                        <td className="px-2 py-1 max-w-xs truncate text-gray-600">
                          {r.promptPreview ?? "—"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}

