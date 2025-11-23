import React, { useState, useEffect, useCallback, useRef } from 'react';
import LoadingSpinner from './LoadingSpinner';
import StatusBanner from './StatusBanner';
import SearchBar from './SearchBar';
import ResultsList from './ResultsList';
import CapabilitiesSidebar from './CapabilitiesSidebar';
import { Verse } from './VerseCard';

interface LexiconEntry {
    entry_id: number;
    strongs_id: string;
    lemma: string;
    transliteration: string | null;
    definition: string | null;
    usage: string | null;
    gloss: string | null;
}

interface VerseSimilarityResult {
    verse_id: number;
    book_name: string;
    chapter_num: number;
    verse_num: number;
    text: string;
    translation_source: string;
    similarity_score: number;
}

interface VerseContext {
    reference: string;
    primary_text: string;
    secondary_texts: Record<string, string>;
    lexicon_entries: LexiconEntry[];
    similar_verses: VerseSimilarityResult[];
    metadata?: Record<string, unknown>;
}

interface InsightsData {
    reference: string;
    found?: boolean;
    context: VerseContext | null;
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

export default function InsightsTab() {
    const [liveMode, setLiveMode] = useState(false);
    const [staticData, setStaticData] = useState<InsightsData | null>(null);
    const [liveResults, setLiveResults] = useState<InsightsData | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [reference, setReference] = useState('');
    const [showCapabilities, setShowCapabilities] = useState(false);
    const searchingRef = useRef(false);
    const lastQueryRef = useRef<string>('');

    // Load static export (hermetic mode)
    useEffect(() => {
        if (!liveMode) {
            setLoading(true);
            fetchJsonSafe<InsightsData>('/exports/biblescholar/insights.json')
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
    const handleLiveLookup = useCallback(async (ref: string) => {
        if (!ref.trim()) return;
        
        // Prevent duplicate searches for the same query or if already searching
        if (searchingRef.current || lastQueryRef.current === ref.trim()) {
            return;
        }

        searchingRef.current = true;
        lastQueryRef.current = ref.trim();
        setLoading(true);
        setError(null);

        try {
            // Normalize reference format (John 3:16 -> John.3.16)
            const normalizedRef = ref.replace(/\s+/g, '.').replace(/:/g, '.');
            const response = await fetch(`/api/bible/insights/${encodeURIComponent(normalizedRef)}`);

            if (!response.ok) {
                if (response.status === 404) {
                    setLiveResults({
                        reference: ref,
                        found: false,
                        context: null,
                        mode: 'available',
                    });
                    setLoading(false);
                    return;
                }
                throw new Error(`API error: ${response.status}`);
            }

            const data = await response.json();

            if (data.mode === 'db_off') {
                setError('Database offline. Switching to static mode.');
                setLiveMode(false);
            } else if (data.reference) {
                setLiveResults({
                    reference: data.reference,
                    found: true,
                    context: {
                        reference: data.reference,
                        primary_text: data.primary_text || '',
                        secondary_texts: data.secondary_texts || {},
                        lexicon_entries: data.lexicon_entries || [],
                        similar_verses: data.similar_verses || [],
                    },
                    mode: 'available',
                });
            } else {
                setLiveResults({
                    reference: ref,
                    found: false,
                    context: null,
                    mode: 'available',
                });
            }
        } catch (err) {
            setError('Live lookup failed. Switching to static mode.');
            setLiveMode(false);
        } finally {
            setLoading(false);
            searchingRef.current = false;
        }
    }, []); // Empty deps - function doesn't depend on any props/state that change

    const data = liveMode ? liveResults : staticData;

    // Map similar verses to Verse interface
    const mappedSimilarVerses: Verse[] = data?.context?.similar_verses.map(v => ({
        book: v.book_name,
        chapter: v.chapter_num,
        verse: v.verse_num,
        text: v.text,
        translation: v.translation_source,
        similarity: v.similarity_score
    })) || [];

    return (
        <div className="flex gap-4 h-full">
            <div className="flex-1 space-y-4 min-w-0">
                {/* Toggle */}
                <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-semibold text-gray-900">Verse Insights</h3>
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

                    {/* Live Lookup Input */}
                    {liveMode && (
                        <div className="mb-4">
                            <SearchBar
                                onSearch={handleLiveLookup}
                                disabled={loading}
                                placeholder="Enter Bible reference (e.g., John 3:16)"
                                initialValue={reference}
                            />
                        </div>
                    )}
                </div>

                {/* Loading */}
                {loading && <LoadingSpinner message="Loading insights..." />}

                {/* Hermetic Mode - No Data */}
                {!loading && !liveMode && !staticData && !error && (
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                        <h3 className="font-semibold text-yellow-900 mb-2">WHEN/THEN</h3>
                        <div className="text-sm text-yellow-800 space-y-1">
                            <p>
                                <strong>No insights export found.</strong> Run{' '}
                                <code className="bg-yellow-100 px-1 py-0.5 rounded text-xs">
                                    make export.biblescholar.insights REF="Gen.1.1"
                                </code>{' '}
                                to generate verse insights.
                            </p>
                            <p className="mt-2">
                                Example:{' '}
                                <code className="bg-yellow-100 px-1 py-0.5 rounded text-xs">
                                    make export.biblescholar.insights REF="Genesis 1:1"
                                </code>
                            </p>
                        </div>
                    </div>
                )}

                {/* Verse Not Found */}
                {!loading && data && (!data.found || !data.context) && (
                    <div className="bg-white p-8 rounded-lg shadow-sm border border-gray-200 text-center text-gray-500">
                        Verse not found: {data.reference}
                    </div>
                )}

                {/* Insights Display */}
                {!loading && data && data.context && (
                    <>
                        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
                            <div className="flex justify-between items-center mb-2">
                                <div className="text-sm text-gray-600">
                                    Reference: <strong>{data.context.reference}</strong>
                                </div>
                                {data.generated_at && (
                                    <div className="text-xs text-gray-400">
                                        {new Date(data.generated_at).toLocaleString()}
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Primary Text */}
                        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                            <h4 className="text-sm font-semibold text-gray-700 mb-2">Text (KJV)</h4>
                            <p className="text-gray-900 text-lg italic">"{data.context.primary_text}"</p>
                        </div>

                        {/* Secondary Translations */}
                        {Object.keys(data.context.secondary_texts).length > 0 && (
                            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                                <h4 className="text-sm font-semibold text-gray-700 mb-3">Other Translations</h4>
                                <div className="space-y-2">
                                    {Object.entries(data.context.secondary_texts).map(([trans, text]) => (
                                        <div key={trans}>
                                            <span className="text-xs font-medium text-gray-500">{trans}:</span>
                                            <p className="text-gray-700 mt-1">{text}</p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Lexicon Entries */}
                        {data.context.lexicon_entries.length > 0 && (
                            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                                <h4 className="text-sm font-semibold text-gray-700 mb-3">Lexicon (Original Language)</h4>
                                <div className="space-y-3">
                                    {data.context.lexicon_entries.map((entry) => (
                                        <div key={entry.entry_id || entry.strongs_id} className="border-l-4 border-blue-500 pl-3">
                                            <div className="flex items-center gap-2 mb-1">
                                                <span className="font-semibold text-gray-900">{entry.lemma}</span>
                                                <span className="text-xs text-gray-500">
                                                    {entry.strongs_id.startsWith('H') ? 'Hebrew' : 'Greek'} {entry.strongs_id}
                                                </span>
                                            </div>
                                            {entry.gloss && (
                                                <p className="text-sm text-gray-700">{entry.gloss}</p>
                                            )}
                                            {entry.definition && (
                                                <p className="text-xs text-gray-600 mt-1">{entry.definition}</p>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Similar Verses */}
                        {data.context.similar_verses.length > 0 && (
                            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                                <h4 className="text-sm font-semibold text-gray-700 mb-3">Similar Verses (Semantic)</h4>
                                <ResultsList
                                    results={mappedSimilarVerses}
                                    showSimilarity={true}
                                />
                            </div>
                        )}
                    </>
                )}
            </div>

            {/* Sidebar */}
            {showCapabilities && (
                <CapabilitiesSidebar
                    query={data?.reference || ''}
                    subsystem="biblescholar"
                    className="w-80 flex-shrink-0"
                />
            )}
        </div>
    );
}

