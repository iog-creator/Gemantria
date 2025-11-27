import { TileStatus } from "./Tile";

export interface TileAdapterResult {
    data: any;
    status: TileStatus;
    reason?: string;
    lastUpdated?: string;
}

async function fetchJsonSafe<T>(url: string): Promise<T | null> {
    try {
        const response = await fetch(url);
        if (!response.ok) return null;
        
        // Check content-type to ensure it's JSON, not HTML (404 pages)
        const contentType = response.headers.get("content-type");
        if (!contentType || !contentType.includes("application/json")) {
            return null;
        }
        
        const text = await response.text();
        if (!text || text.trim().startsWith("<!DOCTYPE")) {
            // HTML response (likely 404 page)
            return null;
        }
        
        return JSON.parse(text);
    } catch (error) {
        // Silently handle errors - this is expected for missing exports (hermetic behavior)
        return null;
    }
}

export async function dbTileAdapter(): Promise<TileAdapterResult> {
    try {
        const statusRes = await fetch("/api/status/system");
        if (statusRes.ok) {
            const statusJson = await statusRes.json();
            const dbData = statusJson.db || {};
            
            let status: TileStatus = "unknown";
            let reason = "";
            
            if (dbData.mode === "ready" && dbData.reachable) {
                status = "healthy";
                reason = "Ready";
            } else if (dbData.mode === "partial") {
                status = "degraded";
                reason = "Partial (some tables missing)";
            } else if (dbData.mode === "db_off") {
                status = "offline";
                reason = "Database unavailable";
            } else {
                status = "unknown";
                reason = dbData.notes || "Unknown status";
            }
            
            return {
                data: dbData,
                status,
                reason,
                lastUpdated: new Date().toISOString(),
            };
        }
    } catch (error) {
        console.warn("Failed to fetch DB status:", error);
    }
    
    // Fallback: try static export
    const systemHealth = await fetchJsonSafe<any>("/exports/control-plane/system_health.json");
    if (systemHealth?.components?.db) {
        const db = systemHealth.components.db;
        let status: TileStatus = "unknown";
        if (db.mode === "ready") status = "healthy";
        else if (db.mode === "partial") status = "degraded";
        else if (db.mode === "db_off") status = "offline";
        
        return {
            data: db,
            status,
            reason: db.mode,
            lastUpdated: systemHealth.generated_at,
        };
    }
    
    return {
        data: null,
        status: "unknown",
        reason: "No DB health data available",
    };
}

export async function lmTileAdapter(): Promise<TileAdapterResult> {
    try {
        const statusRes = await fetch("/api/status/system");
        if (statusRes.ok) {
            const statusJson = await statusRes.json();
            const lmData = statusJson.lm || {};
            const slots = lmData.slots || [];
            
            const okSlots = slots.filter((s: any) => s.service === "OK");
            const downSlots = slots.filter((s: any) => s.service === "DOWN");
            
            let status: TileStatus = "unknown";
            let reason = "";
            
            if (okSlots.length > 0 && downSlots.length === 0) {
                status = "healthy";
                reason = `${okSlots.length} slot(s) active`;
            } else if (okSlots.length > 0 && downSlots.length > 0) {
                status = "degraded";
                reason = `${okSlots.length} active, ${downSlots.length} down`;
            } else if (downSlots.length > 0) {
                status = "offline";
                reason = "All slots down";
            } else {
                status = "unknown";
                reason = "No LM data available";
            }
            
            return {
                data: lmData,
                status,
                reason,
                lastUpdated: new Date().toISOString(),
            };
        }
    } catch (error) {
        console.warn("Failed to fetch LM status:", error);
    }
    
    // Fallback: try static export
    const lmIndicator = await fetchJsonSafe<any>("/exports/control-plane/lm_indicator.json");
    if (lmIndicator) {
        return {
            data: lmIndicator,
            status: lmIndicator.status as TileStatus || "unknown",
            reason: lmIndicator.status,
            lastUpdated: lmIndicator.generated_at,
        };
    }
    
    return {
        data: null,
        status: "unknown",
        reason: "No LM data available",
    };
}

export async function systemTileAdapter(): Promise<TileAdapterResult> {
    try {
        const statusRes = await fetch("/api/status/system");
        if (statusRes.ok) {
            const statusJson = await statusRes.json();
            
            // Aggregate status from DB and LM
            const dbStatus = statusJson.db?.mode || "unknown";
            const lmData = statusJson.lm || {};
            const slots = lmData.slots || [];
            const lmOk = slots.some((s: any) => s.service === "OK");
            
            let status: TileStatus = "unknown";
            let reason = "";
            
            if (dbStatus === "ready" && lmOk) {
                status = "healthy";
                reason = "All systems operational";
            } else if (dbStatus === "ready" || lmOk) {
                status = "degraded";
                reason = "Some systems offline";
            } else {
                status = "offline";
                reason = "Systems unavailable";
            }
            
            return {
                data: statusJson,
                status,
                reason,
                lastUpdated: new Date().toISOString(),
            };
        }
    } catch (error) {
        console.warn("Failed to fetch system status:", error);
    }
    
    // Fallback: try static export
    const systemHealth = await fetchJsonSafe<any>("/exports/control-plane/system_health.json");
    if (systemHealth) {
        let status: TileStatus = "unknown";
        if (systemHealth.ok === true) status = "healthy";
        else if (systemHealth.ok === false) status = "offline";
        
        return {
            data: systemHealth,
            status,
            reason: systemHealth.ok ? "All systems OK" : "Some systems offline",
            lastUpdated: systemHealth.generated_at,
        };
    }
    
    return {
        data: null,
        status: "unknown",
        reason: "No system health data available",
    };
}

export async function inferenceTileAdapter(): Promise<TileAdapterResult> {
    try {
        const response = await fetch("/api/inference/models");
        if (response.ok) {
            const data = await response.json();
            const hasOllama = data.ollama?.available || false;
            const hasLMStudio = data.lmstudio?.available || false;
            
            let status: TileStatus = "unknown";
            let reason = "";
            
            if (hasOllama && hasLMStudio) {
                status = "healthy";
                reason = "Ollama + LM Studio available";
            } else if (hasOllama || hasLMStudio) {
                status = "degraded";
                reason = hasOllama ? "Ollama only" : "LM Studio only";
            } else {
                status = "offline";
                reason = "No inference providers available";
            }
            
            return {
                data,
                status,
                reason,
                lastUpdated: data.last_updated,
            };
        }
    } catch (error) {
        console.warn("Failed to fetch inference models:", error);
    }
    
    return {
        data: null,
        status: "unknown",
        reason: "No inference data available",
    };
}

export async function docsTileAdapter(): Promise<TileAdapterResult> {
    // Try API endpoint first (if available)
    try {
        const response = await fetch("/api/docs/summary");
        if (response.ok) {
            const data = await response.json();
            return {
                data: data,
                status: "healthy",
                reason: `${data.totals?.total || 0} docs`,
                lastUpdated: data.generated_at || new Date().toISOString(),
            };
        }
    } catch (error) {
        console.warn("Failed to fetch docs summary from API:", error);
    }
    
    // Fallback to static export
    const summary = await fetchJsonSafe<any>("/exports/docs-control/summary.json");
    if (summary) {
        return {
            data: summary,
            status: "healthy",
            reason: `${summary.totals?.total || 0} docs`,
            lastUpdated: summary.generated_at,
        };
    }
    
    return {
        data: null,
        status: "unknown",
        reason: "No docs data available",
    };
}

export async function graphTileAdapter(): Promise<TileAdapterResult> {
    const stats = await fetchJsonSafe<any>("/exports/graph_stats.json");
    if (stats) {
        const nodeCount = stats.nodes?.total || 0;
        const edgeCount = stats.edges?.total || 0;
        
        return {
            data: stats,
            status: nodeCount > 0 ? "healthy" : "unknown",
            reason: `${nodeCount} nodes, ${edgeCount} edges`,
            lastUpdated: stats.generated_at,
        };
    }
    
    return {
        data: null,
        status: "unknown",
        reason: "No graph data available",
    };
}

export async function temporalTileAdapter(): Promise<TileAdapterResult> {
    const patterns = await fetchJsonSafe<any>("/exports/temporal_patterns.json");
    if (patterns) {
        return {
            data: patterns,
            status: "healthy",
            reason: "Temporal patterns available",
            lastUpdated: patterns.generated_at,
        };
    }
    
    return {
        data: null,
        status: "unknown",
        reason: "No temporal data available",
    };
}

export async function forecastTileAdapter(): Promise<TileAdapterResult> {
    const forecast = await fetchJsonSafe<any>("/exports/pattern_forecast.json");
    if (forecast) {
        return {
            data: forecast,
            status: "healthy",
            reason: "Forecast available",
            lastUpdated: forecast.generated_at,
        };
    }
    
    return {
        data: null,
        status: "unknown",
        reason: "No forecast data available",
    };
}

export async function mcpTileAdapter(): Promise<TileAdapterResult> {
    // Try API endpoint first (if available)
    try {
        const response = await fetch("/api/mcp/status");
        if (response.ok) {
            const data = await response.json();
            return {
                data: data,
                status: data.all_ok ? "healthy" : "degraded",
                reason: data.all_ok ? "All proofs OK" : "Some proofs failed",
                lastUpdated: data.generated_at || new Date().toISOString(),
            };
        }
    } catch (error) {
        console.warn("Failed to fetch MCP status from API:", error);
    }
    
    // Fallback to static export
    const proof = await fetchJsonSafe<any>("/exports/mcp/bundle_proof.json");
    if (proof) {
        return {
            data: proof,
            status: proof.all_ok ? "healthy" : "degraded",
            reason: proof.all_ok ? "All proofs OK" : "Some proofs failed",
            lastUpdated: proof.generated_at,
        };
    }
    
    return {
        data: null,
        status: "unknown",
        reason: "No MCP proof data available",
    };
}

export async function autopilotTileAdapter(): Promise<TileAdapterResult> {
    const summary = await fetchJsonSafe<any>("/exports/control-plane/autopilot_summary.json");
    if (summary) {
        return {
            data: summary,
            status: summary.ok && summary.connection_ok !== false ? "healthy" : "offline",
            reason: summary.ok ? "Connected" : "Disconnected",
            lastUpdated: summary.generated_at,
        };
    }
    
    return {
        data: null,
        status: "unknown",
        reason: "No autopilot data available",
    };
}

// Adapter registry
export const tileAdapters: Record<string, () => Promise<TileAdapterResult>> = {
    db: dbTileAdapter,
    lm: lmTileAdapter,
    system: systemTileAdapter,
    inference: inferenceTileAdapter,
    docs: docsTileAdapter,
    graph: graphTileAdapter,
    temporal: temporalTileAdapter,
    forecast: forecastTileAdapter,
    mcp: mcpTileAdapter,
    autopilot: autopilotTileAdapter,
};

