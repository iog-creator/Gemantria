// webui/dashboard/src/utils/modelsData.ts

// --- Interfaces based on LM export schemas (all fields optional for tolerance) ---

export interface LMIndicatorData {
    status?: "offline" | "healthy" | "degraded";
    reason?: string;
    success_rate?: number;
    error_rate?: number;
    total_calls?: number;
    db_off?: boolean;
    top_error_reason?: string | null;
    window_days?: number;
    generated_at?: string;
    error?: string | null;
}

export interface LMUsage7dData {
    schema?: string;
    generated_at?: string;
    window_days?: number;
    since?: string;
    ok?: boolean;
    connection_ok?: boolean;
    total_calls?: number;
    successful_calls?: number;
    failed_calls?: number;
    total_tokens_prompt?: number;
    total_tokens_completion?: number;
    total_latency_ms?: number;
    avg_latency_ms?: number;
    calls_by_day?: Array<Record<string, unknown>>;
    error?: string | null;
}

export interface LMHealth7dData {
    schema?: string;
    generated_at?: string;
    window_days?: number;
    since?: string;
    ok?: boolean;
    connection_ok?: boolean;
    health_score?: number;
    success_rate?: number;
    avg_latency_ms?: number;
    error_rate?: number;
    total_calls?: number;
    error_types?: Record<string, number>;
    recent_errors?: Array<Record<string, unknown>>;
    error?: string | null;
}

export interface LMInsights7dData {
    schema?: string;
    generated_at?: string;
    window_days?: number;
    since?: string;
    ok?: boolean;
    connection_ok?: boolean;
    db_off?: boolean;
    total_calls?: number;
    successful_calls?: number;
    failed_calls?: number;
    success_rate?: number;
    error_rate?: number;
    lm_studio_calls?: number | null;
    remote_calls?: number | null;
    lm_studio_usage_ratio?: number | null;
    top_error_reason?: string | null;
    error?: string | null;
}

// --- Data Access Functions (null-on-failure pattern) ---

const BASE_URL = '/exports/control-plane';

async function fetchJsonSafe<T>(filename: string): Promise<T | null> {
    try {
        const response = await fetch(`${BASE_URL}/${filename}`);
        if (!response.ok) {
            return null;
        }
        return await response.json();
    } catch (error) {
        console.error(`Failed to fetch ${filename}:`, error);
        return null;
    }
}

export const getLMIndicator = () => fetchJsonSafe<LMIndicatorData>('lm_indicator.json');
export const getLMUsage7d = () => fetchJsonSafe<LMUsage7dData>('lm_usage_7d.json');
export const getLMHealth7d = () => fetchJsonSafe<LMHealth7dData>('lm_health_7d.json');
export const getLMInsights7d = () => fetchJsonSafe<LMInsights7dData>('lm_insights_7d.json');

