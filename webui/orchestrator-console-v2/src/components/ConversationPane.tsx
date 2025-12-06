import React from "react";
import type { ConversationContextData } from "../data/conversationContext";

interface ConversationPaneProps {
    conversationData: ConversationContextData | null;
}

function renderPromptsBlock(label: string, text?: string) {
    if (!text || !text.trim()) {
        return (
            <div className="prompts-block">
                <h3>{label}</h3>
                <p>(no active prompts loaded)</p>
            </div>
        );
    }

    const lines = text.split(/\r?\n/).filter((line) => line.trim().length > 0);

    return (
        <div className="prompts-block">
            <h3>{label}</h3>
            <ul>
                {lines.map((line, idx) => (
                    <li key={idx}>
                        <code>{line}</code>
                    </li>
                ))}
            </ul>
        </div>
    );
}

export const ConversationPane: React.FC<ConversationPaneProps> = ({
    conversationData
}) => {
    const phaseIndexSnippet = conversationData?.phase_index_text
        ? conversationData.phase_index_text.slice(0, 160)
        : null;

    const phaseSummaryCount = conversationData?.phase_summary_count ?? 0;

    const orchestratorHasState =
        conversationData?.orchestrator_state != null ||
        conversationData?.orchestrator_decisions != null;
    const oaHasState =
        conversationData?.oa_state != null || conversationData?.oa_decisions != null;

    return (
        <section className="conversation-pane">
            <header className="conversation-pane__header">
                <h1>Orchestrator Console v2</h1>
                <p>
                    Chat-first console. This pane will eventually host the live conversation
                    between the Orchestrator and PM.
                </p>
            </header>

            <div className="conversation-pane__body">
                <h2>Current Context</h2>
                <ul>
                    <li>
                        Phase index snippet:
                        <br />
                        <code>
                            {phaseIndexSnippet ?? "(phase index markdown not loaded yet)"}
                        </code>
                    </li>
                    <li>Phase summaries available: {phaseSummaryCount}</li>
                    <li>
                        Orchestrator state/decisions loaded:{" "}
                        {orchestratorHasState ? "yes" : "no"}
                    </li>
                    <li>OA state/decisions loaded: {oaHasState ? "yes" : "no"}</li>
                </ul>

                <h2>Actionable Prompts</h2>
                {renderPromptsBlock(
                    "Orchestrator Active Prompts",
                    conversationData?.orchestrator_prompts_text
                )}
                {renderPromptsBlock(
                    "OA Active Prompts",
                    conversationData?.oa_prompts_text
                )}

                <p>In future phases, this pane will show:</p>
                <ul>
                    <li>Recent orchestrator decisions and OA proposals</li>
                    <li>Inline links to relevant share/ surfaces and exports</li>
                    <li>Structured prompts that can be sent to Cursor and OA.</li>
                </ul>
            </div>
        </section>
    );
};
