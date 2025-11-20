export interface TemporalPatternsResult<T = unknown> {
    ok: boolean;
    data: T | null;
    error?: string;
}

async function fetchJson<T>(path: string): Promise<TemporalPatternsResult<T>> {
    try {
        const res = await fetch(path, { cache: "no-store" });
        if (!res.ok) {
            return { ok: false, data: null, error: `HTTP ${res.status}` };
        }
        const json = (await res.json()) as T;
        return { ok: true, data: json };
    } catch (err) {
        return { ok: false, data: null, error: "Failed to load export JSON" };
    }
}

export async function loadTemporalPatterns<T = unknown>(): Promise<TemporalPatternsResult<T>> {
    // Path must match the webui-contract for temporal exports.
    return fetchJson<T>("/exports/temporal_patterns.json");
}

export async function loadForecastPatterns<T = unknown>(): Promise<TemporalPatternsResult<T>> {
    // Path must match the webui-contract for forecast exports.
    return fetchJson<T>("/exports/pattern_forecast.json");
}
