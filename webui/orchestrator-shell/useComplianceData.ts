import { useState, useEffect } from 'react';

export type ComplianceLevel = 'OK' | 'WARN' | 'ERROR';

export interface ViolationItem {
    violation_code: string;
    count: number;
    rule_title?: string; // May be populated from RULES_INDEX mapping if available
    severity?: 'HINT' | 'WARN' | 'ERROR'; // May be inferred from violation code
}

export interface ComplianceHeadData {
    schema?: string;
    generated_at?: string;
    ok?: boolean;
    connection_ok?: boolean;
    summary?: {
        window_7d?: {
            runs?: number;
            por_ok_ratio?: number;
            schema_ok_ratio?: number;
            provenance_ok_ratio?: number;
            updated_at?: string;
        };
        window_30d?: {
            runs?: number;
            por_ok_ratio?: number;
            schema_ok_ratio?: number;
            provenance_ok_ratio?: number;
            updated_at?: string;
        };
    } | null;
    error?: string;
}

export interface ViolationsWindowData {
    schema?: string;
    generated_at?: string;
    ok?: boolean;
    connection_ok?: boolean;
    window?: string;
    violations?: ViolationItem[];
    error?: string;
}

export interface OrchestratorCompliance {
    level: ComplianceLevel | null;
    headline: string;
    lastRunAt: string | null;
    stats: {
        totalChecks: number;
        totalHints: number;
        totalWarnings: number;
        totalErrors: number;
    };
    top7d: ViolationItem[];
    top30d: ViolationItem[];
    hints: string[];
}

const BASE_URL = '/exports/control-plane';

async function fetchJsonSafe<T>(path: string): Promise<T | null> {
    try {
        const response = await fetch(path);
        if (!response.ok) {
            return null;
        }
        return await response.json();
    } catch (error) {
        console.error(`Failed to fetch ${path}:`, error);
        return null;
    }
}

/**
 * Infer severity from violation code (heuristic based on common patterns).
 * This is a best-effort mapping; actual severity may vary.
 */
function inferSeverity(code: string): 'HINT' | 'WARN' | 'ERROR' {
    const codeLower = code.toLowerCase();
    if (codeLower.includes('error') || codeLower.includes('strict') || codeLower.includes('fail')) {
        return 'ERROR';
    }
    if (codeLower.includes('warn') || codeLower.includes('warning')) {
        return 'WARN';
    }
    return 'HINT';
}

/**
 * Sort violations by severity (ERROR > WARN > HINT) then by count descending.
 */
function sortViolations(violations: ViolationItem[]): ViolationItem[] {
    const severityOrder = { ERROR: 0, WARN: 1, HINT: 2 };
    return [...violations].sort((a, b) => {
        const aSev = a.severity || inferSeverity(a.violation_code);
        const bSev = b.severity || inferSeverity(b.violation_code);
        const sevDiff = (severityOrder[aSev] || 2) - (severityOrder[bSev] || 2);
        if (sevDiff !== 0) return sevDiff;
        return b.count - a.count;
    });
}

/**
 * Hook to fetch and normalize orchestrator compliance data from static exports.
 * Reads compliance.head.json, top_violations_7d.json, and top_violations_30d.json.
 */
export function useComplianceData(): OrchestratorCompliance {
    const [compliance, setCompliance] = useState<OrchestratorCompliance>({
        level: null,
        headline: 'Waiting for data...',
        lastRunAt: null,
        stats: {
            totalChecks: 0,
            totalHints: 0,
            totalWarnings: 0,
            totalErrors: 0,
        },
        top7d: [],
        top30d: [],
        hints: [],
    });

    useEffect(() => {
        const fetchData = async () => {
            const hints: string[] = [];
            let level: ComplianceLevel | null = null;
            let headline = 'Waiting for data...';
            let lastRunAt: string | null = null;
            const stats = {
                totalChecks: 0,
                totalHints: 0,
                totalWarnings: 0,
                totalErrors: 0,
            };
            let top7d: ViolationItem[] = [];
            let top30d: ViolationItem[] = [];

            try {
                // Fetch all three compliance exports
                const [headData, violations7d, violations30d] = await Promise.all([
                    fetchJsonSafe<ComplianceHeadData>(`${BASE_URL}/compliance.head.json`),
                    fetchJsonSafe<ViolationsWindowData>(`${BASE_URL}/top_violations_7d.json`),
                    fetchJsonSafe<ViolationsWindowData>(`${BASE_URL}/top_violations_30d.json`),
                ]);

                // Process compliance head
                if (headData) {
                    if (headData.generated_at) {
                        lastRunAt = headData.generated_at;
                    }

                    if (headData.ok === true && headData.summary) {
                        // Determine level from summary ratios
                        const summary = headData.summary;
                        const window7d = summary.window_7d;
                        const window30d = summary.window_30d;

                        // Check if any ratios are below threshold (heuristic: < 0.95 = WARN, < 0.8 = ERROR)
                        let hasError = false;
                        let hasWarn = false;

                        if (window7d) {
                            const ratios = [
                                window7d.por_ok_ratio,
                                window7d.schema_ok_ratio,
                                window7d.provenance_ok_ratio,
                            ];
                            for (const ratio of ratios) {
                                if (ratio !== undefined && ratio < 0.8) {
                                    hasError = true;
                                } else if (ratio !== undefined && ratio < 0.95) {
                                    hasWarn = true;
                                }
                            }
                        }

                        if (hasError) {
                            level = 'ERROR';
                            headline = 'Errors present — review top violations';
                        } else if (hasWarn) {
                            level = 'WARN';
                            headline = 'Compliant with warnings — some non-critical issues present';
                        } else {
                            level = 'OK';
                            headline = 'Compliant — no recent ERROR-level violations';
                        }

                        // Extract stats (approximate from ratios)
                        if (window7d?.runs) {
                            stats.totalChecks = window7d.runs;
                        }
                    } else if (headData.ok === false) {
                        level = 'WARN';
                        headline = 'Compliance data unavailable';
                        if (headData.error) {
                            hints.push(`Compliance export error: ${headData.error}`);
                        }
                    }
                } else {
                    hints.push(
                        'Compliance exports not found; run `make reality.green` and check compliance export targets (PLAN-076/078).'
                    );
                    level = 'WARN';
                }

                // Process violations 7d
                if (violations7d && violations7d.violations) {
                    top7d = violations7d.violations.map((v) => ({
                        ...v,
                        severity: v.severity || inferSeverity(v.violation_code),
                    }));
                    top7d = sortViolations(top7d);

                    // Count by severity
                    for (const v of top7d) {
                        const sev = v.severity || inferSeverity(v.violation_code);
                        if (sev === 'ERROR') {
                            stats.totalErrors += v.count;
                        } else if (sev === 'WARN') {
                            stats.totalWarnings += v.count;
                        } else {
                            stats.totalHints += v.count;
                        }
                    }
                }

                // Process violations 30d
                if (violations30d && violations30d.violations) {
                    top30d = violations30d.violations.map((v) => ({
                        ...v,
                        severity: v.severity || inferSeverity(v.violation_code),
                    }));
                    top30d = sortViolations(top30d);
                }

                // Generate insights/hints from data
                if (top7d.length === 0 && top30d.length === 0 && level === 'OK') {
                    hints.push('No violations recorded in the last 7 or 30 days.');
                }

                if (stats.totalErrors > 0) {
                    hints.push(`ERROR-level violations present: ${stats.totalErrors} occurrences in the last 7 days.`);
                } else if (level === 'OK') {
                    hints.push('No ERROR-level violations in the last 7 days.');
                }

                if (top30d.length > 0) {
                    const topViolation = top30d[0];
                    hints.push(
                        `Rule ${topViolation.violation_code} has the highest violation count in the last 30 days (${topViolation.count} occurrences).`
                    );
                }

                if (stats.totalHints > stats.totalWarnings + stats.totalErrors) {
                    hints.push('Hints are dominating; most issues are advisory, not blocking.');
                }

            } catch (error) {
                console.error('Failed to fetch compliance data:', error);
                hints.push('Failed to load compliance data. Check console for details.');
                level = 'WARN';
            }

            setCompliance({
                level,
                headline,
                lastRunAt,
                stats,
                top7d,
                top30d,
                hints,
            });
        };

        fetchData();
        // Poll every 30s (same as other panels)
        const interval = setInterval(fetchData, 30000);
        return () => clearInterval(interval);
    }, []);

    return compliance;
}

