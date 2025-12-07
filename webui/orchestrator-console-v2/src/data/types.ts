/**
 * Helper TS types for data flowing into tiles.
 * Phase 20.4 wires real data into these from the view model.
 * Phase 27.C adds typed OA state and workspace surfaces.
 */

/** OA State from share/orchestrator_assistant/STATE.json (Phase 27.B/C) */
export interface OAStateData {
    version?: number;
    source?: string;
    generated_at?: string;
    branch?: string;
    current_phase?: string;
    last_completed_phase?: string;
    reality_green?: boolean;
    checks_summary?: Array<{ name: string; passed: boolean }>;
    dms_hint_summary?: {
        total_hints?: number;
        flows_with_hints?: number;
    };
    surfaces?: Record<string, string>;
    surface_status?: Record<string, boolean>;
}

/** OA Workspace surfaces (Phase 27.C) */
export interface OAWorkspaceData {
    research_index?: string;
    active_prompts?: string;
    decision_log?: unknown[];
    notes?: string;
}

export interface SystemStatusData {
    ssot?: unknown;
    system_health_root?: string;
}

export interface PhaseGovernanceData {
    phase_index?: string;
    summaries?: unknown[];
    ui_reset_text?: string;
}

export interface DocsRegistryData {
    docs_control_root?: string;
    kb_registry?: unknown;
}

export interface AgentStateData {
    orchestrator_state?: unknown;
    oa_state?: OAStateData;
    orchestrator_decisions?: unknown;
    oa_decisions?: unknown;
    oa_workspace?: OAWorkspaceData;
}

export interface TileDataBundle {
    systemStatus: SystemStatusData;
    phaseGovernance: PhaseGovernanceData;
    docsRegistry: DocsRegistryData;
    agentState: AgentStateData;
}
