import React from 'react';

interface SimilarityBadgeProps {
    score: number; // 0 to 1
}

export default function SimilarityBadge({ score }: SimilarityBadgeProps) {
    // Determine color and border based on score thresholds
    // >90% = Excellent (green), 75-90% = Good (blue), 50-75% = Fair (yellow), <50% = Poor (gray)
    let colorClass = "bg-gray-50 text-gray-700 border-gray-300";
    if (score >= 0.9) colorClass = "bg-green-50 text-green-700 border-green-300";
    else if (score >= 0.75) colorClass = "bg-blue-50 text-blue-700 border-blue-300";
    else if (score >= 0.5) colorClass = "bg-yellow-50 text-yellow-700 border-yellow-300";

    const percentage = (score * 100).toFixed(0);

    return (
        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${colorClass}`}>
            {percentage}%
        </span>
    );
}
