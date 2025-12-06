import React from "react";
import type { TileDataBundle } from "../data/types";

interface RightStatusPaneProps {
    tileData: TileDataBundle | null;
}

export const RightStatusPane: React.FC<RightStatusPaneProps> = ({ tileData }) => {
    const systemStatus = tileData?.systemStatus;
    const phaseGovernance = tileData?.phaseGovernance;
    const docsRegistry = tileData?.docsRegistry;
    const agentState = tileData?.agentState;

    const ssotLoaded = systemStatus?.ssot != null;
    const controlPlaneRoot = systemStatus?.system_health_root;

    const phaseIndexSnippet = phaseGovernance?.phase_index
        ? phaseGovernance.phase_index.slice(0, 120)
        : undefined;
    const phaseSummaryCount = phaseGovernance?.summaries?.length ?? 0;
    const uiResetPresent =
        phaseGovernance?.ui_reset_text != null &&
        phaseGovernance.ui_reset_text.trim().length > 0;

    const docsRoot = docsRegistry?.docs_control_root;
    const kbHasEntries =
        docsRegistry?.kb_registry &&
        typeof docsRegistry.kb_registry === "object" &&
        Object.keys(docsRegistry.kb_registry).length > 0;

    const orchestratorHasState =
        agentState?.orchestrator_state != null ||
        agentState?.orchestrator_decisions != null;
    const oaHasState =
        agentState?.oa_state != null || agentState?.oa_decisions != null;

    return (
        <aside className="right-status">
            <section className="tile tile--system-status">
                <h2>System Status</h2>
                <ul>
                    <li>SSOT surface loaded: {ssotLoaded ? "yes" : "no"}</li>
                    <li>
                        Control-plane exports root: <br />
                        <code>{controlPlaneRoot ?? "(not configured in view model)"}</code>
                    </li>
                </ul>
            </section>

            <section className="tile tile--phase-governance">
                <h2>Phase &amp; Governance</h2>
                <ul>
                    <li>Phase index snippet:</li>
                    <li>
                        <code>
                            {phaseIndexSnippet ?? "(phase index markdown not loaded yet)"}
                        </code>
                    </li>
                    <li>Phase summaries loaded: {phaseSummaryCount}</li>
                    <li>UI reset decision present: {uiResetPresent ? "yes" : "no"}</li>
                </ul>
            </section>

            <section className="tile tile--docs-registry">
                <h2>Docs &amp; Registry</h2>
                <ul>
                    <li>
                        Docs-control exports root:
                        <br />
                        <code>{docsRoot ?? "(not configured in view model)"}</code>
                    </li>
                    <li>KB registry has entries: {kbHasEntries ? "yes" : "no"}</li>
                </ul>
            </section>

            <section className="tile tile--orchestrator-oa">
                <h2>Orchestrator &amp; OA</h2>
                <ul>
                    <li>Orchestrator state/decisions loaded: {orchestratorHasState ? "yes" : "no"}</li>
                    <li>OA state/decisions loaded: {oaHasState ? "yes" : "no"}</li>
                </ul>
            </section>
        </aside>
    );
};
