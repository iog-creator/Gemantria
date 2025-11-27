import React, { useEffect } from "react";
import ChatInterface from "./ChatInterface";
import TileGrid from "./TileGrid";
import MainPage from "./MainPage";
import { useTileState } from "./useTileState";
import { getTilesByPosition, getTileById } from "./tileRegistry";
import { tileAdapters } from "./tileAdapters";
import "./orchestrator-shell.css";

export default function OrchestratorShell() {
    const {
        expandedTileId,
        expandedTile,
        expandTile,
        collapseTile,
        updateTileData,
        getTileData,
    } = useTileState();

    // Fetch data for all tiles on mount and set up auto-refresh
    useEffect(() => {
        const fetchAllTileData = async () => {
            const tiles = ["db", "lm", "system", "inference", "docs", "graph", "temporal", "forecast", "mcp", "autopilot"];

            for (const tileId of tiles) {
                const adapter = tileAdapters[tileId];
                if (adapter) {
                    try {
                        const result = await adapter();
                        updateTileData(tileId, {
                            data: result.data,
                            status: result.status,
                            reason: result.reason,
                            lastUpdated: result.lastUpdated,
                        });
                    } catch (error) {
                        console.warn(`Failed to fetch data for tile ${tileId}:`, error);
                        updateTileData(tileId, {
                            data: null,
                            status: "unknown",
                            reason: "Failed to load data",
                        });
                    }
                }
            }
        };

        fetchAllTileData();
        const interval = setInterval(fetchAllTileData, 60000); // Refresh every 60s
        return () => clearInterval(interval);
    }, [updateTileData]);

    const leftTiles = getTilesByPosition("left");
    const rightTiles = getTilesByPosition("right");
    const bottomTiles = getTilesByPosition("bottom");

    const handleTileClick = (tileId: string) => {
        expandTile(tileId);
    };

    const handleChatTileCommand = (tileId: string) => {
        expandTile(tileId);
    };

    // Get data for expanded tile
    const expandedTileData = expandedTile ? getTileData(expandedTile.id) : null;

    // Build tile data map for TileGrid
    const tileDataMap = new Map();
    ["db", "lm", "system", "inference", "docs", "graph", "temporal", "forecast", "mcp", "autopilot"].forEach((tileId) => {
        const data = getTileData(tileId);
        if (data) {
            tileDataMap.set(tileId, data);
        }
    });

    return (
        <div className="orchestrator-shell">
            <ChatInterface onTileCommand={handleChatTileCommand} />
            <div className="dashboard-body">
                <TileGrid
                    position="left"
                    tiles={leftTiles}
                    onTileClick={handleTileClick}
                    expandedTileId={expandedTileId}
                    tileDataMap={tileDataMap}
                />
                <MainPage
                    expandedTile={expandedTile}
                    onCollapse={collapseTile}
                    tileData={expandedTileData?.data || null}
                    tileStatus={expandedTileData?.status || "unknown"}
                    tileReason={expandedTileData?.reason}
                />
                <TileGrid
                    position="right"
                    tiles={rightTiles}
                    onTileClick={handleTileClick}
                    expandedTileId={expandedTileId}
                    tileDataMap={tileDataMap}
                />
            </div>
            {bottomTiles.length > 0 && (
                <div className="dashboard-bottom">
                    <TileGrid
                        position="bottom"
                        tiles={bottomTiles}
                        onTileClick={handleTileClick}
                        expandedTileId={expandedTileId}
                        tileDataMap={tileDataMap}
                    />
                </div>
            )}
        </div>
    );
}
