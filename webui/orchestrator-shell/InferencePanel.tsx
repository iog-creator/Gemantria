import React, { useState, useEffect } from "react";
import { TileExpandedProps } from "./tileRegistry";

export default function InferencePanel({ data }: TileExpandedProps) {
    const [inferenceData, setInferenceData] = useState<any>(data);
    const [loading, setLoading] = useState(!data);
    const [error, setError] = useState<string | null>(null);

    // Auto-refresh data every 5 seconds
    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await fetch("/api/inference/models");
                if (response.ok) {
                    const newData = await response.json();
                    setInferenceData(newData);
                    setError(null);
                } else {
                    setError(`Failed to fetch: ${response.status}`);
                }
            } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to fetch inference data");
            } finally {
                setLoading(false);
            }
        };

        // Use provided data if available, otherwise fetch
        if (data && (data.ollama || data.lmstudio)) {
            setInferenceData(data);
            setLoading(false);
        } else {
            fetchData();
        }

        // Set up auto-refresh
        const interval = setInterval(fetchData, 5000);
        return () => clearInterval(interval);
    }, [data]);

    const ollama = inferenceData?.ollama || {};
    const lmstudio = inferenceData?.lmstudio || {};

    const hasOllama = ollama.available || false;
    const hasLMStudio = lmstudio.available || false;

    if (loading) {
        return (
            <div className="p-6">
                <div className="text-center text-gray-800">Loading inference data...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-6">
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
                    <strong>Error:</strong> {error}
                </div>
            </div>
        );
    }

    return (
        <div className="p-6 bg-white">
            <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-3">
                    <span className="text-3xl">🔮</span>
                    Inference Models & Activity
                </h2>
                {inferenceData?.last_updated && (
                    <div className="text-xs text-gray-600">
                        Updated: {new Date(inferenceData.last_updated).toLocaleString()}
                    </div>
                )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Ollama Card */}
                <div className={`border-2 rounded-lg p-6 ${hasOllama ? 'bg-white border-green-300' : 'bg-gray-50 border-gray-300'}`}>
                    <div className="flex justify-between items-start mb-4">
                        <h3 className="text-xl font-semibold text-gray-900">Ollama</h3>
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${hasOllama ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                            {hasOllama ? 'Online' : 'Offline'}
                        </span>
                    </div>

                    {hasOllama ? (
                        <div className="space-y-4">
                            <div>
                                <div className="text-xs text-gray-600 mb-1">Base URL</div>
                                <div className="text-sm text-gray-800 font-mono">{ollama.base_url || 'N/A'}</div>
                            </div>

                            <div>
                                <h4 className="text-sm font-medium text-gray-700 uppercase tracking-wider mb-2">Active Requests</h4>
                                <div className="text-3xl font-bold text-gray-900">{(ollama.active_requests?.length || 0)}</div>
                            </div>

                            <div>
                                <h4 className="text-sm font-medium text-gray-700 uppercase tracking-wider mb-2">
                                    Available Models ({ollama.available_models?.length || 0})
                                </h4>
                                <div className="flex flex-wrap gap-2">
                                    {ollama.available_models && ollama.available_models.length > 0 ? (
                                        ollama.available_models.map((m: any, i: number) => (
                                            <span key={i} className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded font-mono">
                                                {typeof m === 'string' ? m : m.name || m.id || m.model || 'unknown'}
                                            </span>
                                        ))
                                    ) : (
                                        <span className="text-sm text-gray-500">No models found</span>
                                    )}
                                </div>
                            </div>

                            {ollama.recent_requests && ollama.recent_requests.length > 0 && (
                                <div>
                                    <h4 className="text-sm font-medium text-gray-700 uppercase tracking-wider mb-2">
                                        Recent Activity ({ollama.recent_requests.length})
                                    </h4>
                                    <div className="space-y-2 max-h-48 overflow-y-auto">
                                        {ollama.recent_requests.slice(0, 10).map((req: any, i: number) => (
                                            <div key={i} className="text-xs bg-gray-50 p-2 rounded border border-gray-200">
                                                <div className="font-medium text-gray-800">{req.model || 'unknown'}</div>
                                                {req.prompt && (
                                                    <div className="text-gray-600 mt-1 truncate">{req.prompt.slice(0, 100)}</div>
                                                )}
                                                {req.tokens && (
                                                    <div className="text-gray-500 mt-1">Tokens: {req.tokens}</div>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    ) : (
                        <p className="text-gray-600 italic">Ollama service not reachable</p>
                    )}
                </div>

                {/* LM Studio Card */}
                <div className={`border-2 rounded-lg p-6 ${hasLMStudio ? 'bg-white border-green-300' : 'bg-gray-50 border-gray-300'}`}>
                    <div className="flex justify-between items-start mb-4">
                        <h3 className="text-xl font-semibold text-gray-900">LM Studio</h3>
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${hasLMStudio ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                            {hasLMStudio ? 'Online' : 'Offline'}
                        </span>
                    </div>

                    {hasLMStudio ? (
                        <div className="space-y-4">
                            {lmstudio.base_urls && lmstudio.base_urls.length > 0 && (
                                <div>
                                    <div className="text-xs text-gray-600 mb-1">Base URLs</div>
                                    <div className="space-y-1">
                                        {lmstudio.base_urls.map((url: string, i: number) => (
                                            <div key={i} className="text-sm text-gray-800 font-mono">{url}</div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            <div>
                                <h4 className="text-sm font-medium text-gray-700 uppercase tracking-wider mb-2">
                                    Available Models ({lmstudio.available_models?.length || 0})
                                </h4>
                                <div className="flex flex-wrap gap-2 max-h-48 overflow-y-auto">
                                    {lmstudio.available_models && lmstudio.available_models.length > 0 ? (
                                        lmstudio.available_models.map((m: any, i: number) => (
                                            <span key={i} className="text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded font-mono">
                                                {typeof m === 'string' ? m : m.id || m.name || 'unknown'}
                                            </span>
                                        ))
                                    ) : (
                                        <span className="text-sm text-gray-500">No models found</span>
                                    )}
                                </div>
                            </div>

                            {lmstudio.recent_activity && lmstudio.recent_activity.length > 0 && (
                                <div>
                                    <h4 className="text-sm font-medium text-gray-700 uppercase tracking-wider mb-2">
                                        Recent Activity ({lmstudio.recent_activity.length})
                                    </h4>
                                    <div className="space-y-2 max-h-48 overflow-y-auto">
                                        {lmstudio.recent_activity.slice(0, 10).map((act: any, i: number) => (
                                            <div key={i} className="text-xs bg-gray-50 p-2 rounded border border-gray-200">
                                                <div className="font-medium text-gray-800">{act.model || 'unknown'}</div>
                                                {act.tokens && (
                                                    <div className="text-gray-600 mt-1">Tokens: {act.tokens}</div>
                                                )}
                                                {act.duration_ms && (
                                                    <div className="text-gray-600 mt-1">Duration: {act.duration_ms}ms</div>
                                                )}
                                                {act.call_site && (
                                                    <div className="text-gray-500 mt-1 font-mono text-xs">{act.call_site}</div>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    ) : (
                        <p className="text-gray-600 italic">LM Studio service not reachable</p>
                    )}
                </div>
            </div>

            <div className="mt-6 text-xs text-gray-600 text-center">
                Auto-refreshing every 5 seconds
            </div>
        </div>
    );
}
