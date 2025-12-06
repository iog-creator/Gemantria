/**
 * Console model helper for Orchestrator Console v2.
 *
 * This file encodes the shapes and locations of the canonical JSON models:
 *   - share/orchestrator/CONSOLE_SCHEMA.json
 *   - share/orchestrator/VIEW_MODEL.json
 *
 * Those JSON files are the truth sources for regions, tiles, modes,
 * data_sources, and bindings.
 */

export const CONSOLE_SCHEMA_PATH = "/share/orchestrator/CONSOLE_SCHEMA.json";
export const VIEW_MODEL_PATH = "/share/orchestrator/VIEW_MODEL.json";

export type RegionId = "conversation" | "right_status" | "left_nav";
export type ModeId = "overview" | "docs" | "temporal" | "forecast" | "graph";
export type TileId = "system_status" | "phase_governance" | "docs_registry" | "orchestrator_oa";

export interface ConsoleTileSchema {
    region: RegionId;
    role: string;
    sources: string[];
    description: string;
}

export interface ConsoleSchema {
    version: number;
    description: string;
    regions: Record<RegionId, { role: string; description: string }>;
    modes: Record<ModeId, { label: string; panels: string[] }>;
    tiles: Record<TileId, ConsoleTileSchema>;
    surfaces: {
        core: Record<string, string>;
        agents: Record<string, string>;
        exports: Record<string, string>;
    };
}

export interface DataSourceConfig {
    path?: string;
    paths?: string[];
    type: string;
    used_by: string[];
}

export interface ViewModel {
    version: number;
    data_sources: Record<string, DataSourceConfig>;
    bindings: {
        conversation: string[];
        right_status: Record<TileId, string[]>;
        left_nav: { modes: ModeId[] };
        panels: Record<string, string[]>;
    };
    status_indicators: Record<string, { source: string; description: string }>;
}

/**
 * Load console schema from share/orchestrator/CONSOLE_SCHEMA.json
 * NOTE: These loaders are stubs. In a later phase we will:
 *   - Decide the correct URL base for serving share/ into the UI
 *   - Add error handling and caching
 */
export async function loadConsoleSchema(): Promise<ConsoleSchema> {
    const res = await fetch(CONSOLE_SCHEMA_PATH);
    if (!res.ok) {
        throw new Error(`Failed to load console schema from ${CONSOLE_SCHEMA_PATH}`);
    }
    return (await res.json()) as ConsoleSchema;
}

/**
 * Load view model from share/orchestrator/VIEW_MODEL.json
 */
export async function loadViewModel(): Promise<ViewModel> {
    const res = await fetch(VIEW_MODEL_PATH);
    if (!res.ok) {
        throw new Error(`Failed to load view model from ${VIEW_MODEL_PATH}`);
    }
    return (await res.json()) as ViewModel;
}
