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
 * Fetch DB health from system health export (components.db).
 * Falls back to evidence/guard validation if system health not available.
 */
export const getDBHealth = async (): Promise<DBHealthData | null> => {
    // Try system health export first (preferred)
    const systemHealth = await fetchJsonSafe<SystemHealthData>(`${BASE_URL}/control-plane/system_health.json`);
    if (systemHealth?.components?.db) {
        return systemHealth.components.db;
    }

    // Fallback: Try evidence/guard validation (may contain DB health info)
    const guardValidation = await fetchJsonSafe<{ data?: { db_health?: DBHealthData } }>(
        `${BASE_URL}/evidence/latest_guard_validation.json`
    );
    if (guardValidation?.data?.db_health) {
        return guardValidation.data.db_health;
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

