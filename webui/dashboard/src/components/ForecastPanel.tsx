import React, { useEffect, useState } from "react";

// Types for forecast data
interface Forecast {
  series_id: string;
  horizon: number;
  model: string;
  predictions: number[];
  book: string;
  rmse?: number;
  mae?: number;
  prediction_intervals?: {
    lower: number[];
    upper: number[];
    confidence_level: number;
  };
}

interface ForecastData {
  forecasts: Forecast[];
  metadata: {
    total_forecasts: number;
    books_forecasted: string[];
    forecast_parameters: {
      default_horizon: number;
      default_model: string;
      min_training_length: number;
    };
    model_distribution: {
      naive: number;
      sma: number;
      arima: number;
    };
    average_metrics: {
      rmse?: number;
      mae?: number;
    };
  };
}

const ForecastPanel: React.FC = () => {
  const [data, setData] = useState<ForecastData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedSeries, setSelectedSeries] = useState<string>("");
  const [horizon, setHorizon] = useState<number>(10);

  useEffect(() => {
    fetchForecastData();
  }, [selectedSeries, horizon]);

  const fetchForecastData = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (selectedSeries) params.append("series_id", selectedSeries);
      if (horizon) params.append("horizon", horizon.toString());

      const response = await fetch(`/api/v1/forecast?${params}`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      setData(result);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  const renderForecastChart = (forecast: Forecast) => {
    const predictions = forecast.predictions;
    const intervals = forecast.prediction_intervals;

    // Create mock historical data (in real implementation, this would come from the temporal data)
    const historicalLength = Math.max(10, predictions.length);
    const historical = Array.from(
      { length: historicalLength },
      (_, i) => 10 + Math.sin(i * 0.5) * 2 + i * 0.1 + Math.random() * 0.5,
    );

    const allValues = [...historical.slice(-10), ...predictions]; // Last 10 historical + predictions
    const maxValue = Math.max(...allValues);
    const minValue = Math.min(...allValues);
    const range = maxValue - minValue || 1;

    return (
      <div className="bg-white p-4 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-2">
          Forecast: {forecast.series_id} - {forecast.book}
        </h3>
        <div className="text-sm text-gray-600 mb-4">
          Model: {forecast.model.toUpperCase()}, Horizon: {forecast.horizon},
          RMSE: {forecast.rmse?.toFixed(3) || "N/A"}, MAE:{" "}
          {forecast.mae?.toFixed(3) || "N/A"}
        </div>

        <div className="relative h-64 bg-gray-50 rounded">
          <svg
            className="w-full h-full"
            viewBox={`0 0 ${allValues.length} 100`}
          >
            {/* Grid lines */}
            <defs>
              <pattern
                id={`grid-${forecast.series_id}`}
                width="10"
                height="10"
                patternUnits="userSpaceOnUse"
              >
                <path
                  d="M 10 0 L 0 0 0 10"
                  fill="none"
                  stroke="#e5e7eb"
                  strokeWidth="0.5"
                />
              </pattern>
            </defs>
            <rect
              width="100%"
              height="100%"
              fill={`url(#grid-${forecast.series_id})`}
            />

            {/* Historical data line */}
            <polyline
              fill="none"
              stroke="#6b7280"
              strokeWidth="2"
              strokeDasharray="5,5"
              points={historical
                .slice(-10)
                .map(
                  (value, index) =>
                    `${index},${100 - ((value - minValue) / range) * 80}`,
                )
                .join(" ")}
            />

            {/* Prediction intervals (if available) */}
            {intervals && intervals.lower && intervals.upper && (
              <polygon
                fill="#dbeafe"
                fillOpacity="0.3"
                stroke="none"
                points={predictions
                  .map((_, index) => {
                    const x = index + 10; // Offset by historical length
                    const yLower =
                      100 - ((intervals.upper[index] - minValue) / range) * 80;
                    const yUpper =
                      100 - ((intervals.lower[index] - minValue) / range) * 80;
                    return `${x},${yLower}`;
                  })
                  .concat(
                    predictions
                      .slice()
                      .reverse()
                      .map((_, index) => {
                        const x = predictions.length - 1 - index + 10;
                        const yLower =
                          100 -
                          ((intervals.lower[predictions.length - 1 - index] -
                            minValue) /
                            range) *
                            80;
                        return `${x},${yLower}`;
                      }),
                  )
                  .join(" ")}
              />
            )}

            {/* Forecast line */}
            <polyline
              fill="none"
              stroke="#ef4444"
              strokeWidth="2"
              points={predictions
                .map(
                  (value, index) =>
                    `${index + 10},${100 - ((value - minValue) / range) * 80}`,
                )
                .join(" ")}
            />

            {/* Vertical line separating historical from forecast */}
            <line
              x1="10"
              y1="0"
              x2="10"
              y2="100"
              stroke="#374151"
              strokeWidth="1"
              strokeDasharray="3,3"
            />
          </svg>

          {/* Legend */}
          <div className="absolute top-2 right-2 text-xs">
            <div className="flex items-center mb-1">
              <div className="w-3 h-0.5 bg-gray-500 mr-1"></div>
              <span>Historical</span>
            </div>
            <div className="flex items-center">
              <div className="w-3 h-0.5 bg-red-500 mr-1"></div>
              <span>Forecast</span>
            </div>
          </div>
        </div>

        {/* Forecast values table */}
        <div className="mt-4">
          <h4 className="text-sm font-semibold mb-2">Forecast Values</h4>
          <div className="grid grid-cols-5 gap-2 text-xs">
            {predictions.slice(0, 10).map((value, index) => (
              <div key={index} className="bg-gray-50 p-2 rounded text-center">
                <div className="font-semibold">Step {index + 1}</div>
                <div className="text-gray-600">{value.toFixed(3)}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="h-32 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h3 className="text-red-800 font-semibold">
            Error Loading Forecast Data
          </h3>
          <p className="text-red-600 mt-2">{error}</p>
        </div>
      </div>
    );
  }

  const forecasts = data?.forecasts || [];
  const availableSeries = [...new Set(forecasts.map((f) => f.series_id))];

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-6">Forecast Analytics</h2>

      {/* Controls */}
      <div className="bg-white p-4 rounded-lg shadow mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Series ID
            </label>
            <select
              value={selectedSeries}
              onChange={(e) => setSelectedSeries(e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Series</option>
              {availableSeries.map((series) => (
                <option key={series} value={series}>
                  {series}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Forecast Horizon
            </label>
            <input
              type="number"
              min="1"
              max="50"
              value={horizon}
              onChange={(e) => setHorizon(parseInt(e.target.value) || 10)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
      </div>

      {/* Summary Stats */}
      {data && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white p-4 rounded-lg shadow">
            <h3 className="text-lg font-semibold text-gray-900">
              Total Forecasts
            </h3>
            <p className="text-3xl font-bold text-blue-600">
              {data.metadata.total_forecasts}
            </p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <h3 className="text-lg font-semibold text-gray-900">
              Books Forecasted
            </h3>
            <p className="text-xl font-semibold text-green-600">
              {data.metadata.books_forecasted.length}
            </p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <h3 className="text-lg font-semibold text-gray-900">Avg RMSE</h3>
            <p className="text-xl font-semibold text-red-600">
              {data.metadata.average_metrics.rmse?.toFixed(3) || "N/A"}
            </p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <h3 className="text-lg font-semibold text-gray-900">Avg MAE</h3>
            <p className="text-xl font-semibold text-orange-600">
              {data.metadata.average_metrics.mae?.toFixed(3) || "N/A"}
            </p>
          </div>
        </div>
      )}

      {/* Model Distribution */}
      {data && (
        <div className="bg-white p-4 rounded-lg shadow mb-6">
          <h3 className="text-lg font-semibold mb-4">Model Distribution</h3>
          <div className="grid grid-cols-3 gap-4">
            {Object.entries(data.metadata.model_distribution).map(
              ([model, count]) =>
                count > 0 && (
                  <div key={model} className="text-center">
                    <div className="text-2xl font-bold text-gray-900">
                      {count}
                    </div>
                    <div className="text-sm text-gray-600 uppercase">
                      {model}
                    </div>
                  </div>
                ),
            )}
          </div>
        </div>
      )}

      {/* Forecast Charts */}
      <div className="space-y-6">
        {forecasts.length === 0 ? (
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
            <p className="text-gray-500">
              No forecasts found matching the current filters.
            </p>
          </div>
        ) : (
          forecasts.map((forecast, index) => (
            <div key={`${forecast.series_id}-${index}`}>
              {renderForecastChart(forecast)}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default ForecastPanel;
