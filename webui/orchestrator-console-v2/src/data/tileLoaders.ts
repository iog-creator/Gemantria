import { loadJson, loadText } from "./loadData";
import type {
    SystemStatusData,
    PhaseGovernanceData,
    DocsRegistryData,
    AgentStateData,
    TileDataBundle
} from "./types";
import type { ViewModel } from "../model/consoleConfig";

/**
 * Helper to get a single-path data source from the view model.
 */
function getPath(vm: ViewModel, key: string): string | undefined {
    const ds = vm.data_sources[key];
    return ds?.path;
}

/**
 * Helper to get multi-path data source from the view model.
 */
function getPaths(vm: ViewModel, key: string): string[] | undefined {
    const ds = vm.data_sources[key];
    return ds?.paths;
}

export async function loadSystemStatusData(
    viewModel: ViewModel
): Promise<SystemStatusData> {
    const ssotPath = getPath(viewModel, "ssot_surface");
    const controlPlanePath = getPath(viewModel, "control_plane_exports");

    const [ssot] = await Promise.all([
        ssotPath ? loadJson(ssotPath) : Promise.resolve(undefined)
        // NOTE: control-plane exports is a directory; in a later phase we may
        // load specific JSON files from it. For now we just surface the path.
    ]);

    return {
        ssot,
        system_health_root: controlPlanePath
    };
}

export async function loadPhaseGovernanceData(
    viewModel: ViewModel
): Promise<PhaseGovernanceData> {
    const phaseIndexPath = getPath(viewModel, "phase_index");
    const phaseSummaryPaths = getPaths(viewModel, "phase_summaries") ?? [];
    const uiDecisionPath = getPath(viewModel, "ui_decision");

    const [phaseIndexText, uiDecisionText, ...summaryJsons] = await Promise.all([
        phaseIndexPath ? loadText(phaseIndexPath) : Promise.resolve(undefined),
        uiDecisionPath ? loadText(uiDecisionPath) : Promise.resolve(undefined),
        ...phaseSummaryPaths.map((p) => loadJson(p))
    ]);

    const summaries = summaryJsons.filter(Boolean);

    return {
        phase_index: phaseIndexText,
        summaries,
        ui_reset_text: uiDecisionText
    };
}

export async function loadDocsRegistryData(
    viewModel: ViewModel
): Promise<DocsRegistryData> {
    const docsExportsPath = getPath(viewModel, "docs_control_exports");
    const kbRegistryPath = getPath(viewModel, "kb_registry");

    const kbRegistry = kbRegistryPath ? await loadJson(kbRegistryPath) : undefined;

    return {
        docs_control_root: docsExportsPath,
        kb_registry: kbRegistry
    };
}

export async function loadAgentStateData(
    viewModel: ViewModel
): Promise<AgentStateData> {
    const orchestratorStatePath = getPath(viewModel, "orchestrator_state");
    const oaStatePath = getPath(viewModel, "oa_state");
    const orchestratorDecisionsPath = getPath(viewModel, "orchestrator_decisions");
    const oaDecisionsPath = getPath(viewModel, "oa_decisions");

    const [orchestratorState, oaState, orchestratorDecisions, oaDecisions] =
        await Promise.all([
            orchestratorStatePath ? loadJson(orchestratorStatePath) : Promise.resolve(undefined),
            oaStatePath ? loadJson(oaStatePath) : Promise.resolve(undefined),
            orchestratorDecisionsPath
                ? loadJson(orchestratorDecisionsPath)
                : Promise.resolve(undefined),
            oaDecisionsPath ? loadJson(oaDecisionsPath) : Promise.resolve(undefined)
        ]);

    return {
        orchestrator_state: orchestratorState,
        oa_state: oaState,
        orchestrator_decisions: orchestratorDecisions,
        oa_decisions: oaDecisions
    };
}

export async function loadTileData(
    viewModel: ViewModel
): Promise<TileDataBundle> {
    const [systemStatus, phaseGovernance, docsRegistry, agentState] =
        await Promise.all([
            loadSystemStatusData(viewModel),
            loadPhaseGovernanceData(viewModel),
            loadDocsRegistryData(viewModel),
            loadAgentStateData(viewModel)
        ]);

    return {
        systemStatus,
        phaseGovernance,
        docsRegistry,
        agentState
    };
}
