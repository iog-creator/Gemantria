import React, { useState, useEffect, useCallback, useRef } from 'react';
import LoadingSpinner from './LoadingSpinner';
import StatusBanner from './StatusBanner';
import SearchBar from './SearchBar';
import CapabilitiesSidebar from './CapabilitiesSidebar';

interface LexiconEntry {
    entry_id: number;
    strongs_id: string;
    lemma: string;
    transliteration: string | null;
    definition: string | null;
    usage: string | null;
    gloss: string | null;
}

interface LexiconData {
    strongs_id: string;
    db_status?: string;
    found?: boolean;
    entry: LexiconEntry | null;
    generated_at?: string;
    mode?: string;
    language?: string;
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

export default function LexiconTab() {
    const [liveMode, setLiveMode] = useState(false);
    const [staticData, setStaticData] = useState<LexiconData | null>(null);
    const [liveResults, setLiveResults] = useState<LexiconData | null>(null);
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
            fetchJsonSafe<LexiconData>('/exports/biblescholar/lexicon.json')
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
    const handleLiveLookup = useCallback(async (strongs: string) => {
        if (!strongs.trim()) return;
        
        // Prevent duplicate searches for the same query or if already searching
        const normalized = strongs.trim().toUpperCase();
        if (searchingRef.current || lastQueryRef.current === normalized) {
            return;
        }

        searchingRef.current = true;
        lastQueryRef.current = normalized;
        setLoading(true);
        setError(null);

        try {
            const response = await fetch(`/api/bible/lexicon/${encodeURIComponent(strongs)}`);

            if (!response.ok) {
                if (response.status === 404) {
                    setLiveResults({
                        strongs_id: strongs,
                        found: false,
                        entry: null,
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
            } else {
                setLiveResults({
                    strongs_id: data.strongs_id,
                    found: true,
                    entry: data.lemma ? {
                        entry_id: 0,
                        strongs_id: data.strongs_id,
                        lemma: data.lemma,
                        transliteration: null,
                        definition: null,
                        usage: null,
                        gloss: data.gloss || null,
                    } : null,
                    mode: 'available',
                    language: data.language,
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

    return (
        <div className="flex gap-4 h-full">
            <div className="flex-1 space-y-4 min-w-0">
                {/* Toggle */}
                <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-semibold text-gray-900">Lexicon Lookup</h3>
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
                                onSearch={(val) => handleLiveLookup(val.toUpperCase())}
                                disabled={loading}
                                placeholder="Enter Strong's number (e.g., H7965, G1)"
                                initialValue={strongsId}
                            />
                        </div>
                    )}
                </div>

                {/* Loading */}
                {loading && <LoadingSpinner message="Looking up..." />}

                {/* Results Header */}
                {!loading && data && (
                    <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
                        <div className="flex justify-between items-center mb-2">
                            <div className="text-sm text-gray-600">
                                Strong's: <strong>{data.strongs_id}</strong>
                                {data.language && <span className="ml-2">({data.language})</span>}
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
                                <strong>No lexicon export found.</strong> Run{' '}
                                <code className="bg-yellow-100 px-1 py-0.5 rounded text-xs">
                                    make export.biblescholar.lexicon STRONGS="H0001"
                                </code>{' '}
                                to generate lexicon entry.
                            </p>
                            <p className="mt-2">
                                Examples:{' '}
                                <code className="bg-yellow-100 px-1 py-0.5 rounded text-xs">
                                    make export.biblescholar.lexicon STRONGS="H1"
                                </code>{' '}
                                (Hebrew) or{' '}
                                <code className="bg-yellow-100 px-1 py-0.5 rounded text-xs">
                                    make export.biblescholar.lexicon STRONGS="G1"
                                </code>{' '}
                                (Greek)
                            </p>
                        </div>
                    </div>
                )}

                {/* Entry Not Found */}
                {!loading && data && (!data.found || !data.entry) && (
                    <div className="bg-white p-8 rounded-lg shadow-sm border border-gray-200 text-center text-gray-500">
                        Entry not found for Strong's {data.strongs_id}
                    </div>
                )}

                {/* Entry Display */}
                {!loading && data && data.entry && (
                    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                        <div className="space-y-4">
                            <div>
                                <h4 className="text-sm font-semibold text-gray-700 mb-1">Lemma</h4>
                                <p className="text-lg font-medium text-gray-900">{data.entry.lemma}</p>
                            </div>

                            {data.entry.transliteration && (
                                <div>
                                    <h4 className="text-sm font-semibold text-gray-700 mb-1">Transliteration</h4>
                                    <p className="text-gray-700">{data.entry.transliteration}</p>
                                </div>
                            )}

                            {data.entry.gloss && (
                                <div>
                                    <h4 className="text-sm font-semibold text-gray-700 mb-1">Gloss</h4>
                                    <p className="text-gray-700">{data.entry.gloss}</p>
                                </div>
                            )}

                            {data.entry.definition && (
                                <div>
                                    <h4 className="text-sm font-semibold text-gray-700 mb-1">Definition</h4>
                                    <p className="text-gray-700 whitespace-pre-wrap">{data.entry.definition}</p>
                                </div>
                            )}

                            {data.entry.usage && (
                                <div>
                                    <h4 className="text-sm font-semibold text-gray-700 mb-1">Usage</h4>
                                    <p className="text-gray-700 whitespace-pre-wrap">{data.entry.usage}</p>
                                </div>
                            )}

                            <div className="pt-4 border-t border-gray-200">
                                <div className="text-xs text-gray-500">
                                    {data.entry.entry_id > 0 && `Entry ID: ${data.entry.entry_id} | `}
                                    Strong's: {data.entry.strongs_id}
                                </div>
                            </div>
                        </div>
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

