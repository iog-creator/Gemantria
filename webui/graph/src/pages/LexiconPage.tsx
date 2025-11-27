import React, { useState } from 'react';

interface LexiconEntry {
  strongs_id: string;
  lemma: string;
  gloss: string | null;
  definition: string | null;
  transliteration: string | null;
  usage: string | null;
}

const LexiconPage: React.FC = () => {
  const [strongsId, setStrongsId] = useState('');
  const [loading, setLoading] = useState(false);
  const [entry, setEntry] = useState<LexiconEntry | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!strongsId.trim()) {
      setError('Please enter a Strong\'s number');
      return;
    }

    setLoading(true);
    setError(null);
    setEntry(null);

    try {
      // Normalize Strong's ID (remove spaces, ensure uppercase prefix)
      const normalizedId = strongsId.trim().toUpperCase();
      const url = `/api/bible/lexicon/${encodeURIComponent(normalizedId)}`;
      const response = await fetch(url);

      if (!response.ok) {
        if (response.status === 404) {
          const errorData = await response.json().catch(() => ({ detail: 'Lexicon entry not found' }));
          throw new Error(errorData.detail || 'Lexicon entry not found');
        }
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      const result: LexiconEntry = await response.json();
      setEntry(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch lexicon entry');
      console.error('Lexicon lookup error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getLanguageLabel = (strongsId: string): string => {
    const upper = strongsId.toUpperCase();
    if (upper.startsWith('H')) return 'Hebrew';
    if (upper.startsWith('G')) return 'Greek';
    return 'Unknown';
  };

  return (
    <div className="h-full overflow-auto bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-2">Lexicon Lookup</h1>
        <p className="text-gray-800 mb-6">Look up Hebrew and Greek lexicon entries by Strong's number</p>

        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="strongs-id" className="block text-sm font-medium text-gray-700 mb-2">
                Strong's Number
              </label>
              <input
                type="text"
                id="strongs-id"
                value={strongsId}
                onChange={(e) => setStrongsId(e.target.value)}
                placeholder="e.g. H1, G1, H7965"
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              />
              <p className="mt-1 text-xs text-gray-500">
                Enter a Strong's number (H for Hebrew, G for Greek, e.g., H1, G1)
              </p>
            </div>

            <button
              type="submit"
              disabled={loading || !strongsId.trim()}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Looking up...' : 'Lookup Entry'}
            </button>
          </form>
        </div>

        {loading && (
          <div className="text-center py-8">
            <p className="text-gray-800">Searching lexicon...</p>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
            <p className="text-red-800 font-medium">Error</p>
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {entry && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-2xl font-semibold">Lexicon Entry</h2>
              <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                {getLanguageLabel(entry.strongs_id)}
              </span>
            </div>

            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-1">Strong's Number</h3>
                  <p className="text-lg font-semibold text-gray-900">{entry.strongs_id}</p>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-1">Lemma</h3>
                  <p className="text-lg font-semibold text-gray-900">{entry.lemma}</p>
                </div>
              </div>

              {entry.transliteration && (
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-1">Transliteration</h3>
                  <p className="text-gray-800">{entry.transliteration}</p>
                </div>
              )}

              {entry.gloss && (
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-1">Gloss</h3>
                  <p className="text-gray-800">{entry.gloss}</p>
                </div>
              )}

              {entry.definition && (
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-1">Definition</h3>
                  <p className="text-gray-800 whitespace-pre-wrap">{entry.definition}</p>
                </div>
              )}

              {entry.usage && (
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-1">Usage</h3>
                  <p className="text-gray-800 whitespace-pre-wrap">{entry.usage}</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default LexiconPage;

