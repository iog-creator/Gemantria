import { loadJson, loadText } from "./loadData";
import type { ViewModel } from "../model/consoleConfig";

export interface ConversationContextData {
    phase_index_text?: string;
    phase_summary_count: number;
    orchestrator_state?: unknown;
    oa_state?: unknown;
    orchestrator_decisions?: unknown;
    oa_decisions?: unknown;
    orchestrator_prompts_text?: string;
    oa_prompts_text?: string;
}

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

export async function loadConversationContext(
    viewModel: ViewModel
): Promise<ConversationContextData> {
    const phaseIndexPath = getPath(viewModel, "phase_index");
    const phaseSummaryPaths = getPaths(viewModel, "phase_summaries") ?? [];

    const orchestratorStatePath = getPath(viewModel, "orchestrator_state");
    const oaStatePath = getPath(viewModel, "oa_state");
    const orchestratorDecisionsPath = getPath(viewModel, "orchestrator_decisions");
    const oaDecisionsPath = getPath(viewModel, "oa_decisions");

    const orchestratorPromptsPath = getPath(viewModel, "orchestrator_prompts");
    const oaPromptsPath = getPath(viewModel, "oa_prompts");

    const [phaseIndexText, ...phaseSummaryJsons] = await Promise.all([
        phaseIndexPath ? loadText(phaseIndexPath) : Promise.resolve(undefined),
        ...phaseSummaryPaths.map((p) => loadJson(p))
    ]);

    const phaseSummaryCount = phaseSummaryJsons.filter(Boolean).length;

    const [
        orchestratorState,
        oaState,
        orchestratorDecisions,
        oaDecisions,
        orchestratorPromptsText,
        oaPromptsText
    ] = await Promise.all([
        orchestratorStatePath
            ? loadJson(orchestratorStatePath)
            : Promise.resolve(undefined),
        oaStatePath ? loadJson(oaStatePath) : Promise.resolve(undefined),
        orchestratorDecisionsPath
            ? loadJson(orchestratorDecisionsPath)
            : Promise.resolve(undefined),
        oaDecisionsPath ? loadJson(oaDecisionsPath) : Promise.resolve(undefined),
        orchestratorPromptsPath
            ? loadText(orchestratorPromptsPath)
            : Promise.resolve(undefined),
        oaPromptsPath ? loadText(oaPromptsPath) : Promise.resolve(undefined)
    ]);

    return {
        phase_index_text: phaseIndexText,
        phase_summary_count: phaseSummaryCount,
        orchestrator_state: orchestratorState,
        oa_state: oaState,
        orchestrator_decisions: orchestratorDecisions,
        oa_decisions: oaDecisions,
        orchestrator_prompts_text: orchestratorPromptsText,
        oa_prompts_text: oaPromptsText
    };
}
