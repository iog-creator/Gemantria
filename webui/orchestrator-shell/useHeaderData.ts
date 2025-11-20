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
                // Fetch LM Indicator
                const lmRes = await fetch('/exports/control-plane/lm_indicator.json');
                if (lmRes.ok) {
                    const lmJson = await lmRes.json();
                    setData(prev => ({
                        ...prev,
                        lm: {
                            status: lmJson.status || 'unknown',
                            reason: lmJson.model,
                            updatedAt: lmJson.timestamp
                        }
                    }));
                }

                // Fetch DB Health (via latest guard validation)
                const dbRes = await fetch('/exports/evidence/latest_guard_validation.json');
                if (dbRes.ok) {
                    const dbJson = await dbRes.json();
                    // Logic to determine DB status from guard validation
                    // This is a simplification; real logic depends on specific guard output structure
                    const dbStatus = dbJson.status === 'pass' ? 'healthy' : 'degraded';
                    setData(prev => ({
                        ...prev,
                        db: {
                            status: dbStatus,
                            updatedAt: dbJson.timestamp
                        },
                        system: {
                            status: dbStatus === 'healthy' ? 'healthy' : 'degraded' // Aggregate
                        }
                    }));
                }
            } catch (error) {
                console.error("Failed to fetch header data", error);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 30000); // Poll every 30s
        return () => clearInterval(interval);
    }, []);

    return data;
}
