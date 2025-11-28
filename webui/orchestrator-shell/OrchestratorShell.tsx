import { useState } from "react";
import Header from "./Header";
import LeftRail from "./LeftRail";
import MainCanvas from "./MainCanvas";
import "./orchestrator-shell.css";

export default function OrchestratorShell() {
    const [activeTool, setActiveTool] = useState("overview");

    return (
        <div className="orchestrator-shell">
            <Header />
            <div className="body">
                <LeftRail activeTool={activeTool} onSelectTool={setActiveTool} />
                <MainCanvas activeTool={activeTool} />
            </div>
        </div>
    );
}
