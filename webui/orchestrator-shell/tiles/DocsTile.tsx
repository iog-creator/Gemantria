import React, { useState } from "react";
import { TileSummaryProps } from "../tileRegistry";

export default function DocsTile({ data, status, reason }: TileSummaryProps) {
    const [refreshing, setRefreshing] = useState(false);
    const [testResult, setTestResult] = useState<string | null>(null);

    const totals = data?.totals || {};
    const total = totals.total || 0;
    const canonical = totals.canonical || 0;
    const archiveCandidates = totals.archive_candidates || 0;
    const unreviewed = totals.unreviewed || 0;

    const handleRefresh = async () => {
        setRefreshing(true);
        try {
            // Trigger docs dashboard refresh
            const response = await fetch("/api/docs/refresh", {
                method: "POST",
            });
            if (response.ok) {
                // Reload page data after refresh
                setTimeout(() => window.location.reload(), 1000);
            } else {
                setTestResult(`Refresh failed: ${response.statusText}`);
            }
        } catch (error: any) {
            setTestResult(`Refresh error: ${error.message}`);
        } finally {
            setRefreshing(false);
        }
    };

    const handleTest = async () => {
        setTestResult(null);
        try {
            // Test docs summary endpoint
            const response = await fetch("/exports/docs-control/summary.json");
            if (response.ok) {
                const data = await response.json();
                setTestResult(`Test passed: ${data.totals?.total || 0} docs found`);
            } else {
                setTestResult(`Test failed: ${response.statusText}`);
            }
        } catch (error: any) {
            setTestResult(`Test error: ${error.message}`);
        }
    };

    const getBadgeStyle = () => {
        switch (status) {
            case "healthy":
                return { backgroundColor: '#d1fae5', color: '#065f46' };
            case "degraded":
                return { backgroundColor: '#fef3c7', color: '#92400e' };
            case "offline":
                return { backgroundColor: '#fee2e2', color: '#991b1b' };
            default:
                return { backgroundColor: '#f3f4f6', color: '#374151' };
        }
    };

    return (
        <div style={{ fontSize: '0.875rem' }}>
            <div style={{ marginBottom: '0.5rem' }}>
                <span style={{
                    display: 'inline-block',
                    padding: '0.125rem 0.5rem',
                    borderRadius: '0.25rem',
                    fontSize: '0.75rem',
                    fontWeight: 500,
                    ...getBadgeStyle()
                }}>
                    {status}
                </span>
                {reason && <span style={{ marginLeft: '0.5rem', fontSize: '0.75rem', color: '#4b5563' }}>{reason}</span>}
            </div>
            {total > 0 && (
                <div style={{ fontSize: '0.75rem', color: '#4b5563', marginBottom: '0.5rem' }}>
                    <p style={{ margin: '0.25rem 0' }}>Total: {total}</p>
                    <p style={{ margin: '0.25rem 0' }}>Canonical: {canonical}</p>
                    {archiveCandidates > 0 && (
                        <p style={{ margin: '0.25rem 0', fontSize: '0.7rem' }}>Archive: {archiveCandidates}</p>
                    )}
                    {unreviewed > 0 && (
                        <p style={{ margin: '0.25rem 0', fontSize: '0.7rem' }}>Unreviewed: {unreviewed}</p>
                    )}
                </div>
            )}
            <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem' }}>
                <button
                    onClick={(e) => {
                        e.stopPropagation();
                        handleTest();
                    }}
                    style={{
                        padding: '0.25rem 0.5rem',
                        fontSize: '0.7rem',
                        backgroundColor: '#3b82f6',
                        color: 'white',
                        border: 'none',
                        borderRadius: '0.25rem',
                        cursor: 'pointer',
                    }}
                >
                    Test
                </button>
                <button
                    onClick={(e) => {
                        e.stopPropagation();
                        handleRefresh();
                    }}
                    disabled={refreshing}
                    style={{
                        padding: '0.25rem 0.5rem',
                        fontSize: '0.7rem',
                        backgroundColor: '#10b981',
                        color: 'white',
                        border: 'none',
                        borderRadius: '0.25rem',
                        cursor: refreshing ? 'not-allowed' : 'pointer',
                        opacity: refreshing ? 0.6 : 1,
                    }}
                >
                    {refreshing ? 'Refreshing...' : 'Refresh'}
                </button>
            </div>
            {testResult && (
                <div style={{ marginTop: '0.5rem', fontSize: '0.7rem', color: testResult.includes('passed') ? '#10b981' : '#ef4444' }}>
                    {testResult}
                </div>
            )}
        </div>
    );
}
