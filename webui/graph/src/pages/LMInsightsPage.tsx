import React, { useState, useEffect, useRef } from 'react';

interface InferenceData {
  ollama: {
    available: boolean;
    base_url: string;
    available_models: Array<{ id: string; name: string }>;
    active_requests: Array<{
      model: string;
      endpoint: string;
      status: string;
      timestamp: string;
      prompt?: string;
      file_context?: string;
    }>;
    recent_requests: Array<{
      model: string;
      endpoint: string;
      status: string;
      durationMs: number;
      timestamp: string;
      prompt?: string;
      file_context?: string;
    }>;
  };
  lmstudio: {
    available: boolean;
    base_urls: string[];
    available_models: Array<{ id: string; base_url: string }>;
    recent_activity: Array<{
      model: string;
      status: string;
      input_tokens: number;
      output_tokens: number;
      duration_ms: number;
      timestamp: string;
      file_context?: string;
      call_site?: string;
      app_name?: string;
    }>;
  };
  last_updated: string;
}

interface LMInsightsData {
  usage: {
    total_calls: number;
    successful_calls: number;
    failed_calls: number;
    total_tokens_prompt: number;
    total_tokens_completion: number;
    avg_latency_ms: number;
    calls_by_day: Array<{
      date: string;
      calls: number;
      successful: number;
      failed: number;
    }>;
  } | null;
  health: {
    success_rate: number;
    error_rate: number;
    error_types: Record<string, number>;
    recent_errors: Array<{
      timestamp: string;
      error_type: string;
      message: string;
    }>;
  } | null;
  insights: {
    ok: boolean;
    total_calls: number;
    success_rate: number;
    error_rate: number;
    top_error_reason: string | null;
    lm_studio_usage_ratio: number | null;
  } | null;
  generated_at: string | null;
  window_days: number;
}

const LMInsightsPage: React.FC = () => {
  const [data, setData] = useState<InferenceData | null>(null);
  const [insightsData, setInsightsData] = useState<LMInsightsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [insightsLoading, setInsightsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [insightsError, setInsightsError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'ollama' | 'lmstudio' | 'metrics'>('ollama');
  const [flashActive, setFlashActive] = useState(false);
  const previousActiveCountRef = useRef<number>(0);

  const fetchData = async () => {
    try {
      const response = await fetch('/api/inference/models');
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      const jsonData = await response.json();

      // Flash when new active requests appear
      const currentActiveCount = jsonData.ollama?.active_requests?.length || 0;
      if (currentActiveCount > previousActiveCountRef.current) {
        setFlashActive(true);
        setTimeout(() => setFlashActive(false), 2000);
      }
      previousActiveCountRef.current = currentActiveCount;

      setData(jsonData);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch inference data');
    } finally {
      setLoading(false);
    }
  };

  const fetchInsightsData = async () => {
    try {
      const response = await fetch('/api/lm/insights');
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      const jsonData = await response.json();
      setInsightsData(jsonData);
      setInsightsError(null);
    } catch (err) {
      setInsightsError(err instanceof Error ? err.message : 'Failed to fetch LM insights');
    } finally {
      setInsightsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    fetchInsightsData();
    const interval = setInterval(fetchData, 1000); // Real-time: 1 second updates
    const insightsInterval = setInterval(fetchInsightsData, 30000); // Historical: 30 second updates
    return () => {
      clearInterval(interval);
      clearInterval(insightsInterval);
    };
  }, []);

  const getTaskDescription = (req: any): string => {
    // Show what the model is actually working on - promptPreview is the actual prompt text from the API
    if (req.promptPreview || req.inference_summary) {
      const promptText = req.promptPreview || req.inference_summary;
      if (promptText && promptText.length > 0) {
        // Show the actual prompt text in plain language
        return promptText.length > 80 ? `${promptText.substring(0, 80)}...` : promptText;
      }
    }
    if (req.file_context) {
      return `Processing: ${req.file_context}`;
    }
    if (req.call_site) {
      return `Called from: ${req.call_site}`;
    }
    if (req.app_name) {
      return `App: ${req.app_name}`;
    }
    if (req.endpoint === 'chat') {
      return 'Chat completion';
    }
    if (req.endpoint === 'embed') {
      return 'Text embedding';
    }
    if (req.endpoint === 'generate') {
      return 'Text generation';
    }
    return 'Inference task';
  };

  const formatDuration = (ms: number): string => {
    if (ms < 1000) return `${Math.round(ms)}ms`;
    if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
    return `${(ms / 60000).toFixed(1)}m`;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 text-white p-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold mb-2 text-white">Live Inference Monitor</h1>
          <p className="text-gray-300 mb-6">Loading inference activity...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-900 text-white p-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold mb-2 text-white">Live Inference Monitor</h1>
          <div className="bg-red-900 border border-red-700 rounded-lg p-4 text-red-100">
            <strong>Error:</strong> {error}
          </div>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-screen bg-gray-900 text-white p-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold mb-2 text-white">Live Inference Monitor</h1>
          <p className="text-gray-300">No data available</p>
        </div>
      </div>
    );
  }

  const ollama = data.ollama || {};
  const lmstudio = data.lmstudio || {};
  const activeCount = ollama.active_requests?.length || 0;
  const recentCount = (ollama.recent_requests?.length || 0) + (lmstudio.recent_activity?.length || 0);

  return (
    <div className="min-h-full bg-gray-900 text-white p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold mb-2 text-white">Live Inference Monitor</h1>
            <p className="text-gray-300 text-sm">
              Real-time inference activity • Updated every second
            </p>
          </div>
          {data.last_updated && (
            <div className="text-sm text-gray-400">
              {new Date(data.last_updated).toLocaleTimeString()}
            </div>
          )}
        </div>

        {/* Active Inference Alert */}
        {activeCount > 0 && (
          <div
            className={`mb-6 p-4 rounded-lg border-2 ${flashActive
                ? 'bg-yellow-900 border-yellow-500 animate-pulse'
                : 'bg-yellow-900/30 border-yellow-600'
              }`}
          >
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 bg-yellow-400 rounded-full animate-pulse"></div>
              <div>
                <div className="font-semibold text-yellow-200">
                  {activeCount} Active Inference{activeCount !== 1 ? 's' : ''} Running
                </div>
                <div className="text-sm text-yellow-300">
                  Models are currently processing requests
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
            <div className="text-sm text-gray-400 mb-1">Active Now</div>
            <div className={`text-4xl font-bold ${activeCount > 0 ? 'text-yellow-400' : 'text-gray-500'}`}>
              {activeCount}
            </div>
            <div className="text-xs text-gray-500 mt-1">inference{activeCount !== 1 ? 's' : ''} running</div>
          </div>
          <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
            <div className="text-sm text-gray-400 mb-1">Recent Activity</div>
            <div className="text-4xl font-bold text-blue-400">{recentCount}</div>
            <div className="text-xs text-gray-500 mt-1">completed requests</div>
          </div>
          <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
            <div className="text-sm text-gray-400 mb-1">Providers</div>
            <div className="flex gap-4 mt-2">
              {ollama.available && (
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                  <span className="text-sm text-gray-300">Ollama</span>
                </div>
              )}
              {lmstudio.available && (
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                  <span className="text-sm text-gray-300">LM Studio</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Provider Tabs */}
        <div className="mb-6 border-b border-gray-700">
          <nav className="flex space-x-8">
            <button
              onClick={() => setActiveTab('ollama')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'ollama'
                  ? 'text-blue-400 border-blue-400'
                  : 'text-gray-400 border-transparent hover:text-gray-300'
                }`}
            >
              Ollama
            </button>
            <button
              onClick={() => setActiveTab('lmstudio')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'lmstudio'
                  ? 'text-blue-400 border-blue-400'
                  : 'text-gray-400 border-transparent hover:text-gray-300'
                }`}
            >
              LM Studio
            </button>
            <button
              onClick={() => setActiveTab('metrics')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'metrics'
                  ? 'text-blue-400 border-blue-400'
                  : 'text-gray-400 border-transparent hover:text-gray-300'
                }`}
            >
              7-Day Metrics
            </button>
          </nav>
        </div>

        {/* Ollama Tab Content */}
        {activeTab === 'ollama' && (
          <div className="space-y-6">
            {/* Active Requests - Priority Display */}
            {ollama.active_requests && ollama.active_requests.length > 0 && (
              <div className="bg-gray-800 rounded-lg border-2 border-yellow-600 p-6">
                <div className="flex items-center gap-2 mb-4">
                  <div className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse"></div>
                  <h2 className="text-xl font-semibold text-yellow-200">Active Inference</h2>
                </div>
                <div className="space-y-3">
                  {ollama.active_requests.map((req: any, i: number) => (
                    <div
                      key={i}
                      className="bg-gray-900 rounded-lg border border-yellow-600/50 p-4 animate-pulse"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <span className="font-semibold text-white">{req.model || 'Unknown Model'}</span>
                            <span className="text-xs bg-yellow-900 text-yellow-200 px-2 py-1 rounded">
                              {req.status || 'processing'}
                            </span>
                          </div>
                          <div className="text-sm text-white font-medium mb-1">
                            {getTaskDescription(req)}
                          </div>
                        </div>
                        <div className="text-xs text-gray-500">
                          {req.timestamp ? new Date(req.timestamp).toLocaleTimeString() : '—'}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Recent Activity */}
            {ollama.recent_requests && ollama.recent_requests.length > 0 && (
              <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
                <h2 className="text-lg font-semibold mb-4 text-white">Recent Activity</h2>
                <div className="space-y-2">
                  {ollama.recent_requests.slice(0, 10).map((req: any, i: number) => (
                    <div
                      key={i}
                      className="bg-gray-900 rounded-lg border border-gray-700 p-4 hover:border-blue-500 transition-colors"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-1">
                            <span className="font-medium text-white">{req.model || 'Unknown'}</span>
                            <span className="text-xs bg-green-900 text-green-200 px-2 py-1 rounded">
                              {req.status || 'completed'}
                            </span>
                            <span className="text-xs text-gray-400">
                              {formatDuration(req.durationMs || 0)}
                            </span>
                          </div>
                          <div className="text-sm text-white">
                            {getTaskDescription(req)}
                          </div>
                        </div>
                        <div className="text-xs text-gray-500">
                          {req.timestamp ? new Date(req.timestamp).toLocaleTimeString() : '—'}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeCount === 0 && (!ollama.recent_requests || ollama.recent_requests.length === 0) && (
              <div className="bg-gray-800 rounded-lg border border-gray-700 p-12 text-center">
                <div className="text-gray-400 text-lg mb-2">No inference activity</div>
                <div className="text-gray-500 text-sm">Waiting for inference requests...</div>
              </div>
            )}
          </div>
        )}

        {/* LM Studio Tab Content */}
        {activeTab === 'lmstudio' && (
          <div className="space-y-6">
            {lmstudio.recent_activity && lmstudio.recent_activity.length > 0 ? (
              <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
                <h2 className="text-lg font-semibold mb-4 text-white">Recent Activity</h2>
                <div className="space-y-2">
                  {lmstudio.recent_activity.slice(0, 10).map((act: any, i: number) => (
                    <div
                      key={i}
                      className="bg-gray-900 rounded-lg border border-gray-700 p-4 hover:border-blue-500 transition-colors"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-1">
                            <span className="font-medium text-white">{act.model || 'Unknown'}</span>
                            <span className="text-xs bg-green-900 text-green-200 px-2 py-1 rounded">
                              {act.status || 'completed'}
                            </span>
                            <span className="text-xs text-gray-400">
                              {formatDuration(act.duration_ms || 0)}
                            </span>
                            {(act.input_tokens || act.output_tokens) && (
                              <span className="text-xs text-gray-400">
                                {act.input_tokens || 0}→{act.output_tokens || 0} tokens
                              </span>
                            )}
                          </div>
                          <div className="text-sm text-gray-300">
                            {getTaskDescription(act)}
                          </div>
                        </div>
                        <div className="text-xs text-gray-500">
                          {act.timestamp ? new Date(act.timestamp).toLocaleTimeString() : '—'}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="bg-gray-800 rounded-lg border border-gray-700 p-12 text-center">
                <div className="text-gray-400 text-lg mb-2">No inference activity</div>
                <div className="text-gray-500 text-sm">Waiting for inference requests...</div>
              </div>
            )}
          </div>
        )}

        {/* 7-Day Metrics Tab Content */}
        {activeTab === 'metrics' && (
          <div className="space-y-6">
            {insightsLoading ? (
              <div className="bg-gray-800 rounded-lg border border-gray-700 p-12 text-center">
                <div className="text-gray-400 text-lg mb-2">Loading metrics...</div>
              </div>
            ) : insightsError ? (
              <div className="bg-red-900 border border-red-700 rounded-lg p-4 text-red-100">
                <strong>Error:</strong> {insightsError}
              </div>
            ) : insightsData && (insightsData.usage || insightsData.health || insightsData.insights) ? (
              <>
                {/* Summary Cards */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  {insightsData.usage && (
                    <>
                      <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
                        <div className="text-sm text-gray-400 mb-1">Total Calls</div>
                        <div className="text-3xl font-bold text-white">{insightsData.usage.total_calls.toLocaleString()}</div>
                        <div className="text-xs text-gray-500 mt-1">Last {insightsData.window_days} days</div>
                      </div>
                      <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
                        <div className="text-sm text-gray-400 mb-1">Success Rate</div>
                        <div className="text-3xl font-bold text-green-400">
                          {insightsData.health?.success_rate
                            ? `${(insightsData.health.success_rate * 100).toFixed(1)}%`
                            : insightsData.insights?.success_rate
                            ? `${(insightsData.insights.success_rate * 100).toFixed(1)}%`
                            : '—'}
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                          {insightsData.usage.successful_calls} / {insightsData.usage.total_calls}
                        </div>
                      </div>
                      <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
                        <div className="text-sm text-gray-400 mb-1">Avg Latency</div>
                        <div className="text-3xl font-bold text-blue-400">
                          {insightsData.usage.avg_latency_ms
                            ? `${Math.round(insightsData.usage.avg_latency_ms)}ms`
                            : '—'}
                        </div>
                        <div className="text-xs text-gray-500 mt-1">Per request</div>
                      </div>
                      <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
                        <div className="text-sm text-gray-400 mb-1">Total Tokens</div>
                        <div className="text-3xl font-bold text-purple-400">
                          {insightsData.usage.total_tokens_prompt + insightsData.usage.total_tokens_completion > 0
                            ? `${((insightsData.usage.total_tokens_prompt + insightsData.usage.total_tokens_completion) / 1000).toFixed(1)}k`
                            : '—'}
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                          {insightsData.usage.total_tokens_prompt.toLocaleString()} in / {insightsData.usage.total_tokens_completion.toLocaleString()} out
                        </div>
                      </div>
                    </>
                  )}
                </div>

                {/* Usage Details */}
                {insightsData.usage && (
                  <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
                    <h2 className="text-lg font-semibold mb-4 text-white">Usage Statistics</h2>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div>
                        <div className="text-sm text-gray-400">Successful</div>
                        <div className="text-2xl font-bold text-green-400">{insightsData.usage.successful_calls.toLocaleString()}</div>
                      </div>
                      <div>
                        <div className="text-sm text-gray-400">Failed</div>
                        <div className="text-2xl font-bold text-red-400">{insightsData.usage.failed_calls.toLocaleString()}</div>
                      </div>
                      <div>
                        <div className="text-sm text-gray-400">Prompt Tokens</div>
                        <div className="text-2xl font-bold text-white">{insightsData.usage.total_tokens_prompt.toLocaleString()}</div>
                      </div>
                      <div>
                        <div className="text-sm text-gray-400">Completion Tokens</div>
                        <div className="text-2xl font-bold text-white">{insightsData.usage.total_tokens_completion.toLocaleString()}</div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Health Details */}
                {insightsData.health && (
                  <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
                    <h2 className="text-lg font-semibold mb-4 text-white">Health Metrics</h2>
                    <div className="space-y-4">
                      <div>
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-sm text-gray-400">Error Rate</span>
                          <span className="text-lg font-bold text-red-400">
                            {(insightsData.health.error_rate * 100).toFixed(2)}%
                          </span>
                        </div>
                        {insightsData.health.error_types && Object.keys(insightsData.health.error_types).length > 0 && (
                          <div className="mt-4">
                            <div className="text-sm text-gray-400 mb-2">Error Types</div>
                            <div className="space-y-1">
                              {Object.entries(insightsData.health.error_types)
                                .sort(([, a], [, b]) => (b as number) - (a as number))
                                .slice(0, 5)
                                .map(([errorType, count]) => (
                                  <div key={errorType} className="flex justify-between text-sm">
                                    <span className="text-gray-300">{errorType}</span>
                                    <span className="text-gray-400">{count as number}</span>
                                  </div>
                                ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )}

                {/* Insights Summary */}
                {insightsData.insights && (
                  <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
                    <h2 className="text-lg font-semibold mb-4 text-white">Insights Summary</h2>
                    <div className="space-y-2">
                      {insightsData.insights.top_error_reason && (
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-400">Top Error Reason</span>
                          <span className="text-sm text-red-400">{insightsData.insights.top_error_reason}</span>
                        </div>
                      )}
                      {insightsData.insights.lm_studio_usage_ratio !== null && (
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-400">LM Studio Usage Ratio</span>
                          <span className="text-sm text-blue-400">
                            {(insightsData.insights.lm_studio_usage_ratio * 100).toFixed(1)}%
                          </span>
                        </div>
                      )}
                      {insightsData.generated_at && (
                        <div className="flex justify-between mt-4 pt-4 border-t border-gray-700">
                          <span className="text-xs text-gray-500">Last Updated</span>
                          <span className="text-xs text-gray-500">
                            {new Date(insightsData.generated_at).toLocaleString()}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </>
            ) : (
              <div className="bg-gray-800 rounded-lg border border-gray-700 p-12 text-center">
                <div className="text-gray-400 text-lg mb-2">No metrics data available</div>
                <div className="text-gray-500 text-sm">Run the LM metrics export pipeline to populate this data.</div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default LMInsightsPage;
