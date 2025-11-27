import React, { useState, useMemo } from 'react';
import VerseCard, { Verse } from './VerseCard';

interface ResultsListProps {
    results: Verse[];
    showSimilarity?: boolean;
    emptyMessage?: string;
}

type SortOption = 'relevance' | 'reference';

export default function ResultsList({
    results,
    showSimilarity = false,
    emptyMessage = "No results found. Try a different search term or reference."
}: ResultsListProps) {
    const [sortBy, setSortBy] = useState<SortOption>(showSimilarity ? 'relevance' : 'reference');

    const sortedResults = useMemo(() => {
        const list = results || [];
        const sorted = [...list];
        if (sortBy === 'relevance') {
            sorted.sort((a, b) => (b.similarity || 0) - (a.similarity || 0));
        } else {
            sorted.sort((a, b) => {
                const bookCompare = a.book.localeCompare(b.book);
                if (bookCompare !== 0) return bookCompare;
                if (a.chapter !== b.chapter) return a.chapter - b.chapter;
                return a.verse - b.verse;
            });
        }
        return sorted;
    }, [results, sortBy]);

    if (!results || results.length === 0) {
        return (
            <div className="text-center py-12 px-4">
                <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p className="mt-4 text-sm text-gray-500">{emptyMessage}</p>
                <p className="mt-2 text-xs text-gray-400">
                    Try: "faith", "John 3:16", or "hope in difficult times"
                </p>
            </div>
        );
    }

    return (
        <div className="space-y-5">
            {/* Header with count and controls */}
            <div className="flex justify-between items-center">
                <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-gray-700">
                        Found {results.length} {results.length === 1 ? 'verse' : 'verses'}
                    </span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                    <span className="text-gray-500">Sort by:</span>
                    <select
                        value={sortBy}
                        onChange={(e) => setSortBy(e.target.value as SortOption)}
                        className="border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500 py-1"
                    >
                        {showSimilarity && <option value="relevance">Relevance</option>}
                        <option value="reference">Reference</option>
                    </select>
                </div>
            </div>

            {/* List */}
            <div className="space-y-4">
                {sortedResults.map((verse, index) => (
                    <VerseCard
                        key={`${verse.book}-${verse.chapter}-${verse.verse}-${index}`}
                        verse={verse}
                        showSimilarity={showSimilarity}
                    />
                ))}
            </div>
        </div>
    );
}
