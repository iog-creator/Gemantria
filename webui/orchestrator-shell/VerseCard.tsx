import React, { useState } from 'react';
import SimilarityBadge from './SimilarityBadge';

export interface Verse {
    book: string;
    chapter: number;
    verse: number;
    text: string;
    translation?: string;
    similarity?: number; // Optional similarity score
}

interface VerseCardProps {
    verse: Verse;
    showSimilarity?: boolean;
}

export default function VerseCard({ verse, showSimilarity = false }: VerseCardProps) {
    const [expanded, setExpanded] = useState(false);
    const shouldTruncate = verse.text.length > 200;
    const displayText = expanded || !shouldTruncate ? verse.text : verse.text.slice(0, 200) + '...';

    // Determine card styling based on similarity score
    const getBorderColor = () => {
        if (!showSimilarity || verse.similarity === undefined) return 'border-gray-200';
        if (verse.similarity >= 0.9) return 'border-green-200';
        if (verse.similarity >= 0.75) return 'border-blue-200';
        if (verse.similarity >= 0.5) return 'border-yellow-200';
        return 'border-gray-200';
    };

    return (
        <div className={`bg-white overflow-hidden shadow-sm rounded-lg border ${getBorderColor()} hover:shadow-md transition-all duration-200`}>
            <div className="px-5 py-4">
                <div className="flex items-start justify-between gap-3">
                    <h3 className="text-base font-semibold text-gray-900">
                        {verse.book} {verse.chapter}:{verse.verse}
                    </h3>
                    <div className="flex items-center gap-2 flex-shrink-0">
                        {verse.translation && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-600">
                                {verse.translation}
                            </span>
                        )}
                        {showSimilarity && verse.similarity !== undefined && (
                            <SimilarityBadge score={verse.similarity} />
                        )}
                    </div>
                </div>
                <div className="mt-3">
                    <p className="text-sm text-gray-700 leading-relaxed">
                        {displayText}
                    </p>
                    {shouldTruncate && (
                        <button
                            onClick={() => setExpanded(!expanded)}
                            className="mt-2 text-xs text-blue-600 hover:text-blue-800 font-medium"
                        >
                            {expanded ? 'Show less' : 'Read more'}
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
}
