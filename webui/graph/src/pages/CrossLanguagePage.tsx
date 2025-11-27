import React, { useState } from 'react';

interface WordAnalysisResponse {
  strongs_id: string;
  lemma: string;
  gloss: string | null;
  occurrence_count: number;
  related_verses: string[];
}

interface CrossLanguageMatchResponse {
  source_strongs: string;
  target_strongs: string;
  target_lemma: string;
  similarity_score: number;
  common_verses: string[];
}

interface CrossLanguageResponse {
  strongs_id: string;
  reference: string | null;
  word_analysis: WordAnalysisResponse | null;
  connections: CrossLanguageMatchResponse[];
  connections_count: number;
  errors: string[];
}

const CrossLanguagePage: React.FC = () => {
  const [strongsId, setStrongsId] = useState('');
  const [reference, setReference] = useState('');
  const [limit, setLimit] = useState(10);
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<CrossLanguageResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showWordAnalysis, setShowWordAnalysis] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!strongsId.trim()) {
      setError('Please enter a Strong\'s number');
      return;
    }

    setLoading(true);
    setError(null);
    setData(null);
    setShowWordAnalysis(false);

    try {
      const params = new URLSearchParams({
        strongs_id: strongsId.trim().toUpperCase(),
        limit: limit.toString(),
      });
      if (reference.trim()) {
        params.append('reference', reference.trim());
      }

      const url = `/api/biblescholar/cross-language?${params.toString()}`;
      const response = await fetch(url);

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP ${response.status}: ${errorText || response.statusText}`);
      }

      const result: CrossLanguageResponse = await response.json();

      if (result.errors && result.errors.length > 0) {
        setError(result.errors.join('; '));
      }

      setData(result);
      if (result.word_analysis) {
        setShowWordAnalysis(true);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch cross-language connections');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-full overflow-auto p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-2">Cross-Language Search</h1>
        <p className="text-gray-800 mb-6">Find Hebrew↔Greek semantic connections using vector similarity</p>

        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="strongs-id" className="block text-sm font-medium text-gray-700 mb-2">
                Strong's Number <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                id="strongs-id"
                value={strongsId}
                onChange={(e) => setStrongsId(e.target.value)}
                placeholder="e.g. H7965 (Hebrew) or G1 (Greek)"
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              />
              <p className="mt-1 text-xs text-gray-500">
                Enter a Strong's number (H for Hebrew, G for Greek)
              </p>
            </div>
            <div>
              <label htmlFor="reference" className="block text-sm font-medium text-gray-700 mb-2">
                Bible Reference (Optional)
              </label>
              <input
                type="text"
                id="reference"
                value={reference}
                onChange={(e) => setReference(e.target.value)}
                placeholder="e.g. Genesis 1:1"
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              <p className="mt-1 text-xs text-gray-500">
                Optional: Provide a reference to analyze the word in context
              </p>
            </div>
            <div>
              <label htmlFor="limit" className="block text-sm font-medium text-gray-700 mb-2">
                Maximum Connections
              </label>
              <input
                type="number"
                id="limit"
                value={limit}
                onChange={(e) => setLimit(Math.max(1, Math.min(50, parseInt(e.target.value) || 10)))}
                min={1}
                max={50}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Searching...' : 'Find Cross-Language Connections'}
            </button>
          </form>
        </div>

        {loading && (
          <div className="text-center py-8">
            <p className="text-gray-800">Searching for cross-language connections...</p>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {data && (
          <div className="space-y-6">
            {/* Word Analysis */}
            {data.word_analysis && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <button
                  onClick={() => setShowWordAnalysis(!showWordAnalysis)}
                  className="w-full flex items-center justify-between text-left mb-4"
                >
                  <h2 className="text-2xl font-semibold">Word Analysis</h2>
                  <svg
                    className={`w-5 h-5 transform transition-transform ${showWordAnalysis ? 'rotate-180' : ''}`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>

                {showWordAnalysis && (
                  <div className="space-y-4">
                    <div>
                      <h3 className="text-sm font-semibold text-gray-700 mb-2">Strong's ID</h3>
                      <p className="text-gray-800 font-mono">{data.word_analysis.strongs_id}</p>
                    </div>
                    <div>
                      <h3 className="text-sm font-semibold text-gray-700 mb-2">Lemma</h3>
                      <p className="text-gray-800">{data.word_analysis.lemma}</p>
                    </div>
                    {data.word_analysis.gloss && (
                      <div>
                        <h3 className="text-sm font-semibold text-gray-700 mb-2">Gloss</h3>
                        <p className="text-gray-800">{data.word_analysis.gloss}</p>
                      </div>
                    )}
                    <div>
                      <h3 className="text-sm font-semibold text-gray-700 mb-2">Occurrences</h3>
                      <p className="text-gray-800">{data.word_analysis.occurrence_count} verse(s)</p>
                    </div>
                    {data.word_analysis.related_verses.length > 0 && (
                      <div>
                        <h3 className="text-sm font-semibold text-gray-700 mb-2">Related Verses</h3>
                        <div className="space-y-1">
                          {data.word_analysis.related_verses.slice(0, 10).map((verse, idx) => (
                            <div key={idx} className="text-sm text-gray-800">{verse}</div>
                          ))}
                          {data.word_analysis.related_verses.length > 10 && (
                            <div className="text-xs text-gray-500">
                              ... and {data.word_analysis.related_verses.length - 10} more
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Connections Summary */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-semibold">Cross-Language Connections</h2>
                <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                  {data.connections_count} connection{data.connections_count !== 1 ? 's' : ''}
                </span>
              </div>
              {data.reference && (
                <p className="text-sm text-gray-600 mb-4">
                  Reference: <span className="font-medium">{data.reference}</span>
                </p>
              )}
            </div>

            {/* Connections List */}
            {data.connections.length === 0 ? (
              <div className="bg-white rounded-lg shadow-md p-8 text-center text-gray-500">
                No cross-language connections found
              </div>
            ) : (
              <div className="space-y-4">
                {data.connections.map((conn, idx) => (
                  <div key={idx} className="bg-white rounded-lg shadow-md p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-mono bg-gray-100 px-2 py-1 rounded">#{idx + 1}</span>
                        <span className="text-sm font-semibold text-gray-700">Connection</span>
                      </div>
                      <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium">
                        {(conn.similarity_score * 100).toFixed(1)}% similarity
                      </span>
                    </div>

                    <div className="space-y-3">
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-xs font-semibold text-orange-700 bg-orange-50 px-2 py-0.5 rounded">
                            Source
                          </span>
                          <span className="font-mono text-sm text-gray-800">{conn.source_strongs}</span>
                        </div>
                      </div>
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-xs font-semibold text-blue-700 bg-blue-50 px-2 py-0.5 rounded">
                            Target
                          </span>
                          <span className="font-mono text-sm text-gray-800">{conn.target_strongs}</span>
                          <span className="text-sm text-gray-600">({conn.target_lemma})</span>
                        </div>
                      </div>
                      {conn.common_verses.length > 0 && (
                        <div>
                          <h4 className="text-sm font-semibold text-gray-700 mb-2">Common Verses</h4>
                          <div className="space-y-1">
                            {conn.common_verses.map((verse, verseIdx) => (
                              <div key={verseIdx} className="text-sm text-gray-800">{verse}</div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
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

export default CrossLanguagePage;

