import { useMemo } from 'react';
import { useSharedSystemStatus, SharedSystemStatus } from './useSharedSystemStatus';

interface StatusTile {
    status: 'healthy' | 'degraded' | 'offline' | 'unknown';
    reason?: string;
    updatedAt?: string;
}

interface HeaderData {
    db: StatusTile;
    lm: StatusTile;
    system: StatusTile;
}

/**
 * Hook to fetch header status data.
 * 
 * Refactored to use shared system status hook for performance optimization.
 * Reduces duplicate API calls by reusing cached status data.
 */
export function useHeaderData(): HeaderData {
    const systemStatus = useSharedSystemStatus(60000); // Poll every 60s

    return useMemo(() => {
        // Process DB status
        const dbData = systemStatus.db;
        let dbStatus: 'healthy' | 'degraded' | 'offline' | 'unknown' = 'unknown';
        let dbReason = '';

        if (dbData.mode === 'ready' && dbData.reachable) {
            dbStatus = 'healthy';
            dbReason = 'Ready';
        } else if (dbData.mode === 'partial') {
            dbStatus = 'degraded';
            dbReason = 'Partial (some tables missing)';
        } else if (dbData.mode === 'db_off') {
            dbStatus = 'offline';
            dbReason = 'Database unavailable';
        } else {
            dbStatus = 'unknown';
            dbReason = dbData.notes || 'Unknown status';
        }

        // Process LM status from slots
        const lmData = systemStatus.lm;
        const slots = lmData.slots || [];
        const okSlots = slots.filter((s) => s.service === 'OK');
        const downSlots = slots.filter((s) => s.service === 'DOWN');
        const providers = [...new Set(slots.map((s) => s.provider).filter(Boolean))];

        let lmStatus: 'healthy' | 'degraded' | 'offline' | 'unknown' = 'unknown';
        let lmReason = '';

        if (slots.length === 0) {
            lmStatus = 'unknown';
            lmReason = 'No LM slots configured';
        } else if (okSlots.length === slots.length) {
            lmStatus = 'healthy';
            lmReason =
                providers.length > 0
                    ? `${providers.join(' + ')} (${okSlots.length}/${slots.length} slots)`
                    : `${okSlots.length}/${slots.length} slots OK`;
        } else if (okSlots.length > 0) {
            lmStatus = 'degraded';
            lmReason = `${okSlots.length}/${slots.length} slots OK`;
        } else if (downSlots.length === slots.length) {
            lmStatus = 'offline';
            lmReason = 'All slots down';
        } else {
            lmStatus = 'degraded';
            lmReason = `${okSlots.length}/${slots.length} slots OK`;
        }

        // Compute overall system status
        let systemStatus: 'healthy' | 'degraded' | 'offline' | 'unknown' = 'unknown';
        if (dbStatus === 'offline' || lmStatus === 'offline') {
            systemStatus = 'offline';
        } else if (dbStatus === 'degraded' || lmStatus === 'degraded') {
            systemStatus = 'degraded';
        } else if (dbStatus === 'healthy' && lmStatus === 'healthy') {
            systemStatus = 'healthy';
        } else {
            systemStatus = 'unknown';
        }

        return {
            db: {
                status: dbStatus,
                reason: dbReason,
                updatedAt: systemStatus.lastUpdated || undefined,
            },
            lm: {
                status: lmStatus,
                reason: lmReason,
                updatedAt: systemStatus.lastUpdated || undefined,
            },
            system: {
                status: systemStatus,
                updatedAt: systemStatus.lastUpdated || undefined,
            },
        };
    }, [systemStatus]);
}
