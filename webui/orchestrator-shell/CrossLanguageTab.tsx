import { useState, useEffect, useCallback, useRef } from 'react';
import LoadingSpinner from './LoadingSpinner';
import StatusBanner from './StatusBanner';
import SearchBar from './SearchBar';
import SimilarityBadge from './SimilarityBadge';
import CapabilitiesSidebar from './CapabilitiesSidebar';

interface GreekVerse {
  verse_id: number;
  book_name: string;
  chapter_num: number;
  verse_num: number;
  text: string;
  translation_source: string;
}

interface HebrewVerse {
  verse_id: number;
  book_name: string;
  chapter_num: number;
  verse_num: number;
  text: string;
  translation_source: string;
}

interface CrossLanguageConnection {
  hebrew_verse: HebrewVerse;
  greek_verse: GreekVerse;
  similarity_score: number;
}

interface CrossLanguageData {
  strongs_id: string;
  lemma?: string;
  hebrew_verses?: HebrewVerse[];
  connections: CrossLanguageConnection[];
  total_connections?: number;
  connections_count?: number;
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

export default function CrossLanguageTab() {
  const [liveMode, setLiveMode] = useState(false);
  const [staticData, setStaticData] = useState<CrossLanguageData | null>(null);
  const [liveResults, setLiveResults] = useState<CrossLanguageData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [strongsId, setStrongsId] = useState('');
  const [showCapabilities, setShowCapabilities] = useState(false);
  const searchingRef = useRef(false);
  const lastQueryRef = useRef<string>('');

  // Load static export (hermetic mode)
  useEffect(() => {
    if (!liveMode) {
      setLoading(true);
      fetchJsonSafe<CrossLanguageData>('/exports/biblescholar/cross_language.json')
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
  const handleLiveSearch = useCallback(async (strongs: string) => {
    if (!strongs.trim()) return;
    
    // Prevent duplicate searches for the same query or if already searching
    if (searchingRef.current || lastQueryRef.current === strongs.trim().toUpperCase()) {
      return;
    }

    searchingRef.current = true;
    lastQueryRef.current = strongs.trim().toUpperCase();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/bible/cross-language', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ strongs_id: strongs, limit: 10 }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();

      if (data.mode === 'db_off') {
        setError('Database offline. Switching to static mode.');
        setLiveMode(false);
      } else {
        setLiveResults({
          strongs_id: data.strongs_id || strongs,
          connections: data.connections || [],
          connections_count: data.connections_count || 0,
          total_connections: data.connections_count || 0,
          mode: 'available',
        });
      }
    } catch (err) {
      setError('Live search failed. Switching to static mode.');
      setLiveMode(false);
    } finally {
      setLoading(false);
      searchingRef.current = false;
    }
  }, []); // Empty deps - function doesn't depend on any props/state that change

  const data = liveMode ? liveResults : staticData;

  return (
    <div className="flex gap-4 h-full">
      <div className="flex-1 space-y-4 min-w-0">
        {/* Toggle */}
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Cross-Language Connections</h3>
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

          {/* Live Search Input */}
          {liveMode && (
            <div className="mb-4">
              <SearchBar
                onSearch={(val) => handleLiveSearch(val.toUpperCase())}
                disabled={loading}
                placeholder="Enter Strong's number (e.g., H7965)"
                initialValue={strongsId}
              />
            </div>
          )}
        </div>

        {/* Loading */}
        {loading && <LoadingSpinner message="Searching connections..." />}

        {/* Results Header */}
        {!loading && data && (
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
            <div className="flex justify-between items-center mb-2">
              <div className="text-sm text-gray-600">
                Strong's: <strong>{data.strongs_id}</strong>
                {data.lemma && <span> ({data.lemma})</span>} —{' '}
                {data.total_connections ?? data.connections_count ?? 0} connections
              </div>
              {data.generated_at && (
                <div className="text-xs text-gray-400">
                  {new Date(data.generated_at).toLocaleString()}
                </div>
              )}
            </div>
            {data.hebrew_verses && (
              <div className="text-xs text-gray-500">
                Hebrew verses: <span className="font-medium">{data.hebrew_verses.length}</span>
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
                <strong>No cross-language export found.</strong> Run{' '}
                <code className="bg-yellow-100 px-1 py-0.5 rounded text-xs">
                  make export.biblescholar.crosslang STRONGS="H7965"
                </code>{' '}
                to generate cross-language connections.
              </p>
              <p className="mt-2">
                Example:{' '}
                <code className="bg-yellow-100 px-1 py-0.5 rounded text-xs">
                  make export.biblescholar.crosslang STRONGS="H7965" LIMIT=5
                </code>
              </p>
              <p className="mt-2 text-xs opacity-75">
                Cross-language connections find Greek verses semantically similar to Hebrew verses containing
                a specific Strong's number (e.g., H7965 = shalom).
              </p>
            </div>
          </div>
        )}

        {/* Error */}
        {!loading && data && data.error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <h3 className="font-semibold text-red-900 mb-2">Error</h3>
            <p className="text-sm text-red-800">{data.error}</p>
          </div>
        )}

        {/* No Connections */}
        {!loading && data && data.connections.length === 0 && (
          <div className="bg-white p-8 rounded-lg shadow-sm border border-gray-200 text-center text-gray-500">
            No connections found
          </div>
        )}

        {/* Connections List */}
        {!loading && data && data.connections.length > 0 && (
          <div className="space-y-4">
            {data.connections.map((conn, idx) => (
              <div
                key={`${conn.hebrew_verse.verse_id}-${conn.greek_verse.verse_id}-${idx}`}
                className="bg-white p-4 rounded-lg shadow-sm border border-gray-200"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono bg-gray-100 px-2 py-1 rounded">#{idx + 1}</span>
                    <span className="text-sm font-semibold text-gray-700">Connection</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <SimilarityBadge score={conn.similarity_score} />
                  </div>
                </div>

                {/* Hebrew Verse */}
                <div className="mb-3 pb-3 border-b border-gray-200">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-semibold text-orange-700 bg-orange-50 px-2 py-0.5 rounded">
                      Hebrew
                    </span>
                    <span className="font-semibold text-gray-900">
                      {conn.hebrew_verse.book_name} {conn.hebrew_verse.chapter_num}:{conn.hebrew_verse.verse_num}
                    </span>
                    <span className="text-xs text-gray-500">({conn.hebrew_verse.translation_source})</span>
                  </div>
                  <p className="text-gray-700 text-sm">{conn.hebrew_verse.text}</p>
                </div>

                {/* Greek Verse */}
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-semibold text-blue-700 bg-blue-50 px-2 py-0.5 rounded">
                      Greek
                    </span>
                    <span className="font-semibold text-gray-900">
                      {conn.greek_verse.book_name} {conn.greek_verse.chapter_num}:{conn.greek_verse.verse_num}
                    </span>
                    <span className="text-xs text-gray-500">({conn.greek_verse.translation_source})</span>
                  </div>
                  <p className="text-gray-700 text-sm">{conn.greek_verse.text}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Sidebar */}
      {showCapabilities && (
        <CapabilitiesSidebar
          query={data?.strongs_id || ''}
          subsystem="biblescholar"
          className="w-80 flex-shrink-0"
        />
      )}
    </div>
  );
}

