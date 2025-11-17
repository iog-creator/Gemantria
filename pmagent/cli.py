#!/usr/bin/env python3
"""
PM Agent CLI - Health Commands

Phase-3B Feature #4: CLI interface for health checks.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import typer

# Add project root to path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Import health check functions (E402: imports after sys.path modification)
from scripts.guards.guard_db_health import check_db_health  # noqa: E402
from scripts.guards.guard_lm_health import check_lm_health  # noqa: E402
from scripts.graph.graph_overview import compute_graph_overview  # noqa: E402
from scripts.system.system_health import compute_system_health, print_human_summary  # noqa: E402
from scripts.db_import_graph_stats import import_graph_stats  # noqa: E402
from scripts.control.control_status import (  # noqa: E402
    compute_control_status,
    print_human_summary as print_control_summary,
)
from scripts.control.control_tables import (  # noqa: E402
    compute_control_tables,
    print_human_summary as print_tables_summary,
)
from scripts.control.control_schema import (  # noqa: E402
    compute_control_schema,
    print_human_summary as print_schema_summary,
)
from scripts.control.control_pipeline_status import (  # noqa: E402
    compute_control_pipeline_status,
    print_human_summary as print_pipeline_summary,
)
from scripts.control.control_summary import (  # noqa: E402
    compute_control_summary,
    print_human_summary as print_summary_summary,
)
from agentpm.knowledge.qa_docs import answer_doc_question  # noqa: E402
from agentpm.lm.lm_status import compute_lm_status, print_lm_status_table  # noqa: E402
from agentpm.status.explain import explain_system_status  # noqa: E402
from agentpm.docs.search import search_docs  # noqa: E402

app = typer.Typer(add_completion=False, no_args_is_help=True)
health_app = typer.Typer(help="Health check commands")
app.add_typer(health_app, name="health")
graph_app = typer.Typer(help="Graph operations")
app.add_typer(graph_app, name="graph")
control_app = typer.Typer(help="Control-plane operations")
app.add_typer(control_app, name="control")
ask_app = typer.Typer(help="Ask questions using SSOT documentation")
app.add_typer(ask_app, name="ask")
reality_app = typer.Typer(help="Reality checks for automated bring-up")
app.add_typer(reality_app, name="reality-check")
bringup_app = typer.Typer(help="System bring-up commands")
app.add_typer(bringup_app, name="bringup")
mcp_app = typer.Typer(help="MCP server commands")
app.add_typer(mcp_app, name="mcp")
lm_app = typer.Typer(help="LM (Language Model) operations")
app.add_typer(lm_app, name="lm")
status_app = typer.Typer(help="System status helpers")
app.add_typer(status_app, name="status")
docs_app = typer.Typer(help="Documentation search operations")
app.add_typer(docs_app, name="docs")


def _print_health_output(health_json: dict, summary_func=None) -> None:
    """Print health JSON to stdout and optional summary to stderr."""
    print(json.dumps(health_json, indent=2))
    if summary_func:
        summary = summary_func(health_json)
        print(summary, file=sys.stderr)


@health_app.command("system", help="Aggregate system health (DB + LM + Graph)")
def health_system(
    json_only: bool = typer.Option(False, "--json-only", help="Print only JSON"),
) -> None:
    """Check system health (aggregates DB, LM, and Graph health)."""
    health = compute_system_health()
    if json_only:
        print(json.dumps(health, indent=2))
    else:
        _print_health_output(health, print_human_summary)
    sys.exit(0)


@health_app.command("db", help="Check database health")
def health_db(json_only: bool = typer.Option(False, "--json-only", help="Print only JSON")) -> None:
    """Check database health posture."""
    health = check_db_health()

    if json_only:
        print(json.dumps(health, indent=2))
    else:
        # Print JSON to stdout
        print(json.dumps(health, indent=2))
        # Print human-readable summary to stderr
        mode = health.get("mode", "unknown")
        errors = health.get("details", {}).get("errors", [])
        if health.get("ok") and mode == "ready":
            reason = "ok"
        elif errors:
            reason = errors[0].split(":")[-1].strip()[:50]
        else:
            reason = mode
        print(f"DB_HEALTH: mode={mode} ({reason})", file=sys.stderr)
    sys.exit(0)


@health_app.command("lm", help="Check LM Studio health")
def health_lm(json_only: bool = typer.Option(False, "--json-only", help="Print only JSON")) -> None:
    """Check LM Studio health."""
    health = check_lm_health()

    if json_only:
        print(json.dumps(health, indent=2))
    else:
        # Print JSON to stdout
        print(json.dumps(health, indent=2))
        # Print human-readable summary to stderr
        mode = health.get("mode", "unknown")
        errors = health.get("details", {}).get("errors", [])
        if health.get("ok") and mode == "lm_ready":
            reason = "ok"
        elif errors:
            reason = errors[0].split(":")[-1].strip()[:50]
        else:
            reason = "endpoint not reachable"
        print(f"LM_HEALTH: mode={mode} ({reason})", file=sys.stderr)
    sys.exit(0)


@lm_app.command("status", help="Show LM configuration and local service health")
def lm_status(
    json_only: bool = typer.Option(False, "--json-only", help="Print only JSON"),
) -> None:
    """Show LM status for all slots (local_agent, embedding, reranker, theology)."""
    status = compute_lm_status()

    if json_only:
        print(json.dumps(status, indent=2))
    else:
        # Print JSON to stdout
        print(json.dumps(status, indent=2))
        # Print human-readable table to stderr
        table = print_lm_status_table(status)
        print(table, file=sys.stderr)
    sys.exit(0)


@status_app.command("explain", help="Explain current DB + LM health in plain language")
def status_explain(
    json_only: bool = typer.Option(False, "--json-only", help="Return JSON instead of text"),
    no_lm: bool = typer.Option(False, "--no-lm", help="Skip LM enhancement, use rule-based only"),
) -> None:
    """Explain current system status in plain language."""
    explanation = explain_system_status(use_lm=not no_lm)

    if json_only:
        print(json.dumps(explanation, indent=2))
    else:
        # Pretty text output
        level = explanation.get("level", "UNKNOWN")
        headline = explanation.get("headline", "Unknown status")
        details = explanation.get("details", "")

        # Print to stdout
        level_tag = f"[{level}]"
        print(f"{level_tag} {headline}")
        print(details)

        # If ERROR level, also print to stderr
        if level == "ERROR":
            print(f"{level_tag} {headline}", file=sys.stderr)
            print(details, file=sys.stderr)

    sys.exit(0)


@health_app.command("graph", help="Check graph overview")
def health_graph(
    json_only: bool = typer.Option(False, "--json-only", help="Print only JSON"),
) -> None:
    """Check graph overview statistics."""
    overview = compute_graph_overview()

    if json_only:
        print(json.dumps(overview, indent=2))
    else:
        # Print JSON to stdout
        print(json.dumps(overview, indent=2))
        # Print human-readable summary to stderr
        mode = overview.get("mode", "unknown")
        reason = overview.get("reason", "ok")
        if not reason or reason == "ok":
            reason = "ok" if overview.get("ok") else mode
        print(f"GRAPH_OVERVIEW: mode={mode} ({reason[:50]})", file=sys.stderr)
    sys.exit(0)


@graph_app.command("overview", help="Display graph overview statistics")
def graph_overview(
    json_only: bool = typer.Option(False, "--json-only", help="Print only JSON"),
) -> None:
    """Display graph overview statistics from database."""
    overview = compute_graph_overview()

    if json_only:
        print(json.dumps(overview, indent=2))
    else:
        # Print JSON to stdout
        print(json.dumps(overview, indent=2))
        # Print human-readable summary to stderr
        mode = overview.get("mode", "unknown")
        reason = overview.get("reason", "ok")
        if not reason or reason == "ok":
            reason = "ok" if overview.get("ok") else mode
        print(f"GRAPH_OVERVIEW: mode={mode} ({reason[:50]})", file=sys.stderr)
    sys.exit(0)


# Default input path for graph import
_DEFAULT_GRAPH_STATS_PATH = Path("exports/graph_stats.json")


@graph_app.command("import", help="Import graph_stats.json into database")
def graph_import(
    input_path: str = typer.Option(
        str(_DEFAULT_GRAPH_STATS_PATH),
        "--input",
        help="Path to graph_stats.json file",
    ),
) -> None:
    """Import graph_stats.json into Postgres database."""
    path = Path(input_path) if input_path else _DEFAULT_GRAPH_STATS_PATH
    result = import_graph_stats(path)

    # Print JSON to stdout
    print(json.dumps(result, indent=2, default=str))

    # Print human-readable summary to stderr
    if result.get("ok"):
        inserted = result.get("inserted", 0)
        snapshot_id = result.get("snapshot_id", "unknown")
        print(
            f"GRAPH_IMPORT: snapshots_imported=1 rows_inserted={inserted} snapshot_id={snapshot_id}",
            file=sys.stderr,
        )
        sys.exit(0)
    else:
        errors = result.get("errors", [])
        error_msg = errors[0] if errors else "unknown error"
        print(f"GRAPH_IMPORT: failed ({error_msg[:50]})", file=sys.stderr)
        sys.exit(1)


@control_app.command("status", help="Check control-plane database status and table row counts")
def control_status(
    json_only: bool = typer.Option(False, "--json-only", help="Print only JSON"),
) -> None:
    """Check control-plane database status and table row counts."""
    status = compute_control_status()

    if json_only:
        print(json.dumps(status, indent=2))
    else:
        # Print JSON to stdout
        print(json.dumps(status, indent=2))
        # Print human-readable summary to stderr
        summary = print_control_summary(status)
        print(summary, file=sys.stderr)
    sys.exit(0)


@control_app.command("tables", help="List all schema-qualified tables with row counts")
def control_tables(
    json_only: bool = typer.Option(False, "--json-only", help="Print only JSON"),
) -> None:
    """List all schema-qualified tables with row counts."""
    tables = compute_control_tables()

    if json_only:
        print(json.dumps(tables, indent=2))
    else:
        # Print JSON to stdout
        print(json.dumps(tables, indent=2))
        # Print human-readable summary to stderr
        summary = print_tables_summary(tables)
        print(summary, file=sys.stderr)
    sys.exit(0)


@control_app.command("schema", help="Introspect control-plane table schemas (DDL)")
def control_schema(
    json_only: bool = typer.Option(False, "--json-only", help="Print only JSON"),
) -> None:
    """Introspect control-plane table schemas (DDL)."""
    schema = compute_control_schema()

    if json_only:
        print(json.dumps(schema, indent=2))
    else:
        # Print JSON to stdout
        print(json.dumps(schema, indent=2))
        # Print human-readable summary to stderr
        summary = print_schema_summary(schema)
        print(summary, file=sys.stderr)
    sys.exit(0)


@control_app.command("pipeline-status", help="Summarize recent pipeline runs from control.agent_run")
def control_pipeline_status(
    window_hours: int = typer.Option(24, "--window-hours", help="Time window in hours (default: 24)"),
    json_only: bool = typer.Option(False, "--json-only", help="Print only JSON"),
) -> None:
    """Summarize recent pipeline runs from control.agent_run table."""
    status = compute_control_pipeline_status(window_hours=window_hours)

    if json_only:
        print(json.dumps(status, indent=2))
    else:
        # Print JSON to stdout
        print(json.dumps(status, indent=2))
        # Print human-readable summary to stderr
        summary = print_pipeline_summary(status)
        print(summary, file=sys.stderr)
    sys.exit(0)


@control_app.command("summary", help="Aggregated control-plane summary (status/tables/schema/pipeline-status)")
def control_summary(
    json_only: bool = typer.Option(False, "--json-only", help="Print only JSON"),
) -> None:
    """Aggregated control-plane summary combining all control components."""
    summary = compute_control_summary()

    if json_only:
        print(json.dumps(summary, indent=2))
    else:
        # Print JSON to stdout
        print(json.dumps(summary, indent=2))
        # Print human-readable summary to stderr
        summary_line = print_summary_summary(summary)
        print(summary_line, file=sys.stderr)
    sys.exit(0)


@ask_app.command("docs", help="Answer a question using SSOT documentation")
def ask_docs(
    question: str = typer.Argument(..., help="Question to ask"),
    json_only: bool = typer.Option(False, "--json-only", help="Print only JSON"),
) -> None:
    """Answer a question using SSOT documentation via LM Studio."""
    result = answer_doc_question(question)

    if json_only:
        print(json.dumps(result, indent=2))
    else:
        # Print JSON to stdout
        print(json.dumps(result, indent=2))
        # Print human-readable summary to stderr
        if result.get("ok"):
            answer = result.get("answer", "")
            mode = result.get("mode", "unknown")
            sources_count = len(result.get("sources", []))
            print(f"ANSWER ({mode}): {answer[:200]}...", file=sys.stderr)
            print(f"SOURCES: {sources_count} section(s)", file=sys.stderr)
        else:
            mode = result.get("mode", "unknown")
            print(f"ERROR: Failed to generate answer (mode: {mode})", file=sys.stderr)
    sys.exit(0)


@reality_app.command("1", help="Run Reality Check #1 automated bring-up")
def reality_check_one() -> None:
    """Run Reality Check #1 automated bring-up (Postgres + LM Studio + ingestion + Q&A)."""
    import subprocess

    proc = subprocess.run(
        [sys.executable, "-m", "agentpm.scripts.reality_check_1"],
        capture_output=True,
        text=True,
    )
    print(proc.stdout, end="")
    if proc.stderr:
        print(proc.stderr, file=sys.stderr, end="")
    raise typer.Exit(code=proc.returncode)


@reality_app.command("live", help="Run Reality Check #1 LIVE (DB + LM + pipeline)")
def reality_check_live() -> None:
    """Run the full live Reality Check #1 and exit non-zero on failure."""
    import subprocess
    import sys

    proc = subprocess.run(
        [sys.executable, "-m", "agentpm.scripts.reality_check_1_live"],
        text=True,
    )
    # The script itself prints JSON and returns appropriate exit code.
    raise typer.Exit(code=proc.returncode)


@bringup_app.command("full", help="Fully start DB, LM Studio server+GUI, and load models")
def bringup_full() -> None:
    """Run the full system bring-up (DB + LM Studio + models + MCP SSE if enabled)."""
    import subprocess
    import sys

    proc = subprocess.run(
        [sys.executable, "-m", "agentpm.scripts.system_bringup"],
        text=True,
    )
    # The script itself prints JSON and returns appropriate exit code.
    raise typer.Exit(code=proc.returncode)


@mcp_app.command("sse", help="Ensure MCP SSE server is running (auto-start if AUTO_START_MCP_SSE=1)")
def mcp_sse_ensure() -> None:
    """Ensure MCP SSE server is running on port 8005 (for LM Studio bridge)."""
    import subprocess
    import sys
    from pathlib import Path

    script_path = Path("scripts/mcp_sse_ensure.sh")
    if not script_path.exists():
        print(f"ERROR: MCP SSE ensure script not found at {script_path}", file=sys.stderr)
        raise typer.Exit(code=1)

    proc = subprocess.run(
        ["bash", str(script_path)],
        text=True,
    )
    raise typer.Exit(code=proc.returncode)


@docs_app.command("search", help="Search governance/docs content via semantic similarity")
def docs_search(
    query: str = typer.Argument(..., help="Search query text"),
    k: int = typer.Option(10, "--k", help="Number of results to return"),
    json_only: bool = typer.Option(False, "--json-only", help="Print only JSON"),
    tier0_only: bool = typer.Option(
        True, "--tier0-only/--all", help="Search only Tier-0 docs (AGENTS_ROOT + AGENTS::*)"
    ),
) -> None:
    """Search governance/docs content via semantic similarity over control-plane embeddings."""
    result = search_docs(query=query, k=k, tier0_only=tier0_only)

    if json_only:
        print(json.dumps(result, indent=2))
    else:
        # Print JSON to stdout
        print(json.dumps(result, indent=2))
        # Print human-readable summary to stderr
        if result.get("ok"):
            results = result.get("results", [])
            print(
                f"DOCS_SEARCH: found {len(results)} result(s) for '{query[:50]}...'",
                file=sys.stderr,
            )
            for i, r in enumerate(results[:5], 1):  # Show top 5 in summary
                logical_name = r.get("logical_name", "unknown")
                score = r.get("score", 0.0)
                snippet = r.get("content", "")[:100]
                print(f"  {i}. [{logical_name}] (score: {score:.3f}) {snippet}...", file=sys.stderr)
        else:
            error = result.get("error", "unknown error")
            print(f"DOCS_SEARCH: failed ({error[:50]})", file=sys.stderr)

    sys.exit(0 if result.get("ok") else 1)


def main() -> None:
    """Main entry point for pmagent CLI."""
    app()


if __name__ == "__main__":
    main()
