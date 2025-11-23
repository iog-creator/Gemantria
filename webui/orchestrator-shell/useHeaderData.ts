import { useState, useEffect } from 'react';

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

export function useHeaderData() {
    const [data, setData] = useState<HeaderData>({
        db: { status: 'unknown' },
        lm: { status: 'unknown' },
        system: { status: 'unknown' }
    });

    useEffect(() => {
        const fetchData = async () => {
            try {
                // Fetch system status (includes both DB and LM health)
                const statusRes = await fetch('/api/status/system');
                if (statusRes.ok) {
                    const statusJson = await statusRes.json();
                    
                    // Process DB status
                    const dbData = statusJson.db || {};
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
                    const lmData = statusJson.lm || {};
                    const slots = lmData.slots || [];
                    const okSlots = slots.filter((s: any) => s.service === 'OK');
                    const downSlots = slots.filter((s: any) => s.service === 'DOWN');
                    const providers = [...new Set(slots.map((s: any) => s.provider).filter(Boolean))];
                    
                    let lmStatus: 'healthy' | 'degraded' | 'offline' | 'unknown' = 'unknown';
                    let lmReason = '';
                    
                    if (slots.length === 0) {
                        lmStatus = 'unknown';
                        lmReason = 'No LM slots configured';
                    } else if (okSlots.length === slots.length) {
                        lmStatus = 'healthy';
                        lmReason = providers.length > 0 
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
                    
                    setData({
                        db: {
                            status: dbStatus,
                            reason: dbReason,
                            updatedAt: new Date().toISOString()
                        },
                        lm: {
                            status: lmStatus,
                            reason: lmReason,
                            updatedAt: new Date().toISOString()
                        },
                        system: {
                            status: systemStatus,
                            updatedAt: new Date().toISOString()
                        }
                    });
                } else {
                    // If API fails, set all to unknown
                    console.error("Failed to fetch system status:", statusRes.status, statusRes.statusText);
                    setData({
                        db: { status: 'unknown' },
                        lm: { status: 'unknown' },
                        system: { status: 'unknown' }
                    });
                }
            } catch (error) {
                console.error("Failed to fetch header data", error);
                setData({
                    db: { status: 'unknown' },
                    lm: { status: 'unknown' },
                    system: { status: 'unknown' }
                });
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 60000); // Poll every 60s to reduce load
        return () => clearInterval(interval);
    }, []);

    return data;
}
