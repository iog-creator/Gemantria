import React from "react";

export interface LeftRailProps {
    activeTool: string;
    onSelectTool: (tool: string) => void;
}

export default function LeftRail({ activeTool, onSelectTool }: LeftRailProps) {
    const tools = [
        { id: "overview", label: "Overview", icon: "🏠" },
        { id: "docs", label: "Docs", icon: "📄" },
        { id: "graph", label: "Graph", icon: "📊" },
        { id: "temporal", label: "Temporal Explorer", icon: "🕒" },
        { id: "forecast", label: "Forecast Dashboard", icon: "📈" },
        { id: "models", label: "Models", icon: "🧠" },
        { id: "db", label: "DB", icon: "🗄️" },
        { id: "biblescholar", label: "BibleScholar", icon: "📖" },
        { id: "ollama", label: "Ollama Monitor", icon: "🔍" },
        { id: "inputs", label: "Inputs", icon: "📎" },
        { id: "insights", label: "Insights", icon: "💡" },
        { id: "compliance", label: "Compliance", icon: "✅" },
        { id: "autopilot", label: "Autopilot", icon: "🤖" },
    ];

    return (
        <nav className="w-64 flex-shrink-0 bg-gray-900/95 backdrop-blur-xl border-r border-white/10 flex flex-col py-4 overflow-y-auto custom-scrollbar">
            <div className="px-4 mb-6">
                <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Tools</h2>
            </div>
            <div className="flex flex-col gap-1 px-2">
                {tools.map((tool) => (
                    <button
                        key={tool.id}
                        onClick={() => onSelectTool(tool.id)}
                        className={`
                            flex items-center gap-3 px-4 py-3 w-full text-left rounded-lg transition-all duration-200 group
                            ${activeTool === tool.id
                                ? "bg-blue-600/20 text-blue-100 border border-blue-500/30 shadow-[0_0_15px_rgba(59,130,246,0.15)]"
                                : "text-gray-400 hover:bg-white/5 hover:text-gray-100 hover:translate-x-1"
                            }
                        `}
                    >
                        <span className={`text-xl transition-transform duration-200 ${activeTool === tool.id ? "scale-110" : "group-hover:scale-110"}`}>
                            {tool.icon}
                        </span>
                        <span className="font-medium text-sm tracking-wide">{tool.label}</span>
                        {activeTool === tool.id && (
                            <div className="ml-auto w-1.5 h-1.5 rounded-full bg-blue-400 shadow-[0_0_8px_currentColor]" />
                        )}
                    </button>
                ))}
            </div>
        </nav>
    );
}
