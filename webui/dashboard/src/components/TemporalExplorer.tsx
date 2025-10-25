import React, { useEffect, useState } from "react";

// Types for temporal pattern data
interface TemporalPattern {
  series_id: string;
  unit: string;
  window: number;
  start_index: number;
  end_index: number;
  metric: string;
  values: number[];
  method: string;
  book: string;
  change_points?: number[];
  zscore_values?: number[];
}

interface TemporalData {
  temporal_patterns: TemporalPattern[];
  metadata: {
    total_series: number;
    books_analyzed: string[];
    analysis_parameters: {
      default_unit: string;
      default_window: number;
      min_series_length: number;
    };
  };
}

const TemporalExplorer: React.FC = () => {
  const [data, setData] = useState<TemporalData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedSeries, setSelectedSeries] = useState<string>("");
  const [unit, setUnit] = useState<string>("chapter");
  const [window, setWindow] = useState<number>(5);

  useEffect(() => {
    fetchTemporalData();
  }, [selectedSeries, unit, window]);

  const fetchTemporalData = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (selectedSeries) params.append("series_id", selectedSeries);
      if (unit) params.append("unit", unit);
      if (window) params.append("window", window.toString());

      const response = await fetch(`/api/v1/temporal?${params}`);
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

  const renderChart = (pattern: TemporalPattern) => {
    const values = pattern.values;
    const changePoints = pattern.change_points || [];
    const maxValue = Math.max(...values);
    const minValue = Math.min(...values);
    const range = maxValue - minValue || 1;

    return (
      <div className="bg-white p-4 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-2">
          {pattern.series_id} - {pattern.book} ({pattern.unit})
        </h3>
        <div className="text-sm text-gray-600 mb-4">
          Window: {pattern.window}, Method: {pattern.method}, Metric:{" "}
          {pattern.metric}
        </div>

        <div className="relative h-64 bg-gray-50 rounded">
          <svg className="w-full h-full" viewBox={`0 0 ${values.length} 100`}>
            {/* Grid lines */}
            <defs>
              <pattern
                id="grid"
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
            <rect width="100%" height="100%" fill="url(#grid)" />

            {/* Data line */}
            <polyline
              fill="none"
              stroke="#3b82f6"
              strokeWidth="2"
              points={values
                .map(
                  (value, index) =>
                    `${index},${100 - ((value - minValue) / range) * 80}`,
                )
                .join(" ")}
            />

            {/* Change points */}
            {changePoints.map((pointIndex) => (
              <circle
                key={pointIndex}
                cx={pointIndex}
                cy={100 - ((values[pointIndex] - minValue) / range) * 80}
                r="3"
                fill="#ef4444"
                stroke="white"
                strokeWidth="1"
              />
            ))}
          </svg>
        </div>

        {changePoints.length > 0 && (
          <div className="mt-2 text-sm text-red-600">
            Change points detected at indices: {changePoints.join(", ")}
          </div>
        )}
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
            Error Loading Temporal Data
          </h3>
          <p className="text-red-600 mt-2">{error}</p>
        </div>
      </div>
    );
  }

  const patterns = data?.temporal_patterns || [];
  const availableSeries = [...new Set(patterns.map((p) => p.series_id))];

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-6">Temporal Pattern Explorer</h2>

      {/* Controls */}
      <div className="bg-white p-4 rounded-lg shadow mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
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
              Time Unit
            </label>
            <select
              value={unit}
              onChange={(e) => setUnit(e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="verse">Verse</option>
              <option value="chapter">Chapter</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Window Size
            </label>
            <input
              type="number"
              min="1"
              value={window}
              onChange={(e) => setWindow(parseInt(e.target.value) || 5)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
      </div>

      {/* Summary Stats */}
      {data && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-white p-4 rounded-lg shadow">
            <h3 className="text-lg font-semibold text-gray-900">
              Total Series
            </h3>
            <p className="text-3xl font-bold text-blue-600">
              {data.metadata.total_series}
            </p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <h3 className="text-lg font-semibold text-gray-900">
              Books Analyzed
            </h3>
            <p className="text-xl font-semibold text-green-600">
              {data.metadata.books_analyzed.length}
            </p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <h3 className="text-lg font-semibold text-gray-900">
              Default Window
            </h3>
            <p className="text-xl font-semibold text-purple-600">
              {data.metadata.analysis_parameters.default_window}
            </p>
          </div>
        </div>
      )}

      {/* Charts */}
      <div className="space-y-6">
        {patterns.length === 0 ? (
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
            <p className="text-gray-500">
              No temporal patterns found matching the current filters.
            </p>
          </div>
        ) : (
          patterns.map((pattern, index) => (
            <div key={`${pattern.series_id}-${index}`}>
              {renderChart(pattern)}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default TemporalExplorer;
