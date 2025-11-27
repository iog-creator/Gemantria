import React from "react";
import DocControlPanel from "../dashboard/src/components/DocControlPanel";
import GraphDashboard from "../graph/src/pages/GraphDashboard";
import OrchestratorOverview from "./OrchestratorOverview";
import TemporalExplorer from "../dashboard/src/components/TemporalExplorer";
import ForecastDashboard from "../dashboard/ForecastDashboard";
import ModelsPanel from "./ModelsPanel";
import DbPanel from "./DbPanel";
import BibleScholarPanel from "./BibleScholarPanel";
import OllamaMonitorPanel from "./OllamaMonitorPanel";
import InsightsPanel from "./InsightsPanel";
import CompliancePanel from "./CompliancePanel";
import AutopilotPanel from "./AutopilotPanel";

interface MainCanvasProps {
    activeTool: string;
}

export default function MainCanvas({ activeTool }: MainCanvasProps) {
    return (
        <div className="main-canvas">
            {activeTool === "overview" && <OrchestratorOverview />}
            {activeTool === "docs" && <DocControlPanel />}
            {activeTool === "models" && <ModelsPanel />}
            {activeTool === "db" && <DbPanel />}
            {activeTool === "biblescholar" && <BibleScholarPanel />}
            {activeTool === "ollama" && <OllamaMonitorPanel />}
            {activeTool === "graph" && <GraphDashboard embedded={true} />}
            {activeTool === "temporal" && <TemporalExplorer />}
            {activeTool === "forecast" && <ForecastDashboard />}
            {activeTool === "insights" && <InsightsPanel />}
            {activeTool === "compliance" && <CompliancePanel />}
            {activeTool === "autopilot" && <AutopilotPanel />}
            {!["overview", "docs", "models", "db", "biblescholar", "ollama", "graph", "temporal", "forecast", "insights", "compliance", "autopilot"].includes(activeTool) && (
                <div className="p-8">
                    <p>Orchestrator Shell — {activeTool} (placeholder)</p>
                </div>
            )}
        </div>
    );
}
