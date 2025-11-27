import React from "react";
import { useNavigate, useLocation, Outlet } from "react-router-dom";
import LeftRail from "../../../orchestrator-shell/LeftRail";
import Header from "../../../orchestrator-shell/Header";

export default function ShellLayout() {
    const navigate = useNavigate();
    const location = useLocation();

    // Map routes to tool IDs
    const getActiveTool = () => {
        const path = location.pathname;
        if (path === "/graph") return "graph";
        if (path === "/docs") return "docs";
        if (path === "/temporal") return "temporal";
        if (path === "/forecast") return "forecast";
        if (path === "/bible") return "biblescholar";
        if (path === "/search") return "inputs"; // Assuming keyword search maps to inputs or similar? Or maybe "search" isn't in LeftRail yet?
        // LeftRail has: overview, docs, graph, temporal, forecast, models, db, biblescholar, ollama, inputs, insights, compliance, autopilot
        if (path === "/vector-search") return "inputs"; // Mapping vector search to inputs for now
        if (path === "/lexicon") return "biblescholar"; // Related to bible?
        if (path === "/insights") return "biblescholar"; // Contextual Insights (Phase 8A)
        if (path === "/cross-language") return "biblescholar"; // Cross-Language Search (Phase 8B)
        if (path === "/dashboard") return "overview"; // System Dashboard
        if (path === "/lm-insights") return "insights";
        if (path === "/db-insights") return "db";
        if (path === "/") return "overview";
        return "overview";
    };

    const handleSelectTool = (toolId: string) => {
        switch (toolId) {
            case "graph": navigate("/graph"); break;
            case "docs": navigate("/docs"); break;
            case "temporal": navigate("/temporal"); break;
            case "forecast": navigate("/forecast"); break;
            case "biblescholar": navigate("/insights"); break; // Primary BibleScholar feature (Contextual Insights)
            case "inputs": navigate("/search"); break; // Defaulting inputs to search
            case "insights": navigate("/lm-insights"); break;
            case "overview": navigate("/dashboard"); break;
            case "db": navigate("/db-insights"); break; // DB health insights page
            case "models": navigate("/lm-insights"); break; // Models details in LM insights
            case "ollama": navigate("/lm-insights"); break;
            case "autopilot": navigate("/shell"); break; // Autopilot might be the shell chat or similar
            default: navigate("/dashboard"); break;
        }
    };

    return (
        <div className="flex h-screen flex-col bg-[#0a0b0f] text-white overflow-hidden font-sans selection:bg-blue-500/30">
            <Header />
            <div className="flex flex-1 overflow-hidden">
                <LeftRail activeTool={getActiveTool()} onSelectTool={handleSelectTool} />
                <main className="flex-1 overflow-auto bg-gray-50 text-black relative">
                    <Outlet />
                </main>
            </div>
        </div>
    );
}
