import React, { useState } from 'react';

interface GematriaSystemResult {
  system: string;
  value: number;
  normalized: string;
  letters: string[];
}

interface VerseWithGematria {
  book: string;
  chapter: number;
  verse: number;
  text: string;
  gematria: Record<string, GematriaSystemResult> | null;
}

interface PassageResponse {
  reference: string;
  verses: VerseWithGematria[];
  commentary: {
    source: string;
    text: string;
  };
  errors: string[];
}

const BiblePage: React.FC = () => {
  const [reference, setReference] = useState('');
  const [selectedTranslations, setSelectedTranslations] = useState<string[]>(['KJV']);
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<Record<string, PassageResponse>>({});
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!reference.trim()) {
      setError('Please enter a Bible reference');
      return;
    }

    if (selectedTranslations.length === 0) {
      setError('Please select at least one translation');
      return;
    }

    setLoading(true);
    setError(null);
    setData({});

    try {
      // Fetch all selected translations in parallel
      const promises = selectedTranslations.map(async (trans) => {
        const url = `/api/biblescholar/passage?reference=${encodeURIComponent(reference)}&translation=${encodeURIComponent(trans)}&use_lm=false`;
        const response = await fetch(url);

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText} for ${trans}`);
        }

        const result: PassageResponse = await response.json();
        return { translation: trans, data: result };
      });

      const results = await Promise.all(promises);
      const dataMap: Record<string, PassageResponse> = {};

      // Check for errors in any result
      const allErrors: string[] = [];
      for (const { translation, data: result } of results) {
        if (result.errors && result.errors.length > 0) {
          allErrors.push(`${translation}: ${result.errors.join('; ')}`);
        } else {
          dataMap[translation] = result;
        }
      }

      if (allErrors.length > 0) {
        setError(allErrors.join(' | '));
      }

      setData(dataMap);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch passages');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-full overflow-auto bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-2">Bible Scholar</h1>
        <p className="text-gray-800 mb-6">Passage Lookup with Gematria</p>

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
                placeholder="e.g. John 3:16-18"
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Translations (select multiple for parallel view)
              </label>
              <div className="grid grid-cols-2 gap-3">
                {['KJV', 'ESV', 'ASV', 'YLT', 'TAHOT'].map((trans) => (
                  <div key={trans} className="flex items-center">
                    <input
                      type="checkbox"
                      id={`trans-${trans}`}
                      checked={selectedTranslations.includes(trans)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedTranslations([...selectedTranslations, trans]);
                        } else {
                          setSelectedTranslations(selectedTranslations.filter(t => t !== trans));
                        }
                      }}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label htmlFor={`trans-${trans}`} className="ml-2 block text-sm text-gray-700">
                      {trans === 'KJV'
                        ? 'King James Version'
                        : trans === 'ESV'
                        ? 'English Standard Version'
                        : trans === 'ASV'
                        ? 'American Standard Version'
                        : trans === 'YLT'
                        ? "Young's Literal Translation"
                        : 'The Ancient Hebrew of the Torah'}
                    </label>
                  </div>
                ))}
              </div>
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Loading...' : 'Lookup Passage'}
            </button>
          </form>
        </div>

        {loading && (
          <div className="text-center py-8">
            <p className="text-gray-800">Loading...</p>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {Object.keys(data).length > 0 && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-2xl font-semibold mb-4">
                {Object.values(data)[0]?.reference || reference}
              </h2>
              
              {/* Parallel Translation View */}
              <div className={`grid gap-4 ${Object.keys(data).length === 1 ? 'grid-cols-1' : Object.keys(data).length === 2 ? 'grid-cols-2' : 'grid-cols-3'}`}>
                {Object.entries(data).map(([trans, passageData]) => (
                  <div key={trans} className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                    <h3 className="text-lg font-semibold mb-3 text-blue-600 border-b border-gray-300 pb-2">
                      {trans === 'KJV'
                        ? 'King James Version'
                        : trans === 'ESV'
                        ? 'English Standard Version'
                        : trans === 'ASV'
                        ? 'American Standard Version'
                        : trans === 'YLT'
                        ? "Young's Literal Translation"
                        : 'The Ancient Hebrew of the Torah'}
                    </h3>
                    <div className="space-y-3 text-gray-800 text-sm">
                      {passageData.verses.map((verse, idx) => (
                        <div key={idx} className="mb-3 pb-2 border-b border-gray-200 last:border-0">
                          <div className="mb-1">
                            <span className="font-semibold text-blue-600 text-xs">
                              {verse.verse}.
                            </span>{' '}
                            <span className="text-gray-800">{verse.text}</span>
                          </div>
                          {verse.gematria && (
                            <div className="mt-2 p-2 bg-white rounded text-xs">
                              <h4 className="text-xs font-semibold text-gray-700 mb-1">Gematria</h4>
                              <div className="space-y-1">
                                {Object.entries(verse.gematria).map(([system, result]) => (
                                  <div key={system} className="text-xs">
                                    <span className="font-medium text-gray-600">{system}:</span>{' '}
                                    <span className="text-blue-600 font-semibold">{result.value}</span>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>

          </div>
        )}
      </div>
    </div>
  );
};

export default BiblePage;

