import { useState, useEffect } from 'react';
import { getSystemHealth, DBHealthData, SystemHealthData } from '../dashboard/src/utils/dbData';
import { getLMIndicator, LMIndicatorData } from '../dashboard/src/utils/modelsData';

export type SystemHealthLevel = 'OK' | 'WARN' | 'ERROR';

export interface LmSlotStatus {
    name: 'local_agent' | 'embedding' | 'reranker' | 'theology';
    provider: string;
    model: string;
    status: 'healthy' | 'degraded' | 'offline';
}

export interface OrchestratorInsights {
    overallLevel: SystemHealthLevel | null;
    dbSummary: string;
    lmSummary: string;
    slots: LmSlotStatus[];
    lastUpdated: string | null;
    hints: string[];
}

/**
 * Hook to fetch and normalize orchestrator insights from static exports.
 * Reads system_health.json and lm_indicator.json (same sources as header/other panels).
 */
export function useInsightsData(): OrchestratorInsights {
    const [insights, setInsights] = useState<OrchestratorInsights>({
        overallLevel: null,
        dbSummary: 'Waiting for data...',
        lmSummary: 'Waiting for data...',
        slots: [],
        lastUpdated: null,
        hints: [],
    });

    useEffect(() => {
        const fetchData = async () => {
            const hints: string[] = [];
            let overallLevel: SystemHealthLevel | null = null;
            let dbSummary = 'Waiting for data...';
            let lmSummary = 'Waiting for data...';
            const slots: LmSlotStatus[] = [];
            let lastUpdated: string | null = null;

            try {
                // Fetch system health and LM indicator (same paths as header/ModelsPanel)
                const [systemHealth, lmIndicator] = await Promise.all([
                    getSystemHealth(),
                    getLMIndicator(),
                ]);

                // Process system health
                if (systemHealth) {
                    const dbHealth = systemHealth.components?.db;
                    const lmHealth = systemHealth.components?.lm;

                    // Determine overall level
                    if (systemHealth.ok === true) {
                        overallLevel = 'OK';
                    } else if (systemHealth.ok === false) {
                        overallLevel = 'ERROR';
                    } else {
                        overallLevel = 'WARN';
                    }

                    // DB summary
                    if (dbHealth) {
                        const mode = dbHealth.mode || 'unknown';
                        if (mode === 'ready') {
                            dbSummary = 'DB ready (Option C — DB is SSOT)';
                        } else if (mode === 'db_off') {
                            dbSummary = 'DB offline (no operations should be considered valid)';
                            overallLevel = 'ERROR';
                        } else if (mode === 'partial') {
                            dbSummary = 'DB partial (some operations may be limited)';
                            if (overallLevel !== 'ERROR') {
                                overallLevel = 'WARN';
                            }
                        } else {
                            dbSummary = `DB mode: ${mode}`;
                        }
                    } else {
                        hints.push('System health snapshot missing; see DB_HEALTH.md runbook.');
                        if (overallLevel !== 'ERROR') {
                            overallLevel = 'WARN';
                        }
                    }

                    // Extract LM slot info if available (future: per-slot breakdown)
                    // For now, we'll use aggregate LM status from lm_indicator
                    if (lmHealth) {
                        const provider = (lmHealth as any).details?.provider || 'unknown';
                        const endpoint = (lmHealth as any).details?.endpoint || 'unknown';
                        // Note: Per-slot breakdown would require additional export structure
                        // For v1, we show aggregate status in lmSummary
                    }
                } else {
                    hints.push('System health snapshot missing; see DB_HEALTH.md runbook.');
                    overallLevel = 'WARN';
                }

                // Process LM indicator
                if (lmIndicator) {
                    const status = lmIndicator.status || 'unknown';
                    const successRate = lmIndicator.success_rate;
                    const errorRate = lmIndicator.error_rate;
                    const totalCalls = lmIndicator.total_calls;
                    const windowDays = lmIndicator.window_days || 7;

                    if (status === 'healthy') {
                        const rateText = successRate !== null && successRate !== undefined
                            ? `${(successRate * 100).toFixed(0)}% success`
                            : 'healthy';
                        lmSummary = `LM status: Healthy (${rateText} over last ${windowDays}d)`;
                    } else if (status === 'degraded') {
                        lmSummary = `LM status: Degraded (check metrics below)`;
                        if (overallLevel === 'OK') {
                            overallLevel = 'WARN';
                        }
                    } else if (status === 'offline') {
                        lmSummary = 'LM status: Offline';
                        if (overallLevel !== 'ERROR') {
                            overallLevel = 'WARN';
                        }
                    } else {
                        lmSummary = 'LM status: Unknown';
                    }

                    // Add metrics to summary if available
                    if (totalCalls !== null && totalCalls !== undefined) {
                        const callsText = totalCalls.toLocaleString();
                        const errorText = errorRate !== null && errorRate !== undefined
                            ? ` · Error rate: ${(errorRate * 100).toFixed(1)}%`
                            : '';
                        lmSummary += ` · Total calls: ${callsText}${errorText}`;
                    }

                    // Extract last updated
                    if (lmIndicator.generated_at) {
                        lastUpdated = lmIndicator.generated_at;
                    }

                    // Generate insights/hints from LM data
                    if (status === 'healthy' && successRate != null && successRate > 0.95) {
                        hints.push(`LM success rate is above 95% in the last ${windowDays} days.`);
                    }
                    if (status === 'degraded' || status === 'offline') {
                        hints.push(`LM stack currently ${status} — check Models panel for details.`);
                    }
                } else {
                    hints.push('LM indicator data not available; run `make reality.green` and check Atlas exports.');
                    if (overallLevel !== 'ERROR') {
                        overallLevel = 'WARN';
                    }
                }

                // DB health insights
                if (systemHealth?.components?.db) {
                    const dbMode = systemHealth.components.db.mode;
                    if (dbMode === 'ready') {
                        hints.push('No DB downtime recorded in the current window.');
                    }
                }

            } catch (error) {
                console.error('Failed to fetch insights data:', error);
                hints.push('Failed to load insights data. Check console for details.');
                overallLevel = 'WARN';
            }

            setInsights({
                overallLevel,
                dbSummary,
                lmSummary,
                slots, // Empty for v1; can be populated when per-slot export is available
                lastUpdated,
                hints,
            });
        };

        fetchData();
        // Poll every 30s (same as header)
        const interval = setInterval(fetchData, 30000);
        return () => clearInterval(interval);
    }, []);

    return insights;
}

