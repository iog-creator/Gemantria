import React, { useState, useEffect, useCallback, useRef } from 'react';
import LoadingSpinner from './LoadingSpinner';
import StatusBanner from './StatusBanner';
import SearchBar from './SearchBar';
import ResultsList from './ResultsList';
import CapabilitiesSidebar from './CapabilitiesSidebar';
import { Verse } from './VerseCard';

interface SemanticSearchResult {
  verse_id: number;
  book_name: string;
  chapter_num: number;
  verse_num: number;
  text: string;
  translation_source: string;
  similarity_score?: number;
}

interface SemanticSearchData {
  query: string;
  translation: string;
  limit: number;
  model?: string;
  results_count: number;
  results: SemanticSearchResult[];
  generated_at?: string;
  error?: string;
  mode?: string;
}

async function fetchJsonSafe<T>(path: string): Promise<T | null> {
  try {
    const response = await fetch(path);
    if (!response.ok) {
      return null;
    }
    return await response.json();
  } catch (error) {
    console.error(`Failed to fetch ${path}:`, error);
    return null;
  }
}

export default function SemanticSearchTab() {
  const [liveMode, setLiveMode] = useState(true);
  const [staticData, setStaticData] = useState<SemanticSearchData | null>(null);
  const [liveResults, setLiveResults] = useState<SemanticSearchData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showCapabilities, setShowCapabilities] = useState(false);
  const searchingRef = useRef(false);
  const lastQueryRef = useRef<string>('');

  // Load static export (hermetic mode)
  useEffect(() => {
    if (!liveMode) {
      setLoading(true);
      fetchJsonSafe<SemanticSearchData>('/exports/biblescholar/semantic_search.json')
        .then((data) => {
          setStaticData(data);
          setLoading(false);
        })
        .catch(() => {
          setStaticData(null);
          setLoading(false);
        });
    }
  }, [liveMode]);

  // Live API call - memoized to prevent SearchBar debounce loop
  const handleLiveSearch = useCallback(async (query: string) => {
    if (!query.trim()) return;

    // Prevent duplicate searches for the same query or if already searching
    if (searchingRef.current || lastQueryRef.current === query.trim()) {
      return;
    }

    searchingRef.current = true;
    lastQueryRef.current = query.trim();
    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams({
        q: query.trim(),
        limit: '20'
      });

      const response = await fetch(`/api/bible/semantic?${params}`, {
        method: 'GET',
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();

      // API returns { query: str, results: [...], total: N }
      // Map to our SemanticSearchData structure
      setLiveResults({
        query: data.query || query,
        translation: 'KJV',
        limit: 20,
        results_count: data.total || 0,
        results: (data.results || []).map((r: any) => ({
          verse_id: 0, // Not provided by API
          book_name: r.book,
          chapter_num: r.chapter,
          verse_num: r.verse,
          text: r.text,
          translation_source: 'KJV',
          similarity_score: r.similarity
        })),
        mode: 'available',
      });
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Live search failed';
      setError(`Live search failed: ${errorMsg}. Switching to static mode.`);
      setLiveMode(false);
    } finally {
      setLoading(false);
      searchingRef.current = false;
    }
  }, []); // Empty deps - function doesn't depend on any props/state that change

  const data = liveMode ? liveResults : staticData;

  // Map results to Verse interface
  const mappedResults: Verse[] = data?.results.map(r => ({
    book: r.book_name,
    chapter: r.chapter_num,
    verse: r.verse_num,
    text: r.text,
    translation: r.translation_source,
    similarity: r.similarity_score
  })) || [];

  return (
    <div className="flex gap-4 h-full">
      <div className="flex-1 space-y-4 min-w-0">
        {/* Toggle */}
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Semantic Search</h3>
            <div className="flex items-center gap-4">
              <button
                onClick={() => setShowCapabilities(!showCapabilities)}
                className={`text-sm font-medium px-3 py-1.5 rounded transition-colors ${showCapabilities
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-600 hover:bg-gray-100'
                  }`}
              >
                {showCapabilities ? 'Hide Tools' : 'Show Related Tools'}
              </button>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={liveMode}
                  onChange={(e) => {
                    setLiveMode(e.target.checked);
                    setError(null);
                    if (!e.target.checked) {
                      setLiveResults(null);
                      searchingRef.current = false;
                      lastQueryRef.current = '';
                    }
                  }}
                  className="w-4 h-4"
                />
                <span className="text-sm font-medium">
                  {liveMode ? '🟢 Live Search' : '📦 Static Mode'}
                </span>
              </label>
            </div>
          </div>

          {/* Status Banner */}
          {error && (
            <StatusBanner
              mode="error"
              message={error}
              onDismiss={() => setError(null)}
            />
          )}
          {!error && (
            <StatusBanner mode={liveMode ? 'live' : 'hermetic'} />
          )}

          {/* Search Input - Always show, but only functional in Live Mode */}
          <div className="mb-4">
            <SearchBar
              onSearch={liveMode ? handleLiveSearch : () => {}}
              disabled={loading || !liveMode}
              placeholder={liveMode ? "Enter semantic query (e.g., 'hope in difficult times')" : "Enable Live Search to search"}
            />
          </div>
        </div>

        {/* Loading */}
        {loading && <LoadingSpinner message="Searching..." />}

        {/* Results Info */}
        {!loading && data && (
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
            <div className="flex justify-between items-center mb-2">
              <div className="text-sm text-gray-600">
                Query: <strong>"{data.query}"</strong> in <strong>{data.translation}</strong> (
                {data.results_count} results)
              </div>
              {data.generated_at && (
                <div className="text-xs text-gray-400">
                  {new Date(data.generated_at).toLocaleString()}
                </div>
              )}
            </div>
            {data.model && (
              <div className="text-xs text-gray-500 mb-4">
                Model: <span className="font-medium">{data.model}</span>
              </div>
            )}
          </div>
        )}

        {/* Hermetic Mode - No Data */}
        {!loading && !liveMode && !staticData && !error && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <h3 className="font-semibold text-yellow-900 mb-2">WHEN/THEN</h3>
            <div className="text-sm text-yellow-800 space-y-1">
              <p>
                <strong>No semantic search export found.</strong> Run{' '}
                <code className="bg-yellow-100 px-1 py-0.5 rounded text-xs">
                  make export.biblescholar.semantic QUERY="your query"
                </code>{' '}
                to generate semantic search results.
              </p>
              <p className="mt-2">
                Example:{' '}
                <code className="bg-yellow-100 px-1 py-0.5 rounded text-xs">
                  make export.biblescholar.semantic QUERY="hope in difficult times" LIMIT=10
                </code>
              </p>
              <p className="mt-2 text-xs opacity-75">
                Semantic search finds verses by <strong>meaning</strong>, not just keywords. Use concepts,
                questions, or themes to discover thematically related verses.
              </p>
            </div>
          </div>
        )}

        {/* Results List */}
        {!loading && data && (
          <ResultsList
            results={mappedResults}
            showSimilarity={true}
          />
        )}
      </div>

      {/* Sidebar */}
      {showCapabilities && (
        <CapabilitiesSidebar
          query="semantic search bible"
          subsystem="biblescholar"
          className="w-80 flex-shrink-0"
        />
      )}
    </div>
  );
}
