import React, { useState, useEffect } from 'react';
import LoadingSpinner from './LoadingSpinner';

interface Tool {
    name: string;
    description: string;
    tags: string[];
    subsystem: string;
    visibility: string;
    similarity: number;
    popularity: number;
}

interface CapabilitiesSidebarProps {
    query: string;
    subsystem?: string;
    className?: string;
}

export default function CapabilitiesSidebar({ query, subsystem, className = '' }: CapabilitiesSidebarProps) {
    const [tools, setTools] = useState<Tool[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!query) {
            setTools([]);
            return;
        }

        // Debounce API calls to prevent excessive requests
        const timeoutId = setTimeout(() => {
            setLoading(true);
            setError(null);

            const params = new URLSearchParams({ q: query, limit: '5' });
            if (subsystem) params.append('subsystem', subsystem);

            fetch(`/api/mcp/tools/search?${params}`)
                .then(res => {
                    if (!res.ok) throw new Error(`API error: ${res.status}`);
                    return res.json();
                })
                .then(data => {
                    setTools(data.results || []);
                    setLoading(false);
                })
                .catch(err => {
                    console.error('Failed to fetch tools:', err);
                    setError('Failed to load related tools');
                    setLoading(false);
                });
        }, 1000); // 1s debounce to reduce API calls

        return () => clearTimeout(timeoutId);
    }, [query, subsystem]);

    if (!query) return null;

    return (
        <div className={`bg-gray-50 border-l border-gray-200 p-4 w-80 flex-shrink-0 overflow-y-auto ${className}`}>
            <h3 className="text-sm font-semibold text-gray-700 mb-3 uppercase tracking-wider">
                Related Capabilities
            </h3>

            {loading && <LoadingSpinner message="Finding tools..." />}

            {error && (
                <div className="text-xs text-red-600 bg-red-50 p-2 rounded border border-red-100">
                    {error}
                </div>
            )}

            {!loading && !error && tools.length === 0 && (
                <div className="text-sm text-gray-500 italic">
                    No related tools found.
                </div>
            )}

            <div className="space-y-3">
                {tools.map(tool => (
                    <div key={tool.name} className="bg-white p-3 rounded shadow-sm border border-gray-200 hover:border-blue-300 transition-colors cursor-pointer">
                        <div className="flex justify-between items-start mb-1">
                            <h4 className="text-sm font-medium text-blue-700 break-words">{tool.name}</h4>
                            <span className="text-xs font-mono text-gray-400 bg-gray-100 px-1.5 py-0.5 rounded">
                                {(tool.similarity * 100).toFixed(0)}%
                            </span>
                        </div>
                        <p className="text-xs text-gray-600 mb-2 line-clamp-2">{tool.description}</p>
                        <div className="flex flex-wrap gap-1">
                            {tool.tags.map(tag => (
                                <span key={tag} className="text-[10px] bg-blue-50 text-blue-600 px-1.5 py-0.5 rounded border border-blue-100">
                                    {tag}
                                </span>
                            ))}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
