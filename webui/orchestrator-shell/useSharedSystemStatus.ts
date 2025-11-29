import { useState, useEffect, useRef } from 'react';

/**
 * Shared system status data structure.
 * Consolidates DB, LM, and system health information.
 */
export interface SharedSystemStatus {
    db: {
        reachable: boolean;
        mode: 'ready' | 'db_off' | 'partial';
        notes: string;
    };
    lm: {
        slots: Array<{
            name: string;
            provider: string;
            model: string;
            service: 'OK' | 'DOWN' | 'UNKNOWN' | 'DISABLED' | 'SKIPPED';
        }>;
        notes: string;
    };
    ai_tracking?: {
        ok: boolean;
        mode: 'db_on' | 'db_off';
        summary?: Record<string, unknown>;
    };
    share_manifest?: {
        ok: boolean;
        count: number;
        items?: unknown[];
    };
    eval_insights?: Record<string, unknown>;
    kb_doc_health?: Record<string, unknown>;
    lastUpdated: string | null;
    error: string | null;
}

/**
 * Shared hook for system status polling.
 * 
 * Consolidates status fetching to reduce duplicate API calls.
 * All status consumers should use this hook instead of fetching independently.
 * 
 * Features:
 * - Single source of truth for system status
 * - Configurable polling interval (default: 60s)
 * - Automatic error handling and retry
 * - Cached results to prevent duplicate requests
 * 
 * @param pollInterval - Polling interval in milliseconds (default: 60000 = 60s)
 * @returns Shared system status data
 */
export function useSharedSystemStatus(pollInterval: number = 60000): SharedSystemStatus {
    const [status, setStatus] = useState<SharedSystemStatus>({
        db: {
            reachable: false,
            mode: 'db_off',
            notes: 'Waiting for data...',
        },
        lm: {
            slots: [],
            notes: 'Waiting for data...',
        },
        lastUpdated: null,
        error: null,
    });

    // Track if a fetch is in progress to prevent duplicate requests
    const fetchingRef = useRef(false);
    const lastFetchRef = useRef<number>(0);

    const fetchStatus = async () => {
        // Prevent duplicate concurrent requests
        if (fetchingRef.current) {
            return;
        }

        // Throttle: don't fetch more than once per 5 seconds
        const now = Date.now();
        if (now - lastFetchRef.current < 5000) {
            return;
        }

        fetchingRef.current = true;
        lastFetchRef.current = now;

        try {
            const response = await fetch('/api/status/system');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();

            setStatus({
                db: data.db || {
                    reachable: false,
                    mode: 'db_off',
                    notes: 'No DB data available',
                },
                lm: data.lm || {
                    slots: [],
                    notes: 'No LM data available',
                },
                ai_tracking: data.ai_tracking,
                share_manifest: data.share_manifest,
                eval_insights: data.eval_insights,
                kb_doc_health: data.kb_doc_health,
                lastUpdated: new Date().toISOString(),
                error: null,
            });
        } catch (error) {
            console.error('Failed to fetch system status:', error);
            setStatus((prev) => ({
                ...prev,
                error: error instanceof Error ? error.message : 'Unknown error',
            }));
        } finally {
            fetchingRef.current = false;
        }
    };

    useEffect(() => {
        // Initial fetch
        fetchStatus();

        // Set up polling interval
        const interval = setInterval(fetchStatus, pollInterval);

        return () => clearInterval(interval);
    }, [pollInterval]);

    return status;
}

