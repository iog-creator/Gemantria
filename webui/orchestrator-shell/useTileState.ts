import { useState, useEffect, useCallback } from "react";
import { TileConfig, getTileById } from "./tileRegistry";
import { TileStatus } from "./Tile";

interface TileData {
    data: any;
    status: TileStatus;
    reason?: string;
    lastUpdated?: string;
}

export function useTileState() {
    const [expandedTileId, setExpandedTileId] = useState<string | null>(null);
    const [tileDataMap, setTileDataMap] = useState<Map<string, TileData>>(new Map());

    const expandTile = useCallback((tileId: string) => {
        const tile = getTileById(tileId);
        if (!tile) return;

        // If clicking the same tile, collapse it
        if (expandedTileId === tileId) {
            setExpandedTileId(null);
        } else {
            setExpandedTileId(tileId);
        }
    }, [expandedTileId]);

    const collapseTile = useCallback(() => {
        setExpandedTileId(null);
    }, []);

    const updateTileData = useCallback((tileId: string, data: TileData) => {
        setTileDataMap((prev) => {
            const next = new Map(prev);
            next.set(tileId, data);
            return next;
        });
    }, []);

    const getExpandedTile = useCallback((): TileConfig | null => {
        if (!expandedTileId) return null;
        return getTileById(expandedTileId) || null;
    }, [expandedTileId]);

    const getTileData = useCallback((tileId: string): TileData | null => {
        return tileDataMap.get(tileId) || null;
    }, [tileDataMap]);

    return {
        expandedTileId,
        expandedTile: getExpandedTile(),
        expandTile,
        collapseTile,
        updateTileData,
        getTileData,
    };
}

