import React from "react";
import { TileSummaryProps } from "../tileRegistry";

export default function GraphTile({ data, status, reason }: TileSummaryProps) {
    const nodes = data?.nodes || {};
    const edges = data?.edges || {};
    const nodeCount = nodes.total || 0;
    const edgeCount = edges.total || 0;

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
            </div>
            {nodeCount > 0 && (
                <div style={{ fontSize: '0.75rem', color: '#4b5563' }}>
                    <p style={{ margin: '0.25rem 0' }}>Nodes: {nodeCount}</p>
                    <p style={{ margin: '0.25rem 0' }}>Edges: {edgeCount}</p>
                </div>
            )}
        </div>
    );
}

