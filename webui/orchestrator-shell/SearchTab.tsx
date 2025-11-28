import React, { useState, useEffect, useCallback, useRef } from 'react';
import LoadingSpinner from './LoadingSpinner';
import StatusBanner from './StatusBanner';
import SearchBar from './SearchBar';
import ResultsList from './ResultsList';
import CapabilitiesSidebar from './CapabilitiesSidebar';
import { Verse } from './VerseCard';

interface VerseRecord {
    verse_id: number;
    book_name: string;
    chapter_num: number;
    verse_num: number;
    text: string;
    translation_source: string;
}

interface SearchData {
    query: string;
    translation: string;
    limit: number;
    db_status?: string;
    results_count: number;
    results: VerseRecord[];
    generated_at?: string;
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

export default function SearchTab() {
    const [liveMode, setLiveMode] = useState(false);
    const [staticData, setStaticData] = useState<SearchData | null>(null);
    const [liveResults, setLiveResults] = useState<SearchData | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [showCapabilities, setShowCapabilities] = useState(false);
    const searchingRef = useRef(false);
    const lastQueryRef = useRef<string>('');

    // Load static export (hermetic mode)
    useEffect(() => {
        if (!liveMode) {
            setLoading(true);
            fetchJsonSafe<SearchData>('/exports/biblescholar/search.json')
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
            const response = await fetch('/api/bible/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query, limit: 20, translation: 'KJV' }),
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
                    query: data.query || query,
                    translation: data.translation || 'KJV',
                    limit: data.limit || 20,
                    results_count: data.results_count || 0,
                    results: data.results || [],
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

    // Map results to Verse interface
    const mappedResults: Verse[] = data?.results.map(r => ({
        book: r.book_name,
        chapter: r.chapter_num,
        verse: r.verse_num,
        text: r.text,
        translation: r.translation_source
    })) || [];

    return (
        <div className="flex gap-4 h-full">
            <div className="flex-1 space-y-4 min-w-0">
                {/* Toggle */}
                <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-semibold text-gray-900">Keyword Search</h3>
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
                                onSearch={handleLiveSearch}
                                disabled={loading}
                                placeholder="Enter keyword search (e.g., 'Jesus')"
                            />
                        </div>
                    )}
                </div>

                {/* Loading */}
                {loading && <LoadingSpinner message="Searching..." />}

                {/* Results Header */}
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
                        {data.db_status && (
                            <div className="text-xs text-gray-500">
                                DB Status: <span className="font-medium">{data.db_status}</span>
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
                                <strong>No search export found.</strong> Run{' '}
                                <code className="bg-yellow-100 px-1 py-0.5 rounded text-xs">
                                    make export.biblescholar.search QUERY="your query"
                                </code>{' '}
                                to generate search results.
                            </p>
                            <p className="mt-2">
                                Example:{' '}
                                <code className="bg-yellow-100 px-1 py-0.5 rounded text-xs">
                                    make export.biblescholar.search QUERY="Jesus" TRANSLATION="KJV" LIMIT=20
                                </code>
                            </p>
                        </div>
                    </div>
                )}

                {/* Results List */}
                {!loading && data && (
                    <ResultsList
                        results={mappedResults}
                        showSimilarity={false}
                    />
                )}
            </div>

            {/* Sidebar */}
            {showCapabilities && (
                <CapabilitiesSidebar
                    query={data?.query || ''}
                    subsystem="biblescholar"
                    className="w-80 flex-shrink-0"
                />
            )}
        </div>
    );
}

