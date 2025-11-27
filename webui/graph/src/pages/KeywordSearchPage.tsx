import React, { useState } from 'react';

interface VerseResult {
  book: string;
  chapter: number;
  verse: number;
  text: string;
  translation: string;
}

interface SearchResponse {
  results: VerseResult[];
  count: number;
}

const KeywordSearchPage: React.FC = () => {
  const [query, setQuery] = useState('');
  const [translation, setTranslation] = useState('KJV');
  const [limit, setLimit] = useState(20);
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<SearchResponse | null>(null);
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
      const url = `/api/bible/search?q=${encodeURIComponent(query.trim())}&translation=${translation}&limit=${limit}`;
      const response = await fetch(url);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      const result: SearchResponse = await response.json();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to search verses');
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-full overflow-auto bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-2">Keyword Search</h1>
        <p className="text-gray-800 mb-6">Search Bible verses by keyword across translations</p>

        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="query" className="block text-sm font-medium text-gray-700 mb-2">
                Search Query
              </label>
              <input
                type="text"
                id="query"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="e.g. beginning, love, faith"
                minLength={2}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
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
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="KJV">KJV (King James Version)</option>
                  <option value="ESV">ESV (English Standard Version)</option>
                  <option value="NIV">NIV (New International Version)</option>
                  <option value="NASB">NASB (New American Standard Bible)</option>
                </select>
              </div>

              <div>
                <label htmlFor="limit" className="block text-sm font-medium text-gray-700 mb-2">
                  Results Limit
                </label>
                <input
                  type="number"
                  id="limit"
                  value={limit}
                  onChange={(e) => setLimit(parseInt(e.target.value, 10) || 20)}
                  min={1}
                  max={100}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading || !query.trim() || query.trim().length < 2}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
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
                {data.count} {data.count === 1 ? 'result' : 'results'} found
              </span>
            </div>

            {data.results.length === 0 ? (
              <div className="text-center py-8 text-gray-700">
                <p>No verses found matching "{query}"</p>
                <p className="text-sm mt-2">Try a different search term or translation</p>
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
                      <span className="text-sm text-gray-700 ml-2">({verse.translation})</span>
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

export default KeywordSearchPage;

