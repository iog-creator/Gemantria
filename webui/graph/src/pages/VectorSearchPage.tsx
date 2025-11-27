import React, { useState } from 'react';

interface SemanticVerseResult {
  book: string;
  chapter: number;
  verse: number;
  text: string;
  similarity: number;
}

interface SemanticSearchResponse {
  query: string;
  results: SemanticVerseResult[];
  total: number;
}

const VectorSearchPage: React.FC = () => {
  const [query, setQuery] = useState('');
  const [translation, setTranslation] = useState('KJV');
  const [limit, setLimit] = useState(20);
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<SemanticSearchResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || query.trim().length < 2) {
      setError('Query must be at least 2 characters');
      return;
    }

    setLoading(true);
    setError(null);
    setData(null);

    try {
      const url = `/api/bible/semantic?q=${encodeURIComponent(query.trim())}&limit=${limit}&translation=${encodeURIComponent(translation)}`;
      const response = await fetch(url);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Search failed' }));
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }

      const result: SemanticSearchResponse = await response.json();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-full overflow-auto p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-2">Vector Search</h1>
        <p className="text-gray-800 mb-6">Semantic search for Bible verses using vector embeddings. Search by concepts, themes, or questions.</p>

        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="query" className="block text-sm font-medium text-gray-700 mb-2">
                Search Query
              </label>
              <input
                id="query"
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="e.g., hope in difficult times, faith and trust in God"
                className="w-full px-4 py-2 border border-gray-300 rounded-md text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                disabled={loading}
                minLength={2}
              />
              <p className="mt-1 text-xs text-gray-700">Minimum 2 characters required</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="translation" className="block text-sm font-medium text-gray-700 mb-2">
                  Translation
                </label>
                <select
                  id="translation"
                  value={translation}
                  onChange={(e) => setTranslation(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  disabled={loading}
                >
                  <option value="KJV">KJV (King James Version)</option>
                  <option value="ESV">ESV (English Standard Version)</option>
                  <option value="NIV">NIV (New International Version)</option>
                </select>
              </div>

              <div>
                <label htmlFor="limit" className="block text-sm font-medium text-gray-700 mb-2">
                  Results Limit
                </label>
                <input
                  id="limit"
                  type="number"
                  min="1"
                  max="100"
                  value={limit}
                  onChange={(e) => setLimit(parseInt(e.target.value, 10) || 20)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  disabled={loading}
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading || !query.trim() || query.trim().length < 2}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-semibold py-2 px-4 rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              {loading ? 'Searching...' : 'Search Verses'}
            </button>
          </form>
        </div>

        {loading && (
          <div className="text-center py-8">
            <p className="text-gray-800">Searching...</p>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
            <p className="text-red-800 font-medium">Error</p>
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {data && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-2xl font-semibold">Search Results</h2>
              <span className="text-sm text-gray-800">
                {data.total} {data.total === 1 ? 'result' : 'results'} found
              </span>
            </div>

            {data.results.length === 0 ? (
              <div className="text-center py-8 text-gray-700">
                <p>No verses found matching &quot;{data.query}&quot;</p>
                <p className="text-sm mt-2">Try a different search term</p>
              </div>
            ) : (
              <div className="space-y-4">
                {data.results.map((verse, idx) => (
                  <div
                    key={idx}
                    className="p-4 border border-gray-200 rounded-md hover:bg-gray-50 transition-colors"
                  >
                    <div className="mb-2">
                      <span className="font-semibold text-blue-600">
                        {verse.book} {verse.chapter}:{verse.verse}
                      </span>
                      <span className="text-sm text-gray-700 ml-2">({translation})</span>
                      <span className="text-sm text-gray-700 ml-2">
                        · {(verse.similarity * 100).toFixed(1)}% match
                      </span>
                    </div>
                    <div className="text-gray-800">{verse.text}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default VectorSearchPage;

