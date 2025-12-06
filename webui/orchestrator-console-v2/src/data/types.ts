/**
 * Helper TS types for data flowing into tiles.
 * Phase 20.4 wires real data into these from the view model.
 */

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
    oa_state?: unknown;
    orchestrator_decisions?: unknown;
    oa_decisions?: unknown;
}

export interface TileDataBundle {
    systemStatus: SystemStatusData;
    phaseGovernance: PhaseGovernanceData;
    docsRegistry: DocsRegistryData;
    agentState: AgentStateData;
}
