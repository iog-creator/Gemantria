import { useEffect, useState } from "react";

// Types for pattern data
interface Pattern {
  book_source: string;
  book_target: string;
  shared_concepts: string[];
  pattern_strength: number;
  metric: string;
  support: number;
  lift: number;
  confidence: number;
  jaccard: number;
}

interface PatternsData {
  patterns: Pattern[];
  metadata: {
    total_patterns: number;
    analyzed_books: string[];
    pattern_methods: string[];
  };
}

export default function PatternExplorer() {
  const [patterns, setPatterns] = useState<PatternsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedMetric, setSelectedMetric] = useState<string>("jaccard");
  const [minStrength, setMinStrength] = useState<number>(0.1);

  useEffect(() => {
    fetchPatterns();
  }, []);

  const fetchPatterns = async () => {
    try {
      setLoading(true);
      const response = await fetch("/api/v1/patterns");
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      const data: PatternsData = await response.json();
      setPatterns(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-64 mb-4"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (error || !patterns) {
    return (
      <div className="p-6">
        <div className="text-red-600">
          <h3 className="text-lg font-semibold mb-2">Error Loading Patterns</h3>
          <p>{error || "No pattern data available"}</p>
          <button
            onClick={fetchPatterns}
            className="mt-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  // Filter and prepare data for visualization
  const filteredPatterns = patterns.patterns.filter(
    (p) => p.pattern_strength >= minStrength,
  );
  const books = Array.from(
    new Set([
      ...filteredPatterns.map((p) => p.book_source),
      ...filteredPatterns.map((p) => p.book_target),
    ]),
  ).sort();

  // Create matrix for heatmap visualization
  const matrix: number[][] = books.map(() => books.map(() => 0));
  const maxValue = Math.max(
    ...filteredPatterns.map((p) => {
      switch (selectedMetric) {
        case "strength":
          return p.pattern_strength;
        case "jaccard":
          return p.jaccard;
        case "lift":
          return p.lift;
        case "confidence":
          return p.confidence;
        case "support":
          return p.support;
        default:
          return p.pattern_strength;
      }
    }),
  );

  filteredPatterns.forEach((pattern) => {
    const sourceIndex = books.indexOf(pattern.book_source);
    const targetIndex = books.indexOf(pattern.book_target);

    if (sourceIndex !== -1 && targetIndex !== -1) {
      let value = pattern.pattern_strength;
      switch (selectedMetric) {
        case "jaccard":
          value = pattern.jaccard;
          break;
        case "lift":
          value = pattern.lift;
          break;
        case "confidence":
          value = pattern.confidence;
          break;
        case "support":
          value = pattern.support;
          break;
      }
      matrix[sourceIndex][targetIndex] = value;
      matrix[targetIndex][sourceIndex] = value; // Make symmetric for heatmap
    }
  });

  const getColor = (value: number) => {
    if (value === 0) return "bg-gray-100";
    const intensity = Math.min(value / maxValue, 1);
    if (intensity < 0.2) return "bg-blue-100";
    if (intensity < 0.4) return "bg-blue-200";
    if (intensity < 0.6) return "bg-blue-300";
    if (intensity < 0.8) return "bg-blue-400";
    return "bg-blue-500";
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold mb-4">Cross-Book Pattern Explorer</h2>

        {/* Controls */}
        <div className="flex gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium mb-1">Metric</label>
            <select
              value={selectedMetric}
              onChange={(e) => setSelectedMetric(e.target.value)}
              className="border rounded px-3 py-1"
            >
              <option value="strength">Pattern Strength</option>
              <option value="jaccard">Jaccard Similarity</option>
              <option value="lift">Lift</option>
              <option value="confidence">Confidence</option>
              <option value="support">Support</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">
              Min Strength: {minStrength.toFixed(2)}
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={minStrength}
              onChange={(e) => setMinStrength(parseFloat(e.target.value))}
              className="w-32"
            />
          </div>
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-600">Total Patterns</div>
            <div className="text-2xl font-bold">
              {patterns.metadata.total_patterns}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-600">Analyzed Books</div>
            <div className="text-2xl font-bold">
              {patterns.metadata.analyzed_books.length}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-600">Filtered Patterns</div>
            <div className="text-2xl font-bold">{filteredPatterns.length}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-600">Max {selectedMetric}</div>
            <div className="text-2xl font-bold">{maxValue.toFixed(3)}</div>
          </div>
        </div>
      </div>

      {/* Heatmap Visualization */}
      <div className="overflow-x-auto">
        <div className="inline-block min-w-full">
          {/* Column headers */}
          <div className="flex mb-2">
            <div className="w-32 flex-shrink-0"></div>
            {books.map((book) => (
              <div
                key={book}
                className="w-12 h-12 flex items-center justify-center text-xs font-medium transform -rotate-45 origin-center"
              >
                {book.length > 6 ? book.substring(0, 6) + "..." : book}
              </div>
            ))}
          </div>

          {/* Rows */}
          {books.map((sourceBook, i) => (
            <div key={sourceBook} className="flex items-center mb-1">
              {/* Row header */}
              <div className="w-32 flex-shrink-0 text-right pr-2 text-sm font-medium truncate">
                {sourceBook}
              </div>

              {/* Cells */}
              {books.map((targetBook, j) => {
                const value = matrix[i][j];
                const isDiagonal = i === j;

                return (
                  <div
                    key={`${sourceBook}-${targetBook}`}
                    className={`
                      w-12 h-12 border border-gray-200 flex items-center justify-center text-xs
                      ${isDiagonal ? "bg-gray-200" : getColor(value)}
                      ${!isDiagonal && value > 0 ? "cursor-pointer hover:opacity-75" : ""}
                    `}
                    title={
                      isDiagonal
                        ? `${sourceBook} (diagonal)`
                        : value > 0
                          ? `${sourceBook} ↔ ${targetBook}: ${value.toFixed(3)}`
                          : `${sourceBook} ↔ ${targetBook}: No pattern`
                    }
                  >
                    {value > 0 && !isDiagonal && (
                      <span className="text-white font-medium">
                        {value.toFixed(2)}
                      </span>
                    )}
                  </div>
                );
              })}
            </div>
          ))}
        </div>
      </div>

      {/* Legend */}
      <div className="mt-6 flex items-center gap-4 text-sm">
        <span>Intensity:</span>
        <div className="flex gap-1">
          <div className="w-4 h-4 bg-gray-100 border"></div>
          <div className="w-4 h-4 bg-blue-100 border"></div>
          <div className="w-4 h-4 bg-blue-200 border"></div>
          <div className="w-4 h-4 bg-blue-300 border"></div>
          <div className="w-4 h-4 bg-blue-400 border"></div>
          <div className="w-4 h-4 bg-blue-500 border"></div>
        </div>
        <span>Low to High</span>
      </div>

      {/* Top Patterns List */}
      <div className="mt-8">
        <h3 className="text-lg font-semibold mb-4">
          Top 10 Strongest Patterns
        </h3>
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white border border-gray-300">
            <thead>
              <tr className="bg-gray-50">
                <th className="border border-gray-300 px-4 py-2 text-left">
                  Source Book
                </th>
                <th className="border border-gray-300 px-4 py-2 text-left">
                  Target Book
                </th>
                <th className="border border-gray-300 px-4 py-2 text-left">
                  Strength
                </th>
                <th className="border border-gray-300 px-4 py-2 text-left">
                  Shared Concepts
                </th>
                <th className="border border-gray-300 px-4 py-2 text-left">
                  Jaccard
                </th>
                <th className="border border-gray-300 px-4 py-2 text-left">
                  Lift
                </th>
              </tr>
            </thead>
            <tbody>
              {filteredPatterns
                .sort((a, b) => b.pattern_strength - a.pattern_strength)
                .slice(0, 10)
                .map((pattern, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="border border-gray-300 px-4 py-2">
                      {pattern.book_source}
                    </td>
                    <td className="border border-gray-300 px-4 py-2">
                      {pattern.book_target}
                    </td>
                    <td className="border border-gray-300 px-4 py-2">
                      {pattern.pattern_strength.toFixed(3)}
                    </td>
                    <td className="border border-gray-300 px-4 py-2">
                      {pattern.shared_concepts.length}
                    </td>
                    <td className="border border-gray-300 px-4 py-2">
                      {pattern.jaccard.toFixed(3)}
                    </td>
                    <td className="border border-gray-300 px-4 py-2">
                      {pattern.lift.toFixed(2)}
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
