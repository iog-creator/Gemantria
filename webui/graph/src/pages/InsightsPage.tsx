import React, { useState } from 'react';

interface LexiconEntryResponse {
  strongs_id: string;
  lemma: string;
  gloss: string;
  definition: string;
  transliteration: string;
  usage: string;
}

interface SemanticVerseResult {
  book: string;
  chapter: number;
  verse: number;
  text: string;
  similarity: number;
}

interface VerseContextResponse {
  reference: string;
  primary_text: string;
  secondary_texts: Record<string, string>;
  lexicon_entries: LexiconEntryResponse[];
  similar_verses: SemanticVerseResult[];
}

interface InsightsResponse {
  reference: string;
  insight_text: string;
  source: string; // "lm_theology" | "raw_context"
  context: VerseContextResponse;
  errors: string[];
}

const InsightsPage: React.FC = () => {
  const [reference, setReference] = useState('');
  const [useLm, setUseLm] = useState(true);
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<InsightsResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showContext, setShowContext] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!reference.trim()) {
      setError('Please enter a Bible reference');
      return;
    }

    setLoading(true);
    setError(null);
    setData(null);
    setShowContext(false);

    try {
      const url = `/api/biblescholar/insights?reference=${encodeURIComponent(reference)}&use_lm=${useLm}`;
      const response = await fetch(url);

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP ${response.status}: ${errorText || response.statusText}`);
      }

      const result: InsightsResponse = await response.json();

      if (result.errors && result.errors.length > 0) {
        setError(result.errors.join('; '));
        return;
      }

      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch insights');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-full overflow-auto p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-2">Contextual Insights</h1>
        <p className="text-gray-800 mb-6">DB-grounded theological insights for Bible verses</p>

        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="reference" className="block text-sm font-medium text-gray-700 mb-2">
                Bible Reference
              </label>
              <input
                type="text"
                id="reference"
                value={reference}
                onChange={(e) => setReference(e.target.value)}
                placeholder="e.g. John 3:16"
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              />
            </div>
            <div className="flex items-center">
              <input
                type="checkbox"
                id="use-lm"
                checked={useLm}
                onChange={(e) => setUseLm(e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="use-lm" className="ml-2 block text-sm text-gray-700">
                Use AI synthesis
              </label>
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Loading...' : 'Get Insights'}
            </button>
          </form>
        </div>

        {loading && (
          <div className="text-center py-8">
            <p className="text-gray-800">Loading insights...</p>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {data && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-semibold">{data.reference}</h2>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  data.source === 'lm_theology'
                    ? 'bg-green-100 text-green-800'
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {data.source === 'lm_theology' ? 'AI Synthesis' : 'Raw Context'}
                </span>
              </div>
              <div className="text-gray-700 whitespace-pre-wrap mb-4">
                {data.insight_text}
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <button
                onClick={() => setShowContext(!showContext)}
                className="w-full flex items-center justify-between text-left mb-4"
              >
                <h3 className="text-xl font-semibold">Context Breakdown</h3>
                <svg
                  className={`w-5 h-5 transform transition-transform ${showContext ? 'rotate-180' : ''}`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              {showContext && (
                <div className="space-y-4">
                  <div>
                    <h4 className="text-sm font-semibold text-gray-700 mb-2">Primary Text (KJV)</h4>
                    <p className="text-gray-800">{data.context.primary_text}</p>
                  </div>

                  {Object.keys(data.context.secondary_texts).length > 0 && (
                    <div>
                      <h4 className="text-sm font-semibold text-gray-700 mb-2">Other Translations</h4>
                      <div className="space-y-2">
                        {Object.entries(data.context.secondary_texts).map(([trans, text]) => (
                          <div key={trans}>
                            <span className="font-medium text-gray-700">{trans}:</span>{' '}
                            <span className="text-gray-800">{text}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {data.context.lexicon_entries.length > 0 && (
                    <div>
                      <h4 className="text-sm font-semibold text-gray-700 mb-2">Lexicon Entries</h4>
                      <div className="space-y-2">
                        {data.context.lexicon_entries.map((entry, idx) => (
                          <div key={idx} className="p-3 bg-gray-50 rounded-md">
                            <div className="font-medium text-gray-800">
                              {entry.lemma} ({entry.strongs_id})
                            </div>
                            <div className="text-sm text-gray-600 mt-1">
                              {entry.gloss || entry.definition}
                            </div>
                            {entry.transliteration && (
                              <div className="text-xs text-gray-500 mt-1">
                                Transliteration: {entry.transliteration}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {data.context.similar_verses.length > 0 && (
                    <div>
                      <h4 className="text-sm font-semibold text-gray-700 mb-2">Similar Verses</h4>
                      <div className="space-y-2">
                        {data.context.similar_verses.map((verse, idx) => (
                          <div key={idx} className="p-3 bg-gray-50 rounded-md">
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <span className="font-semibold text-blue-600">
                                  {verse.book} {verse.chapter}:{verse.verse}
                                </span>
                                <span className="text-gray-500 ml-2">
                                  (similarity: {(verse.similarity * 100).toFixed(1)}%)
                                </span>
                                <p className="text-gray-800 mt-1">{verse.text}</p>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default InsightsPage;

