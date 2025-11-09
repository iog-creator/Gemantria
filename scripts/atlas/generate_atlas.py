#!/usr/bin/env python3
"""
Atlas generator - creates telemetry-driven Mermaid diagrams and human summaries.

PR lane: Grey scaffolds (no DSN)
Tag lane: Populated from DB (GEMATRIA_DSN)
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Any

# Add scripts directory to path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from scripts.atlas.telemetry_queries import (
    q_active_runs,
    q_errors,
    q_latency_p90,
    q_pipeline_runs,
)

# REPO is defined above in imports
ATLAS_DIR = REPO / "docs" / "atlas"
EVIDENCE_DOCS = REPO / "docs" / "evidence"
DSN = os.getenv("GEMATRIA_DSN")
ATLAS_WINDOW = os.getenv("ATLAS_WINDOW", "24h")
ATLAS_HIDE_MISSING = os.getenv("ATLAS_HIDE_MISSING", "0") == "1"

BACK_LINK_HTML = '<p style="margin:0 0 16px"><a href="/atlas/index.html">← Back to Atlas</a></p>\n'


def _hint(msg: str) -> None:
    """Emit HINT to stderr."""
    print(f"HINT: atlas: {msg}", file=sys.stderr)


def _write_file(path: Path, content: str) -> None:
    """Write file and emit hint."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    _hint(f"wrote {path.relative_to(REPO)}")


def _has_data() -> bool:
    """Check if we have database data (tag lane) or just evidence (PR lane)."""
    return DSN is not None and DSN.strip() != ""


def _generate_execution_live() -> str:
    """Generate execution_live.mmd - currently executing pipelines."""
    active_runs = q_active_runs() if _has_data() else []

    lines = ["```mermaid", "flowchart TD"]
    lines.append("  %% Execution Live - Currently Running Pipelines")

    if not active_runs:
        lines.append("  NO_RUNS[No active runs]:::grey")
        lines.append("  classDef grey fill:#f3f4f6,stroke:#6b7280,color:#111827,stroke-width:1px;")
    else:
        lines.append("  subgraph ACTIVE[Active Pipeline Runs]")
        for i, (run_id, started_at) in enumerate(active_runs[:10]):  # Limit to 10
            node_id = f"RUN{i}"
            lines.append(f'    {node_id}["{run_id[:8]}...<br/>{started_at}"]:::green')
            lines.append(f'    click {node_id} "/evidence/execution_live.html" "View run details"')
        lines.append("  end")
        lines.append("  classDef green fill:#a7f3d0,stroke:#065f46,color:#083344,stroke-width:1px;")

    lines.append("```")
    return "\n".join(lines)


def _generate_pipeline_flow_historical() -> str:
    """Generate pipeline_flow_historical.mmd - historical pipeline flow."""
    runs = q_pipeline_runs(limit=20) if _has_data() else []

    lines = ["```mermaid", "flowchart LR"]
    lines.append("  %% Pipeline Flow - Historical View")

    # Pipeline nodes (8 stages)
    nodes = [
        "collect_nouns",
        "validate_batch",
        "enrichment",
        "math_verifier",
        "confidence_validator",
        "network_aggregator",
        "schema_validator",
        "analysis_runner",
    ]

    lines.append("  subgraph PIPELINE[Pipeline Stages]")
    for i, node in enumerate(nodes):
        node_id = node.upper().replace("_", "")
        # Get latency if available
        latency_info = ""
        if _has_data():
            latencies = q_latency_p90()
            for lat_node, calls, avg_ms, p50, p90, p95, p99 in latencies:
                if lat_node == node:
                    latency_info = f"<br/>p90: {p90:.0f}ms"
                    break
        lines.append(f'    {node_id}["{node}{latency_info}"]:::blue')
        lines.append(f'    click {node_id} "/evidence/pipeline_flow_historical.html" "View {node} details"')
        if i < len(nodes) - 1:
            lines.append(f"    {node_id} --> {nodes[i + 1].upper().replace('_', '')}")
    lines.append("  end")

    if runs:
        lines.append("  subgraph RECENT[Recent Runs]")
        for i, (run_id, started_at, finished_at, duration_ms) in enumerate(runs[:5]):
            run_node = f"R{i}"
            duration_s = duration_ms / 1000.0 if duration_ms else 0
            lines.append(f'    {run_node}["{run_id[:8]}...<br/>{duration_s:.1f}s"]:::green')
        lines.append("  end")
        lines.append("  RECENT --> PIPELINE")

    lines.append("  classDef blue fill:#dbeafe,stroke:#1e40af,color:#1e3a8a,stroke-width:1px;")
    lines.append("  classDef green fill:#a7f3d0,stroke:#065f46,color:#083344,stroke-width:1px;")
    lines.append("```")
    return "\n".join(lines)


def _generate_kpis() -> str:
    """Generate kpis.mmd - key performance indicators."""
    active_runs = q_active_runs() if _has_data() else []
    errors = q_errors() if _has_data() else []
    latencies = q_latency_p90() if _has_data() else []

    lines = ["```mermaid", "flowchart TD"]
    lines.append("  %% KPIs - Key Performance Indicators")

    lines.append("  subgraph KPIS[Key Metrics]")
    lines.append(f'    ACTIVE["Active Runs: {len(active_runs)}"]:::green')
    lines.append(f'    ERRORS["Errors (24h): {len(errors)}"]:::{"red" if errors else "green"}')

    if latencies:
        top_slow = latencies[0]
        node_name, _, _, _, p90, _, _ = top_slow
        lines.append(f'    SLOWEST["Slowest p90: {node_name}<br/>{p90:.0f}ms"]:::yellow')
    else:
        lines.append('    SLOWEST["Slowest p90: N/A"]:::grey')

    lines.append("  end")

    lines.append('  click ACTIVE "/evidence/kpis.html" "View active runs"')
    lines.append('  click ERRORS "/evidence/kpis.html" "View errors"')
    lines.append('  click SLOWEST "/evidence/kpis.html" "View latency details"')

    lines.append("  classDef green fill:#a7f3d0,stroke:#065f46,color:#083344,stroke-width:1px;")
    lines.append("  classDef red fill:#fecaca,stroke:#7f1d1d,color:#111827,stroke-width:1px;")
    lines.append("  classDef yellow fill:#fef3c7,stroke:#92400e,color:#78350f,stroke-width:1px;")
    lines.append("  classDef grey fill:#f3f4f6,stroke:#6b7280,color:#111827,stroke-width:1px;")
    lines.append("```")
    return "\n".join(lines)


def _generate_dependencies() -> str:
    """Generate dependencies.mmd - module/package dependencies."""
    lines = ["```mermaid", "graph TD"]
    lines.append("  %% Dependencies - Module Structure")

    lines.append("  subgraph SOURCE[Source Code]")
    lines.append('    SRC["src/"]:::blue')
    lines.append('    SCRIPTS["scripts/"]:::blue')
    lines.append('    TESTS["tests/"]:::blue')
    lines.append("  end")

    lines.append("  subgraph MODULES[Core Modules]")
    lines.append('    GRAPH["graph/"]:::green')
    lines.append('    NODES["nodes/"]:::green')
    lines.append('    INFRA["infra/"]:::green')
    lines.append('    SERVICES["services/"]:::green')
    lines.append("  end")

    lines.append("  SRC --> GRAPH")
    lines.append("  SRC --> NODES")
    lines.append("  SRC --> INFRA")
    lines.append("  SRC --> SERVICES")
    lines.append("  SCRIPTS --> SRC")

    lines.append('  click GRAPH "/evidence/dependencies.html" "View graph module"')
    lines.append('  click NODES "/evidence/dependencies.html" "View nodes module"')

    lines.append("  classDef blue fill:#dbeafe,stroke:#1e40af,color:#1e3a8a,stroke-width:1px;")
    lines.append("  classDef green fill:#a7f3d0,stroke:#065f46,color:#083344,stroke-width:1px;")
    lines.append("```")
    return "\n".join(lines)


def _generate_call_graph() -> str:
    """Generate call_graph.mmd - function/method call relationships."""
    lines = ["```mermaid", "graph LR"]
    lines.append("  %% Call Graph - Execution Flow")

    # Show LangGraph node sequence
    lines.append("  subgraph PIPELINE[LangGraph Pipeline]")
    nodes = [
        "collect_nouns",
        "validate_batch",
        "enrichment",
        "math_verifier",
        "confidence_validator",
        "network_aggregator",
        "schema_validator",
        "analysis_runner",
    ]
    for i, node in enumerate(nodes):
        node_id = node.upper().replace("_", "")
        lines.append(f'    {node_id}["{node}()"]:::blue')
        if i < len(nodes) - 1:
            lines.append(f"    {node_id} --> {nodes[i + 1].upper().replace('_', '')}")
    lines.append("  end")

    lines.append('  click collect_nouns "/evidence/call_graph.html" "View call details"')

    lines.append("  classDef blue fill:#dbeafe,stroke:#1e40af,color:#1e3a8a,stroke-width:1px;")
    lines.append("```")
    return "\n".join(lines)


def _generate_class_diagram() -> str:
    """Generate class_diagram.mmd - UML class relationships."""
    lines = ["```mermaid", "classDiagram"]
    lines.append("  %% Class Diagram - Data Structures")

    lines.append("  class PipelineState {")
    lines.append("    +run_id: UUID")
    lines.append("    +nouns: List[Noun]")
    lines.append("    +enriched_nouns: List[EnrichedNoun]")
    lines.append("    +graph: Graph")
    lines.append("  }")

    lines.append("  class Noun {")
    lines.append("    +noun_id: UUID")
    lines.append("    +surface: str")
    lines.append("    +gematria: int")
    lines.append("  }")

    lines.append("  class EnrichedNoun {")
    lines.append("    +noun_id: UUID")
    lines.append("    +analysis: Dict")
    lines.append("  }")

    lines.append("  PipelineState --> Noun")
    lines.append("  PipelineState --> EnrichedNoun")

    lines.append('  click PipelineState "/evidence/class_diagram.html" "View class details"')
    lines.append("```")
    return "\n".join(lines)


def _generate_knowledge_graph() -> str:
    """Generate knowledge_graph.mmd - semantic relationships."""
    lines = ["```mermaid", "graph LR"]
    lines.append("  %% Knowledge Graph - Semantic Relationships")

    lines.append("  subgraph CONCEPTS[Concepts]")
    lines.append('    C1["Concept A"]:::green')
    lines.append('    C2["Concept B"]:::green')
    lines.append('    C3["Concept C"]:::green')
    lines.append("  end")

    lines.append("  C1 -->|semantic| C2")
    lines.append("  C2 -->|cooccur| C3")
    lines.append("  C1 -->|theology| C3")

    lines.append('  click C1 "/evidence/knowledge_graph.html" "View concept details"')

    lines.append("  classDef green fill:#a7f3d0,stroke:#065f46,color:#083344,stroke-width:1px;")
    lines.append("```")
    return "\n".join(lines)


def _generate_summary_md(diagram_name: str, title: str, description: str, data: dict[str, Any] | None = None) -> str:
    """Generate human-readable Markdown summary."""
    lines = [f"# {title}"]
    lines.append("")
    lines.append("[← Back to Atlas](/atlas/index.html)")
    lines.append("")
    lines.append(f"**What this shows:** {description}")
    lines.append("")

    if _has_data():
        lines.append("**Status:** LIVE (populated from database)")
    else:
        lines.append("**Status:** SCAFFOLD (PR lane - no database)")

    lines.append("")

    if data:
        lines.append("**Data excerpt:**")
        lines.append("")
        lines.append("```json")
        # Truncate large data
        data_str = json.dumps(data, indent=2, default=str)
        if len(data_str) > 500:
            data_str = data_str[:500] + "\n  ... (truncated)"
        lines.append(data_str)
        lines.append("```")
        lines.append("")

    lines.append(
        "_Definitions:_ **PR** = proposal to merge change (fast checks) · **Tag** = frozen proof snapshot · **Badge** = visual pass/fail marker · **Verdict** = JSON pass/fail."
    )
    return "\n".join(lines)


def _generate_summary_html(md_content: str) -> str:
    """Convert Markdown summary to HTML."""
    # Simple HTML wrapper (can be enhanced with markdown library later)
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Atlas Summary</title>
    <style>
        body {{ font-family: system-ui, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; }}
        h1 {{ color: #2c3e50; }}
        code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }}
        pre {{ background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }}
    </style>
</head>
<body>
{BACK_LINK_HTML}{md_content.replace(chr(10), "<br>").replace("```json", "<pre><code>").replace("```", "</code></pre>")}
</body>
</html>"""
    return html


def main() -> int:
    """Generate all Atlas diagrams and summaries."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate Atlas diagrams and summaries")
    parser.add_argument(
        "--diagram",
        help="Generate specific diagram only",
        choices=[
            "execution_live",
            "pipeline_flow_historical",
            "kpis",
            "dependencies",
            "call_graph",
            "class_diagram",
            "knowledge_graph",
        ],
    )
    args = parser.parse_args()

    start_time = time.time()

    # Ensure directories exist
    ATLAS_DIR.mkdir(parents=True, exist_ok=True)
    EVIDENCE_DOCS.mkdir(parents=True, exist_ok=True)

    # Generate diagrams
    diagrams = {
        "execution_live": ("Execution Live", "Currently executing pipeline runs", _generate_execution_live),
        "pipeline_flow_historical": (
            "Pipeline Flow Historical",
            "Historical pipeline execution flow",
            _generate_pipeline_flow_historical,
        ),
        "kpis": ("KPIs", "Key performance indicators", _generate_kpis),
        "dependencies": ("Dependencies", "Module and package dependencies", _generate_dependencies),
        "call_graph": ("Call Graph", "Function and method call relationships", _generate_call_graph),
        "class_diagram": ("Class Diagram", "UML class relationships", _generate_class_diagram),
        "knowledge_graph": ("Knowledge Graph", "Semantic concept relationships", _generate_knowledge_graph),
    }

    # Filter to specific diagram if requested
    if args.diagram:
        diagrams = {args.diagram: diagrams[args.diagram]}

    for name, (title, desc, generator) in diagrams.items():
        # Generate Mermaid diagram
        mmd_content = generator()
        _write_file(ATLAS_DIR / f"{name}.mmd", mmd_content)

        # Generate summaries
        data = None
        if name == "execution_live" and _has_data():
            data = {"active_runs": len(q_active_runs())}
        elif name == "kpis" and _has_data():
            data = {
                "active_runs": len(q_active_runs()),
                "errors_24h": len(q_errors()),
                "top_slowest": [{"node": n[0], "p90_ms": n[4]} for n in q_latency_p90()[:5]],
            }

        md_content = _generate_summary_md(name, title, desc, data)
        _write_file(EVIDENCE_DOCS / f"{name}.md", md_content)

        html_content = _generate_summary_html(md_content)
        _write_file(EVIDENCE_DOCS / f"{name}.html", html_content)

    elapsed_ms = (time.time() - start_time) * 1000
    _hint(f"generation completed in {elapsed_ms:.0f}ms")

    if elapsed_ms > 5000:
        _hint(f"WARNING: generation took {elapsed_ms:.0f}ms (>5s threshold)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
