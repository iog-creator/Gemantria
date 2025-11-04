// webui/dashboard/ForecastDashboard.tsx
// Interactive forecast dashboard per ADR-025

import React, { useState, useEffect } from 'react';

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
  const [forecastData, setForecastData] = useState<ForecastData | null>(null);
  const [temporalData, setTemporalData] = useState<TemporalData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        // Load forecast data
        const forecastResponse = await fetch('/api/forecast');
        if (forecastResponse.ok) {
          const forecast = await forecastResponse.json();
          setForecastData(forecast);
        }

        // Load temporal patterns
        const temporalResponse = await fetch('/api/temporal-patterns');
        if (temporalResponse.ok) {
          const temporal = await temporalResponse.json();
          setTemporalData(temporal);
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
    return <div className="p-4">Loading temporal analytics...</div>;
  }

  if (error) {
    return <div className="p-4 text-red-500">Error: {error}</div>;
  }

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Temporal Analytics Dashboard</h1>

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
