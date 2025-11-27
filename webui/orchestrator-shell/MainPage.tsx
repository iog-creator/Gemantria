import React, { useEffect, useRef } from "react";
import { TileConfig, TileExpandedProps } from "./tileRegistry";
import OrchestratorOverview from "./OrchestratorOverview";

interface MainPageProps {
    expandedTile: TileConfig | null;
    onCollapse: () => void;
    tileData: any;
    tileStatus: "healthy" | "degraded" | "offline" | "unknown";
    tileReason?: string;
}

export default function MainPage({
    expandedTile,
    onCollapse,
    tileData,
    tileStatus,
    tileReason,
}: MainPageProps) {
    const mainContentRef = useRef<HTMLDivElement>(null);

    // Focus management: when tile expands, focus the main content area
    useEffect(() => {
        if (expandedTile && mainContentRef.current) {
            mainContentRef.current.focus();
        }
    }, [expandedTile]);

    if (!expandedTile) {
        return <OrchestratorOverview />;
    }

    const ExpandedComponent = expandedTile.expandedComponent;
    const expandedProps: TileExpandedProps = {
        data: tileData,
        status: tileStatus,
        reason: tileReason,
        onCollapse,
    };

    return (
        <div
            className="main-page"
            style={{ flex: 1, display: 'flex', flexDirection: 'column', background: 'white', borderRadius: '0.5rem', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.3)', overflow: 'hidden', minHeight: '400px' }}
            role="region"
            aria-label={`${expandedTile.title} expanded view`}
            tabIndex={-1}
            ref={mainContentRef}
        >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '1rem', borderBottom: '1px solid #e5e7eb', background: '#f9fafb' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    {expandedTile.icon && <span style={{ fontSize: '1.5rem' }} aria-hidden="true">{expandedTile.icon}</span>}
                    <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#111827', margin: 0 }}>{expandedTile.title}</h2>
                </div>
                <button
                    onClick={onCollapse}
                    style={{ padding: '0.5rem 1rem', background: '#f3f4f6', color: '#374151', border: 'none', borderRadius: '0.5rem', fontWeight: 500, cursor: 'pointer', transition: 'background-color 0.2s' }}
                    aria-label={`Collapse ${expandedTile.title} tile`}
                >
                    ← Back to Tile
                </button>
            </div>
            <div style={{ flex: 1, overflowY: 'auto', padding: '1.5rem' }}>
                <ExpandedComponent {...expandedProps} />
            </div>
        </div>
    );
}

