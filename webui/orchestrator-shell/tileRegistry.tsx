import React from "react";
import { TileStatus } from "./Tile";
import DBTile from "./tiles/DBTile";
import LMTile from "./tiles/LMTile";
import SystemTile from "./tiles/SystemTile";
import InferenceTile from "./tiles/InferenceTile";
import DocsTile from "./tiles/DocsTile";
import GraphTile from "./tiles/GraphTile";
import MCPTile from "./tiles/MCPTile";
import DefaultTile from "./tiles/DefaultTile";
import DbPanel from "./DbPanel";
import ModelsPanel from "./ModelsPanel";
import DocControlPanel from "../dashboard/src/components/DocControlPanel";
import GraphDashboard from "../graph/src/pages/GraphDashboard";
import InferencePanel from "./InferencePanel";
import MCPPanel from "./MCPPanel";
import TemporalPanel from "./TemporalPanel";
import ForecastPanel from "./ForecastPanel";

export interface TileConfig {
    id: string;
    title: string;
    dataSource: string | (() => Promise<any>);
    summaryComponent: React.ComponentType<TileSummaryProps>;
    expandedComponent: React.ComponentType<TileExpandedProps>;
    position: "left" | "right" | "bottom";
    order: number;
    icon?: string;
}

export interface TileSummaryProps {
    data: any;
    status: TileStatus;
    reason?: string;
    onExpand?: () => void;
}

export interface TileExpandedProps {
    data: any;
    status: TileStatus;
    reason?: string;
    onCollapse?: () => void;
}

// Expanded view components that wrap existing panels
const DBExpanded: React.FC<TileExpandedProps> = () => <DbPanel />;
const LMExpanded: React.FC<TileExpandedProps> = () => <ModelsPanel />;
const DocsExpanded: React.FC<TileExpandedProps> = () => <DocControlPanel />;
const GraphExpanded: React.FC<TileExpandedProps> = () => <GraphDashboard embedded={true} />;

const DefaultExpanded: React.FC<TileExpandedProps> = ({ data }) => (
    <div>
        <h2 className="text-xl font-bold mb-4">Expanded View</h2>
        <pre className="text-xs bg-gray-100 p-4 rounded overflow-auto">
            {JSON.stringify(data, null, 2)}
        </pre>
    </div>
);

// Tile registry - populated with actual tile configurations
export const tileRegistry: TileConfig[] = [
    {
        id: "db",
        title: "DB",
        dataSource: "/api/status/system",
        summaryComponent: DBTile,
        expandedComponent: DBExpanded,
        position: "left",
        order: 1,
        icon: "🗄️",
    },
    {
        id: "lm",
        title: "LM",
        dataSource: "/api/status/system",
        summaryComponent: LMTile,
        expandedComponent: LMExpanded,
        position: "left",
        order: 2,
        icon: "🧠",
    },
    {
        id: "system",
        title: "System",
        dataSource: "/api/status/system",
        summaryComponent: SystemTile,
        expandedComponent: DefaultExpanded,
        position: "left",
        order: 3,
        icon: "⚙️",
    },
    {
        id: "inference",
        title: "Inference",
        dataSource: "/api/inference/models",
        summaryComponent: InferenceTile,
        expandedComponent: InferencePanel,
        position: "left",
        order: 4,
        icon: "🔮",
    },
    {
        id: "docs",
        title: "Docs",
        dataSource: "/exports/docs-control/summary.json",
        summaryComponent: DocsTile,
        expandedComponent: DocsExpanded,
        position: "left",
        order: 5,
        icon: "📄",
    },
    {
        id: "graph",
        title: "Graph",
        dataSource: "/exports/graph_stats.json",
        summaryComponent: GraphTile,
        expandedComponent: GraphExpanded,
        position: "right",
        order: 1,
        icon: "📊",
    },
    {
        id: "temporal",
        title: "Temporal",
        dataSource: "/exports/temporal_patterns.json",
        summaryComponent: DefaultTile,
        expandedComponent: TemporalPanel,
        position: "right",
        order: 2,
        icon: "🕒",
    },
    {
        id: "forecast",
        title: "Forecast",
        dataSource: "/exports/pattern_forecast.json",
        summaryComponent: DefaultTile,
        expandedComponent: ForecastPanel,
        position: "right",
        order: 3,
        icon: "📈",
    },
    {
        id: "mcp",
        title: "MCP",
        dataSource: "/exports/mcp/bundle_proof.json",
        summaryComponent: MCPTile,
        expandedComponent: MCPPanel,
        position: "right",
        order: 4,
        icon: "🔗",
    },
    {
        id: "autopilot",
        title: "Autopilot",
        dataSource: "/exports/control-plane/autopilot_summary.json",
        summaryComponent: DefaultTile,
        expandedComponent: DefaultExpanded,
        position: "bottom",
        order: 1,
        icon: "🤖",
    },
];

export function getTilesByPosition(position: "left" | "right" | "bottom"): TileConfig[] {
    return tileRegistry
        .filter((tile) => tile.position === position)
        .sort((a, b) => a.order - b.order);
}

export function getTileById(id: string): TileConfig | undefined {
    return tileRegistry.find((tile) => tile.id === id);
}

