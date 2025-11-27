import React, { useState } from "react";
import { TileSummaryProps } from "../tileRegistry";

export default function LMTile({ data, status, reason }: TileSummaryProps) {
    const [testing, setTesting] = useState(false);
    const [testResult, setTestResult] = useState<string | null>(null);

    const slots = data?.slots || [];
    const okSlots = slots.filter((s: any) => s.service === "OK");
    const providers = [...new Set(slots.map((s: any) => s.provider).filter(Boolean))];

    const handleTest = async () => {
        setTesting(true);
        setTestResult(null);
        try {
            // Test LM inference
            const response = await fetch("/api/lm/test", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ slot: "local_agent", prompt: "test" }),
            });
            if (response.ok) {
                const result = await response.json();
                setTestResult(`Test passed: ${result.message || "LM available"}`);
            } else {
                setTestResult(`Test failed: ${response.statusText}`);
            }
        } catch (error: any) {
            setTestResult(`Test error: ${error.message}`);
        } finally {
            setTesting(false);
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
            {slots.length > 0 && (
                <div style={{ fontSize: '0.75rem', color: '#4b5563', marginBottom: '0.5rem' }}>
                    <p style={{ margin: '0.25rem 0' }}>Slots: {okSlots.length}/{slots.length} active</p>
                    {providers.length > 0 && (
                        <p style={{ margin: '0.25rem 0' }}>Providers: {providers.join(", ")}</p>
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
            </div>
            {testResult && (
                <div style={{ marginTop: '0.5rem', fontSize: '0.7rem', color: testResult.includes('passed') ? '#10b981' : '#ef4444' }}>
                    {testResult}
                </div>
            )}
        </div>
    );
}

