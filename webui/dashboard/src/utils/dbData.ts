// webui/dashboard/src/utils/dbData.ts

// --- Interfaces based on DB health guard schema (all fields optional for tolerance) ---

export interface DBCheckData {
    driver_available?: boolean;
    connection_ok?: boolean;
    graph_stats_ready?: boolean;
}

export interface DBHealthData {
    ok?: boolean;
    mode?: "ready" | "db_off" | "partial";
    checks?: DBCheckData;
    details?: {
        errors?: string[];
    };
}

export interface SystemHealthData {
    ok?: boolean;
    components?: {
        db?: DBHealthData;
        lm?: unknown;
        graph?: unknown;
    };
}

// --- Data Access Functions (null-on-failure pattern) ---

const BASE_URL = '/exports';

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

/**
 * Fetch DB health from /api/status/system (preferred, live data).
 * Falls back to system health export if API unavailable.
 */
export const getDBHealth = async (): Promise<DBHealthData | null> => {
    // Try API endpoint first (preferred - live data)
    try {
        const response = await fetch('/api/status/system');
        if (response.ok) {
            const statusData = await response.json();
            const dbData = statusData.db || {};
            
            // Map API response to expected format
            const dbHealth: DBHealthData = {
                ok: dbData.reachable && dbData.mode === 'ready',
                mode: dbData.mode || 'unknown',
                checks: {
                    // Infer checks from mode and reachable status
                    driver_available: dbData.mode !== 'db_off',
                    connection_ok: dbData.reachable || false,
                    graph_stats_ready: dbData.mode === 'ready',
                },
                details: {
                    errors: dbData.mode === 'db_off' || dbData.mode === 'partial' 
                        ? [dbData.notes || 'Database check failed'] 
                        : [],
                },
            };
            return dbHealth;
        }
    } catch (error) {
        console.warn('Failed to fetch DB health from API, trying exports:', error);
    }

    // Fallback: Try system health export
    const systemHealth = await fetchJsonSafe<SystemHealthData>(`${BASE_URL}/control-plane/system_health.json`);
    if (systemHealth?.components?.db) {
        return systemHealth.components.db;
    }

    // If neither available, return null (hermetic behavior)
    return null;
};

/**
 * Fetch system health aggregate (includes DB, LM, graph).
 */
export const getSystemHealth = (): Promise<SystemHealthData | null> => {
    return fetchJsonSafe<SystemHealthData>(`${BASE_URL}/control-plane/system_health.json`);
};

