import React, { useState } from "react";
import { TileSummaryProps } from "../tileRegistry";

export default function MCPTile({ data, status, reason }: TileSummaryProps) {
    const [testing, setTesting] = useState(false);
    const [testResult, setTestResult] = useState<string | null>(null);

    const proof = data?.proofs || {};
    const proofsCount = data?.proofs_count || 0;
    const allOk = data?.all_ok || false;

    const handleTest = async () => {
        setTesting(true);
        setTestResult(null);
        try {
            // Test MCP bundle proof generation
            const response = await fetch("/api/mcp/test", {
                method: "POST",
            });
            if (response.ok) {
                const result = await response.json();
                setTestResult(`Test passed: ${result.message || "OK"}`);
            } else {
                setTestResult(`Test failed: ${response.statusText}`);
            }
        } catch (error: any) {
            setTestResult(`Test error: ${error.message}`);
        } finally {
            setTesting(false);
        }
    };

    const handleRefresh = async () => {
        try {
            // Trigger MCP proof generation
            const response = await fetch("/api/mcp/refresh", {
                method: "POST",
            });
            if (response.ok) {
                // Reload page data after refresh
                window.location.reload();
            }
        } catch (error) {
            console.error("Failed to refresh MCP data:", error);
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
            {data && (
                <div style={{ fontSize: '0.75rem', color: '#4b5563', marginBottom: '0.5rem' }}>
                    <p style={{ margin: '0.25rem 0' }}>
                        Proofs: {proofsCount} {allOk ? '✅' : '⚠️'}
                    </p>
                    {Object.keys(proof).length > 0 && (
                        <p style={{ margin: '0.25rem 0', fontSize: '0.7rem' }}>
                            {Object.entries(proof).slice(0, 3).map(([key, val]: [string, any]) => 
                                `${key}: ${val?.ok ? '✓' : '✗'}`
                            ).join(', ')}
                        </p>
                    )}
                </div>
            )}
            <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem' }}>
                <button
                    onClick={(e) => {
                        e.stopPropagation();
                        handleTest();
                    }}
                    disabled={testing}
                    style={{
                        padding: '0.25rem 0.5rem',
                        fontSize: '0.7rem',
                        backgroundColor: '#3b82f6',
                        color: 'white',
                        border: 'none',
                        borderRadius: '0.25rem',
                        cursor: testing ? 'not-allowed' : 'pointer',
                        opacity: testing ? 0.6 : 1,
                    }}
                >
                    {testing ? 'Testing...' : 'Test'}
                </button>
                <button
                    onClick={(e) => {
                        e.stopPropagation();
                        handleRefresh();
                    }}
                    style={{
                        padding: '0.25rem 0.5rem',
                        fontSize: '0.7rem',
                        backgroundColor: '#10b981',
                        color: 'white',
                        border: 'none',
                        borderRadius: '0.25rem',
                        cursor: 'pointer',
                    }}
                >
                    Refresh
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

