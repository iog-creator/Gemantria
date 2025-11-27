import React from "react";
import { TileConfig, TileSummaryProps } from "./tileRegistry";
import Tile from "./Tile";
import { TileStatus } from "./Tile";

interface TileGridProps {
    position: "left" | "right" | "bottom";
    tiles: TileConfig[];
    onTileClick: (tileId: string) => void;
    expandedTileId?: string | null;
    tileDataMap?: Map<string, { data: any; status: TileStatus; reason?: string }>;
}

export default function TileGrid({ position, tiles, onTileClick, expandedTileId, tileDataMap }: TileGridProps) {
    if (tiles.length === 0) {
        return null;
    }

    const gridStyles: Record<string, React.CSSProperties> = {
        left: { display: 'flex', flexDirection: 'column', gap: '1rem', width: '280px' },
        right: { display: 'flex', flexDirection: 'column', gap: '1rem', width: '280px' },
        bottom: { display: 'flex', flexDirection: 'row', gap: '1rem', flexWrap: 'wrap' },
    };

    return (
        <div style={gridStyles[position]} role="region" aria-label={`${position} tile column`}>
            {tiles.map((tile) => {
                const tileData = tileDataMap?.get(tile.id);
                const SummaryComponent = tile.summaryComponent;
                const summaryProps: TileSummaryProps = {
                    data: tileData?.data || null,
                    status: tileData?.status || "unknown",
                    reason: tileData?.reason,
                    onExpand: () => onTileClick(tile.id),
                };

                return (
                    <div
                        key={tile.id}
                        style={{
                            flex: position === "bottom" ? 1 : undefined,
                            minWidth: position === "bottom" ? "200px" : undefined,
                            opacity: expandedTileId === tile.id ? 0.5 : 1,
                            transition: 'opacity 0.2s',
                        }}
                    >
                        <Tile
                            id={tile.id}
                            title={tile.title}
                            status={tileData?.status || "unknown"}
                            reason={tileData?.reason}
                            onClick={() => onTileClick(tile.id)}
                            isExpanded={expandedTileId === tile.id}
                        >
                            <SummaryComponent {...summaryProps} />
                        </Tile>
                    </div>
                );
            })}
        </div>
    );
}

