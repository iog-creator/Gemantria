// webui/dashboard/ForecastDashboard.tsx
// Interactive forecast dashboard per ADR-025
// Phase-8: Orchestrator Dashboard with system health, LM, compliance, and KB tiles

import React, { useState, useEffect } from 'react';
import {
  fetchOrchestratorSnapshot,
  OrchestratorDashboardSnapshot,
} from './api';

interface ForecastData {
  forecast: number[];
  rmse: number;
  model: string;
  confidence_intervals?: number[][];
}

interface TemporalData {
  rolling_mean: number[];
  change_points: number[];
  metadata: {
    series_length: number;
    window_size: number;
    volatility: number;
    trend_slope: number;
  };
}

const ForecastDashboard: React.FC = () => {
  // Orchestrator dashboard state
  const [orchestratorData, setOrchestratorData] = useState<OrchestratorDashboardSnapshot | null>(null);
  const [orchestratorLoading, setOrchestratorLoading] = useState(true);
  const [orchestratorError, setOrchestratorError] = useState<string | null>(null);

  // Temporal analytics state
  const [forecastData, setForecastData] = useState<ForecastData | null>(null);
  const [temporalData, setTemporalData] = useState<TemporalData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load orchestrator snapshot with auto-refresh
  useEffect(() => {
    let cancelled = false;

    async function loadOrchestrator() {
      try {
        const snapshot = await fetchOrchestratorSnapshot();
        if (!cancelled) {
          setOrchestratorData(snapshot);
          setOrchestratorError(null);
        }
      } catch (e) {
        if (!cancelled) {
          setOrchestratorError(e instanceof Error ? e.message : 'Data unavailable');
        }
      } finally {
        if (!cancelled) {
          setOrchestratorLoading(false);
        }
      }
    }

    loadOrchestrator();
    const id = setInterval(loadOrchestrator, 30000); // 30s auto-refresh

    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, []);

  useEffect(() => {
    const loadData = async () => {
      try {
        // Load forecast data
        const forecastResponse = await fetch('/temporal/forecast?model=naive&horizon=10');
        if (forecastResponse.ok) {
          const forecastResult = await forecastResponse.json();
          // Transform API response to component format
          if (forecastResult.forecasts && forecastResult.forecasts.length > 0) {
            const first = forecastResult.forecasts[0];
            setForecastData({
              forecast: first.predictions || [],
              rmse: first.metrics?.rmse || 0,
              model: first.model || 'naive',
              confidence_intervals: first.prediction_intervals ? [
                first.prediction_intervals.lower || [],
                first.prediction_intervals.upper || []
              ] : undefined,
            });
          }
        }

        // Load temporal patterns
        const temporalResponse = await fetch('/temporal/patterns?book=Genesis');
        if (temporalResponse.ok) {
          const temporalResult = await temporalResponse.json();
          // Transform API response to component format
          if (temporalResult.temporal_patterns && temporalResult.temporal_patterns.length > 0) {
            const first = temporalResult.temporal_patterns[0];
            setTemporalData({
              rolling_mean: first.values || [],
              change_points: first.change_points || [],
              metadata: {
                series_length: first.values?.length || 0,
                window_size: first.window || 5,
                volatility: 0, // Calculate if needed
                trend_slope: 0, // Calculate if needed
              },
            });
          }
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  if (loading) {
    return <div className="p-4">Loading data…</div>;
  }

  if (error) {
    return (
      <div className="p-4">
        <p className="text-gray-600">Data unavailable (safe fallback).</p>
        <p className="text-xs text-muted-foreground mt-1">{error}</p>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Orchestrator Dashboard</h1>

      {/* Orchestrator Tiles */}
      {orchestratorLoading && (
        <div className="mb-6 p-4 bg-gray-50 rounded-lg text-center text-gray-600">
          Loading data…
        </div>
      )}

      {orchestratorError && (
        <div className="mb-6 p-4 bg-gray-50 border border-gray-200 rounded-lg">
          <p className="text-gray-600">Data unavailable (safe fallback).</p>
          <p className="text-xs text-muted-foreground mt-1">{orchestratorError}</p>
        </div>
      )}

      {!orchestratorLoading && !orchestratorError && orchestratorData && (
        <div className="mb-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            {/* System Health Card */}
            <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
              <h2 className="text-xl font-semibold mb-4">System Health</h2>
              {orchestratorData.system ? (
                <>
                  <div className="mb-3">
                    <span
                      className={`inline-block px-3 py-1 rounded-full text-white font-semibold text-sm ${
                        orchestratorData.system.level === 'ERROR'
                          ? 'bg-red-500'
                          : orchestratorData.system.level === 'WARN'
                          ? 'bg-yellow-500'
                          : 'bg-green-500'
                      }`}
                    >
                      {orchestratorData.system.level}
                    </span>
                  </div>
                  <div className="text-sm space-y-2">
                    <div className="font-medium text-gray-800">{orchestratorData.system.headline}</div>
                    <div className="text-gray-600">
                      DB: {orchestratorData.system.dbMode} | LM: {orchestratorData.system.lmMode}
                    </div>
                    <div className="text-xs text-gray-500">{orchestratorData.system.details}</div>
                  </div>
                </>
              ) : (
                <div className="text-sm text-gray-500">Data unavailable (safe fallback).</div>
              )}
            </div>

            {/* LM Stack Card */}
            <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
              <h2 className="text-xl font-semibold mb-4">LM Stack</h2>
              {orchestratorData.lm ? (
                <>
                  <div className="mb-3">
                    <span
                      className={`inline-block px-3 py-1 rounded-full text-white font-semibold text-sm ${
                        orchestratorData.lm.status === 'healthy'
                          ? 'bg-green-500'
                          : orchestratorData.lm.status === 'degraded'
                          ? 'bg-yellow-500'
                          : 'bg-red-500'
                      }`}
                    >
                      {orchestratorData.lm.status || 'offline'}
                    </span>
                  </div>
                  <div className="text-sm space-y-2">
                    <div className="text-gray-600">
                      Reason: {orchestratorData.lm.reason || orchestratorData.lm.top_error_reason || 'No details'}
                    </div>
                    {orchestratorData.lm.total_calls !== undefined && (
                      <div className="text-gray-600">
                        Total Calls: {orchestratorData.lm.total_calls.toLocaleString()}
                        {orchestratorData.lm.success_rate !== undefined && (
                          <> | Success: {(orchestratorData.lm.success_rate * 100).toFixed(1)}%</>
                        )}
                      </div>
                    )}
                    {orchestratorData.lm.db_off && (
                      <div className="text-xs text-yellow-600">Database offline</div>
                    )}
                  </div>
                </>
              ) : (
                <div className="text-sm text-gray-500">Data unavailable (safe fallback).</div>
              )}
            </div>

            {/* Compliance Card */}
            <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
              <h2 className="text-xl font-semibold mb-4">Compliance</h2>
              {orchestratorData.compliance ? (
                <div className="text-sm space-y-2">
                  <div className="text-gray-600">
                    Generated: {new Date(orchestratorData.compliance.generated_at).toLocaleString()}
                  </div>
                  {orchestratorData.compliance.latest_agent_run?.created_at ? (
                    <div className="text-gray-600">
                      Latest Run: {new Date(orchestratorData.compliance.latest_agent_run.created_at).toLocaleString()}
                    </div>
                  ) : (
                    <div className="text-gray-500">No agent runs recorded</div>
                  )}
                  {orchestratorData.compliance.windows && (
                    <div className="text-xs text-gray-500 mt-2">
                      7d: {orchestratorData.compliance.windows['7d']?.runs || 0} runs |{' '}
                      30d: {orchestratorData.compliance.windows['30d']?.runs || 0} runs
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-sm text-gray-500">Data unavailable (safe fallback).</div>
              )}
            </div>

            {/* Knowledge Card */}
            <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
              <h2 className="text-xl font-semibold mb-4">Knowledge</h2>
              {orchestratorData.kb ? (
                <div className="text-sm space-y-2">
                  <div className="text-gray-600">
                    Generated: {new Date(orchestratorData.kb.generated_at).toLocaleString()}
                  </div>
                  <div className="text-gray-600">
                    Schema: {orchestratorData.kb.schema || 'unknown'} | Docs: {orchestratorData.kb.docs?.length || 0}
                  </div>
                  {orchestratorData.kb.db_off && (
                    <div className="text-xs text-yellow-600">Database offline</div>
                  )}
                  {orchestratorData.kb.error && (
                    <div className="text-xs text-red-600">Error: {orchestratorData.kb.error}</div>
                  )}
                </div>
              ) : (
                <div className="text-sm text-gray-500">Data unavailable (safe fallback).</div>
              )}
            </div>
          </div>

          {/* Last Updated Footer */}
          {orchestratorData.lastUpdated && (
            <p className="mt-2 text-xs text-muted-foreground text-center mb-6">
              Last updated: {new Date(orchestratorData.lastUpdated).toLocaleString()}
            </p>
          )}
        </div>
      )}

      {/* Temporal Analytics Section */}
      <h2 className="text-2xl font-bold mb-4">Temporal Analytics</h2>

      {/* Temporal Patterns Section */}
      {temporalData && (
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Temporal Patterns</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <h3 className="font-medium">Series Statistics</h3>
              <p>Series Length: {temporalData.metadata.series_length}</p>
              <p>Window Size: {temporalData.metadata.window_size}</p>
              <p>Volatility: {temporalData.metadata.volatility.toFixed(3)}</p>
              <p>Trend Slope: {temporalData.metadata.trend_slope.toFixed(6)}</p>
            </div>

            <div>
              <h3 className="font-medium">Change Points</h3>
              <p>Detected: {temporalData.change_points.length} points</p>
              {temporalData.change_points.length > 0 && (
                <p>Locations: {temporalData.change_points.slice(0, 5).join(', ')}
                  {temporalData.change_points.length > 5 && '...'}</p>
              )}
            </div>
          </div>

          {/* Rolling Mean Visualization Placeholder */}
          <div className="bg-gray-100 p-4 rounded">
            <h3 className="font-medium mb-2">Rolling Mean Trend</h3>
            <p className="text-gray-600">Interactive chart coming soon...</p>
            <p className="text-sm">Data points: {temporalData.rolling_mean.length}</p>
          </div>
        </div>
      )}

      {/* Forecast Section */}
      {forecastData && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Predictive Forecasting</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <h3 className="font-medium">Model Performance</h3>
              <p>Model: {forecastData.model}</p>
              <p>RMSE: {forecastData.rmse.toFixed(4)}</p>
              <p>Horizon: {forecastData.forecast.length} steps</p>
            </div>

            <div>
              <h3 className="font-medium">Forecast Values</h3>
              <div className="text-sm">
                {forecastData.forecast.slice(0, 5).map((val, i) => (
                  <p key={i}>Step {i+1}: {val.toFixed(2)}</p>
                ))}
                {forecastData.forecast.length > 5 && (
                  <p>... and {forecastData.forecast.length - 5} more</p>
                )}
              </div>
            </div>
          </div>

          {/* Forecast Visualization Placeholder */}
          <div className="bg-gray-100 p-4 rounded">
            <h3 className="font-medium mb-2">Forecast Visualization</h3>
            <p className="text-gray-600">Interactive forecast chart with uncertainty intervals coming soon...</p>
            <p className="text-sm">Model: {forecastData.model} | RMSE: {forecastData.rmse.toFixed(4)}</p>
          </div>
        </div>
      )}

      {/* Status Footer */}
      <div className="mt-6 text-center text-gray-500">
        <p>Phase 8: Multi-Temporal Analytics & Predictive Patterns</p>
        <p className="text-sm">ADR-025 Implementation - Interactive exploration coming soon</p>
      </div>
    </div>
  );
};

export default ForecastDashboard;
