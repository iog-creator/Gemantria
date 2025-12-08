import React from "react";
import type { OAWorkspaceData } from "../data/types";

interface OAWorkspacePanelProps {
    workspace: OAWorkspaceData | undefined;
}

/**
 * OA Workspace Panel (Phase 27.C)
 * 
 * Displays OA research context (not SSOT, just OA working state):
 * - Active prompts / current focus
 * - Research index links
 * - Recent decisions
 * - Notes (if any)
 */
export const OAWorkspacePanel: React.FC<OAWorkspacePanelProps> = ({ workspace }) => {
    if (!workspace) {
        return null;
    }

    const { research_index, active_prompts, decision_log, notes } = workspace;

    // Parse active prompts (simple markdown parsing)
    const promptLines = active_prompts
        ?.split("\n")
        .filter(line => line.trim().startsWith("-") || line.trim().startsWith("*"))
        .map(line => line.trim().replace(/^[-*]\s*/, ""));

    // Parse research index sections
    const researchSections = research_index
        ?.split("\n")
        .filter(line => line.trim().startsWith("-") || line.trim().match(/^\d+\./))
        .map(line => line.trim().replace(/^[-*\d.]\s*/, ""));

    const hasContent = promptLines?.length || researchSections?.length || decision_log?.length;

    if (!hasContent) {
        return null;
    }

    return (
        <section className="tile tile--oa-workspace">
            <h2>OA Workspace</h2>

            {/* Active prompts / current focus */}
            {promptLines && promptLines.length > 0 && (
                <div className="oa-focus">
                    <h3>Current Focus</h3>
                    <ul className="oa-focus-list">
                        {promptLines.slice(0, 5).map((prompt, i) => (
                            <li key={i}>{prompt}</li>
                        ))}
                    </ul>
                </div>
            )}

            {/* Research index */}
            {researchSections && researchSections.length > 0 && (
                <div className="oa-research">
                    <h3>Research Index</h3>
                    <ul className="oa-research-list">
                        {researchSections.slice(0, 5).map((section, i) => (
                            <li key={i} className="oa-research-item">
                                {section}
                            </li>
                        ))}
                    </ul>
                </div>
            )}

            {/* Recent decisions */}
            {decision_log && decision_log.length > 0 && (
                <div className="oa-decisions">
                    <h3>Recent Decisions</h3>
                    <ul className="oa-decisions-list">
                        {decision_log.slice(0, 3).map((decision, i) => {
                            const d = decision as { summary?: string; timestamp?: string };
                            return (
                                <li key={i} className="oa-decision-item">
                                    {d.summary ?? JSON.stringify(decision).slice(0, 60)}
                                </li>
                            );
                        })}
                    </ul>
                </div>
            )}

            {/* Notes indicator */}
            {notes && notes.trim().length > 0 && (
                <div className="oa-notes-indicator">
                    <span className="oa-notes-badge">📝 Notes available</span>
                </div>
            )}
        </section>
    );
};
