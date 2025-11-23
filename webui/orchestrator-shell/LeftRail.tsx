interface LeftRailProps {
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
        { id: "inputs", label: "Inputs", icon: "📎" },
        { id: "insights", label: "Insights", icon: "💡" },
        { id: "compliance", label: "Compliance", icon: "✅" },
        { id: "autopilot", label: "Autopilot", icon: "🤖" },
    ];

    return (
        <nav className="left-rail">
            {tools.map((tool) => (
                <button
                    key={tool.id}
                    aria-label={tool.label}
                    className={activeTool === tool.id ? "active" : ""}
                    onClick={() => onSelectTool(tool.id)}
                    title={tool.label}
                >
                    {tool.icon}
                </button>
            ))}
        </nav>
    );
}
