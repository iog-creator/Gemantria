import React, { useEffect, useState } from "react";
import { LeftNav } from "./components/LeftNav";
import { ConversationPane } from "./components/ConversationPane";
import { RightStatusPane } from "./components/RightStatusPane";
import {
    loadConsoleSchema,
    loadViewModel,
    type ConsoleSchema,
    type ViewModel,
    type ModeId
} from "./model/consoleConfig";
import type { TileDataBundle } from "./data/types";
import { loadTileData } from "./data/tileLoaders";
import type { ConversationContextData } from "./data/conversationContext";
import { loadConversationContext } from "./data/conversationContext";

/**
 * Orchestrator Console v2 root component.
 * - Three regions: left_nav, conversation, right_status
 * - Modes come from VIEW_MODEL bindings (left_nav.modes)
 * - Right-status tiles are backed by real data via TileDataBundle.
 * - Conversation pane shows high-level context via ConversationContextData.
 */

export const App: React.FC = () => {
    const [schema, setSchema] = useState<ConsoleSchema | null>(null);
    const [viewModel, setViewModel] = useState<ViewModel | null>(null);
    const [tileData, setTileData] = useState<TileDataBundle | null>(null);
    const [conversationData, setConversationData] =
        useState<ConversationContextData | null>(null);
    const [activeMode, setActiveMode] = useState<ModeId>("overview");

    useEffect(() => {
        // Best-effort load; failure leaves the skeleton visible.
        void (async () => {
            try {
                const [s, v] = await Promise.all([
                    loadConsoleSchema(),
                    loadViewModel()
                ]);
                setSchema(s);
                setViewModel(v);

                const [tiles, context] = await Promise.all([
                    loadTileData(v),
                    loadConversationContext(v)
                ]);
                setTileData(tiles);
                setConversationData(context);
            } catch (err) {
                // eslint-disable-next-line no-console
                console.warn("Failed to load console models or data:", err);
            }
        })();
    }, []);

    const modes: ModeId[] =
        (viewModel?.bindings.left_nav.modes as ModeId[]) || [
            "overview",
            "docs",
            "temporal",
            "forecast",
            "graph"
        ];

    return (
        <div className="console-root">
            <LeftNav modes={modes} activeMode={activeMode} onModeChange={setActiveMode} />
            <ConversationPane conversationData={conversationData} />
            <RightStatusPane tileData={tileData} />
        </div>
    );
};
