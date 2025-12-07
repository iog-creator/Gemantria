import React from "react";
import type { OAStateData } from "../data/types";

interface KernelHealthTileProps {
    oaState: OAStateData | undefined;
}

/**
 * Kernel Health Tile (Phase 27.C)
 * 
 * Displays kernel health from OA state:
 * - Branch / Phase line
 * - Reality Green badge
 * - Checks summary
 * - DMS hint summary
 */
export const KernelHealthTile: React.FC<KernelHealthTileProps> = ({ oaState }) => {
    if (!oaState) {
        return (
            <section className="tile tile--kernel-health">
                <h2>Kernel Health</h2>
                <div className="tile-status tile-status--loading">
                    Loading kernel state...
                </div>
            </section>
        );
    }

    const { branch, current_phase, last_completed_phase, reality_green, checks_summary, dms_hint_summary } = oaState;

    const passedChecks = checks_summary?.filter(c => c.passed).length ?? 0;
    const totalChecks = checks_summary?.length ?? 0;
    const allPassing = passedChecks === totalChecks && totalChecks > 0;

    return (
        <section className="tile tile--kernel-health">
            <h2>Kernel Health</h2>

            {/* Branch / Phase line */}
            <div className="kernel-phase-line">
                <code className="kernel-branch">{branch ?? "unknown"}</code>
                <span className="kernel-phase">
                    Phase {current_phase ?? "?"}
                    {last_completed_phase && (
                        <span className="kernel-phase-completed">
                            (last: {last_completed_phase})
                        </span>
                    )}
                </span>
            </div>

            {/* Reality Green badge */}
            <div className={`reality-badge ${reality_green ? "reality-badge--green" : "reality-badge--red"}`}>
                {reality_green ? "✅ Reality Green" : "❌ Reality Red"}
            </div>

            {/* Checks summary */}
            <div className="checks-summary">
                <span className={allPassing ? "checks-summary--pass" : "checks-summary--warn"}>
                    {passedChecks}/{totalChecks} checks passing
                </span>
            </div>

            {/* DMS Hint summary */}
            {dms_hint_summary && (
                <div className="dms-hint-summary">
                    <span>{dms_hint_summary.total_hints ?? 0} hints</span>
                    <span className="dms-hint-flows">
                        across {dms_hint_summary.flows_with_hints ?? 0} flows
                    </span>
                </div>
            )}

            {/* Failing checks (if any) */}
            {!allPassing && checks_summary && (
                <ul className="failing-checks">
                    {checks_summary
                        .filter(c => !c.passed)
                        .slice(0, 3)
                        .map((c, i) => (
                            <li key={i} className="failing-check">
                                ❌ {c.name}
                            </li>
                        ))}
                </ul>
            )}
        </section>
    );
};
