import React, { useState } from "react";
import { TileSummaryProps } from "../tileRegistry";

export default function InferenceTile({ data, status, reason }: TileSummaryProps) {
    const [testing, setTesting] = useState(false);
    const [testResult, setTestResult] = useState<string | null>(null);

    const ollama = data?.ollama || {};
    const lmstudio = data?.lmstudio || {};
    const hasOllama = ollama.available || false;
    const hasLMStudio = lmstudio.available || false;
    
    // Show model activity
    const ollamaActive = ollama.active_requests || 0;
    const ollamaRecent = ollama.recent_requests?.length || 0;
    const lmstudioRecent = lmstudio.recent_activity?.length || 0;
    const totalActivity = ollamaActive + ollamaRecent + lmstudioRecent;

    const handleTest = async () => {
        setTesting(true);
        setTestResult(null);
        try {
            // Test inference by making a simple API call
            const response = await fetch("/api/inference/test", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ model: "test", prompt: "test" }),
            });
            if (response.ok) {
                const result = await response.json();
                setTestResult(`Test passed: ${result.message || "Inference available"}`);
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
                {reason && <span style={{ marginLeft: '0.5rem', fontSize: '0.75rem', color: '#1f2937' }}>{reason}</span>}
            </div>
            {(hasOllama || hasLMStudio) && (
                <div style={{ fontSize: '0.75rem', color: '#1f2937', marginBottom: '0.5rem' }}>
                    <p style={{ margin: '0.25rem 0' }}>
                        {hasOllama && hasLMStudio ? "Ollama + LM Studio" :
                         hasOllama ? "Ollama" :
                         hasLMStudio ? "LM Studio" : "None"}
                    </p>
                    {totalActivity > 0 && (
                        <p style={{ margin: '0.25rem 0', fontSize: '0.7rem', color: '#10b981', fontWeight: 500 }}>
                            Activity: {ollamaActive > 0 && `${ollamaActive} active`} {ollamaRecent > 0 && `${ollamaRecent} recent`} {lmstudioRecent > 0 && `${lmstudioRecent} LM Studio`}
                        </p>
                    )}
                    {ollama.available_models && ollama.available_models.length > 0 && (
                        <p style={{ margin: '0.25rem 0', fontSize: '0.7rem' }}>
                            Models: {ollama.available_models.slice(0, 2).map((m: any) => typeof m === 'string' ? m : m.name || m.model || 'unknown').join(', ')}{ollama.available_models.length > 2 ? '...' : ''}
                        </p>
                    )}
                    {lmstudio.available_models && lmstudio.available_models.length > 0 && (
                        <p style={{ margin: '0.25rem 0', fontSize: '0.7rem' }}>
                            LM Studio: {lmstudio.available_models.slice(0, 2).map((m: any) => typeof m === 'string' ? m : m.id || m.name || 'unknown').join(', ')}{lmstudio.available_models.length > 2 ? '...' : ''}
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
            </div>
            {testResult && (
                <div style={{ marginTop: '0.5rem', fontSize: '0.7rem', color: testResult.includes('passed') ? '#10b981' : '#ef4444' }}>
                    {testResult}
                </div>
            )}
        </div>
    );
}

