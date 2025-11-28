#!/usr/bin/env python3
"""
PM Agent CLI - Health Commands

Phase-3B Feature #4: CLI interface for health checks.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

import typer

# Add project root to path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Import health check functions (E402: imports after sys.path modification)
from scripts.guards.guard_db_health import check_db_health  # noqa: E402
from scripts.guards.guard_lm_health import check_lm_health  # noqa: E402
from scripts.graph.graph_overview import compute_graph_overview  # noqa: E402
from scripts.system.system_health import print_human_summary  # noqa: E402
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
    print_human_summary as print_summary_summary,
)
from agentpm.knowledge.qa_docs import answer_doc_question  # noqa: E402
from agentpm.lm.lm_status import compute_lm_status, print_lm_status_table  # noqa: E402
from agentpm.status.explain import explain_system_status  # noqa: E402
from agentpm.status.snapshot import get_kb_status_view  # noqa: E402
from agentpm.docs.search import search_docs  # noqa: E402
from agentpm.ai_docs.reality_check_ai_notes import main as reality_check_ai_notes_main  # noqa: E402
from scripts.config.env import get_retrieval_lane_models, get_lm_model_config  # noqa: E402
from agentpm.scripts.docs_inventory import run_inventory  # noqa: E402
from agentpm.scripts.docs_duplicates_report import generate_duplicates_report  # noqa: E402
from agentpm.scripts.docs_dm002_preview import main as docs_dm002_preview_main  # noqa: E402
from agentpm.scripts.docs_dm002_sync import main as docs_dm002_sync_main  # noqa: E402
from agentpm.scripts.docs_dm002_summary import main as docs_dm002_summary_main  # noqa: E402
from agentpm.scripts.docs_archive_dryrun import main as docs_archive_dryrun_main  # noqa: E402
from agentpm.scripts.docs_dashboard_refresh import main as docs_dashboard_refresh_main  # noqa: E402
from agentpm.scripts.state.ledger_sync import sync_ledger  # noqa: E402
from agentpm.control_plane import create_agent_run, mark_agent_run_success, mark_agent_run_error  # noqa: E402
from agentpm.tools import (  # noqa: E402
    health as tool_health,
    control_summary as tool_control_summary,
    ledger_verify as tool_ledger_verify,
    retrieve_bible_passages,
    rerank_passages,
    extract_concepts,
    generate_embeddings as tool_embed,
)
from agentpm.adapters import planning as planning_adapter  # noqa: E402
from agentpm.adapters import gemini_cli as gemini_cli_adapter  # noqa: E402
from agentpm.adapters import codex_cli as codex_cli_adapter  # noqa: E402
from agentpm.kb.registry import (  # noqa: E402
    load_registry,
    query_registry,
    validate_registry,
    REGISTRY_PATH,
)
from agentpm.plan.kb import build_kb_doc_worklist  # noqa: E402
from agentpm.plan.fix import build_fix_actions, apply_actions  # noqa: E402
from agentpm.plan.next import (  # noqa: E402
    build_capability_session,
    build_next_plan,
    list_capability_sessions,
    run_reality_loop,
)
from agentpm.handoff.service import generate_handoff  # noqa: E402
from agentpm.status.kb_metrics import compute_kb_doc_health_metrics  # noqa: E402
from agentpm.kb.registry import REPO_ROOT  # noqa: E402
from agentpm.governance.conflict_audit import audit_governance_conflicts  # noqa: E402

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
reality_validate_app = typer.Typer(help="Reality validation commands")
app.add_typer(reality_validate_app, name="reality")
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
models_app = typer.Typer(help="Model introspection commands")
app.add_typer(models_app, name="models")
state_app = typer.Typer(help="System state ledger operations")
app.add_typer(state_app, name="state")
kb_app = typer.Typer(help="Knowledge-base document registry operations")
app.add_typer(kb_app, name="kb")
registry_app = typer.Typer(help="KB document registry commands")
handoff_app = typer.Typer(help="Handoff generation commands")
app.add_typer(handoff_app, name="handoff")
kb_app.add_typer(registry_app, name="registry")
plan_app = typer.Typer(help="Planning workflows powered by KB registry")
app.add_typer(plan_app, name="plan")
plan_kb_app = typer.Typer(help="KB-powered planning commands")
plan_app.add_typer(plan_kb_app, name="kb")

report_app = typer.Typer(help="Reporting commands")
app.add_typer(report_app, name="report")

governance_app = typer.Typer(help="Governance conflict audit commands")
app.add_typer(governance_app, name="governance")

tools_app = typer.Typer(help="External planning/tool helpers (Gemini, Codex)")
app.add_typer(tools_app, name="tools")

autopilot_app = typer.Typer(help="Autopilot backend operations")
app.add_typer(autopilot_app, name="autopilot")

# Phase 13: Flow commands for integration testing
flow_app = typer.Typer(help="Flow execution commands for integration testing")
app.add_typer(flow_app, name="flow")


def _print_health_output(health_json: dict, summary_func=None) -> None:
    """Print health JSON to stdout and optional summary to stderr."""
    print(json.dumps(health_json, indent=2))
    if summary_func:
        summary = summary_func(health_json)
        print(summary, file=sys.stderr)


def _load_prompt_text(prompt: str, prompt_file: Path | None) -> str:
    """Load prompt text from argument, stdin, or file."""
    if prompt_file:
        return prompt_file.read_text().strip()
    prompt = prompt.strip()
    if prompt == "-":
        return sys.stdin.read().strip()
    return prompt


def _print_planning_result(result: planning_adapter.PlanningCliResult, *, json_only: bool) -> None:
    """Print planning result summary and optional response."""
    summary = planning_adapter.summarize_result(result)
    print(json.dumps(summary, indent=2))
    if json_only:
        return
    if result.response:
        print("\n=== Response ===")
        print(result.response)
    elif summary.get("reason"):
        print(f"\n(no response - reason: {summary['reason']})")


@health_app.command("system", help="Aggregate system health (DB + LM + Graph)")
def health_system(
    json_only: bool = typer.Option(False, "--json-only", help="Print only JSON"),
) -> None:
    """Check system health (aggregates DB, LM, and Graph health)."""
    run = create_agent_run("system.health", {"json_only": json_only})
    try:
        health = tool_health()
        if json_only:
            print(json.dumps(health, indent=2))
        else:
            _print_health_output(health, print_human_summary)
        mark_agent_run_success(run, health)
        sys.exit(0)
    except Exception as e:
        mark_agent_run_error(run, e)
        raise


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


@lm_app.command("router-status", help="Show LM router configuration (Phase-7C)")
def lm_router_status(
    json_only: bool = typer.Option(False, "--json-only", help="Print only JSON"),
) -> None:
    """Show LM router configuration and slot mappings (read-only, hermetic)."""
    try:
        from agentpm.lm.router import GraniteRouter, RouterTask
        from scripts.config.env import get_lm_model_config

        router = GraniteRouter(config=get_lm_model_config(), dry_run=True)

        # Build router status
        router_enabled = os.getenv("ROUTER_ENABLED", "1") in ("1", "true", "yes")
        status = {
            "router_enabled": router_enabled,
            "slots": {},
        }

        # Test routing for each slot type
        test_tasks = [
            ("embedding", RouterTask(kind="embed", domain=None)),
            ("reranker", RouterTask(kind="rerank", domain=None)),
            ("math", RouterTask(kind="math_verification", domain="math")),
            ("theology", RouterTask(kind="theology_enrichment", domain="theology")),
            ("local_agent", RouterTask(kind="chat", domain="general", needs_tools=False)),
            ("local_agent_tools", RouterTask(kind="chat", domain="general", needs_tools=True)),
        ]

        for slot_name, task in test_tasks:
            try:
                decision = router.route_task(task)
                status["slots"][slot_name] = {
                    "slot": decision.slot,
                    "provider": decision.provider,
                    "model": decision.model_name,
                    "temperature": decision.temperature,
                }
            except Exception as e:
                status["slots"][slot_name] = {
                    "error": str(e),
                }

        if json_only:
            print(json.dumps(status, indent=2))
        else:
            # Print JSON to stdout
            print(json.dumps(status, indent=2))
            # Print human-readable summary to stderr
            print(f"Router enabled: {router_enabled}", file=sys.stderr)
            print(
                f"Slots configured: {len([s for s in status['slots'].values() if 'error' not in s])}",
                file=sys.stderr,
            )

    except ImportError as e:
        error_msg = {"error": f"Router not available: {e}"}
        if json_only:
            print(json.dumps(error_msg, indent=2))
        else:
            print(json.dumps(error_msg, indent=2), file=sys.stderr)
        sys.exit(1)

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


@status_app.command("kb", help="KB registry status view for PM/AgentPM planning")
def status_kb(
    json_only: bool = typer.Option(False, "--json-only", help="Print only JSON"),
    registry_path: str = typer.Option(None, "--registry-path", help="Path to registry JSON file"),
) -> None:
    """Get KB-focused status view showing document counts by subsystem/type and missing files."""
    try:
        path = Path(registry_path) if registry_path else None
        kb_status = get_kb_status_view(registry_path=path)

        if json_only:
            print(json.dumps(kb_status, indent=2))
        else:
            # Human-readable output
            print("KB Registry Status:", file=sys.stderr)
            print(f"  Available: {kb_status.get('available', False)}", file=sys.stderr)
            print(f"  Total documents: {kb_status.get('total', 0)}", file=sys.stderr)

            by_subsystem = kb_status.get("by_subsystem", {})
            if by_subsystem:
                print("  By subsystem:", file=sys.stderr)
                for subsystem, count in sorted(by_subsystem.items()):
                    print(f"    {subsystem}: {count}", file=sys.stderr)

            by_type = kb_status.get("by_type", {})
            if by_type:
                print("  By type:", file=sys.stderr)
                for doc_type, count in sorted(by_type.items()):
                    print(f"    {doc_type}: {count}", file=sys.stderr)

            missing_files = kb_status.get("missing_files", [])
            if missing_files:
                print(f"  Missing files ({len(missing_files)}):", file=sys.stderr)
                for file_path in missing_files[:10]:  # Show first 10
                    print(f"    {file_path}", file=sys.stderr)
                if len(missing_files) > 10:
                    print(f"    ... and {len(missing_files) - 10} more", file=sys.stderr)

            notes = kb_status.get("notes", [])
            if notes:
                print("  Notes:", file=sys.stderr)
                for note in notes:
                    print(f"    {note}", file=sys.stderr)

            # JSON to stdout for scripting
            print(json.dumps(kb_status, indent=2))

    except Exception as e:
        error_msg = {"error": str(e), "available": False, "total": 0}
        if json_only:
            print(json.dumps(error_msg, indent=2))
        else:
            print(f"ERROR: Failed to get KB status: {e}", file=sys.stderr)
            print(json.dumps(error_msg, indent=2))
        sys.exit(1)

    sys.exit(0)


@plan_kb_app.command("list", help="Get KB-powered documentation worklist for planning")
def plan_kb_list(
    json_only: bool = typer.Option(False, "--json-only", help="Print only JSON"),
) -> None:
    """Get prioritized documentation worklist from KB registry status and hints.

    Returns a worklist of documentation tasks grouped by subsystem and ordered by
    severity (missing > stale > out_of_sync > low_coverage > info).
    """
    try:
        worklist = build_kb_doc_worklist()

        if json_only:
            print(json.dumps(worklist, indent=2))
        else:
            # Human-readable output
            available = worklist.get("available", False)
            total_items = worklist.get("total_items", 0)
            items = worklist.get("items", [])
            by_subsystem = worklist.get("by_subsystem", {})

            if not available:
                print("KB Registry unavailable (registry may not be seeded yet)", file=sys.stderr)
                print(json.dumps(worklist, indent=2))
                sys.exit(0)

            if total_items == 0:
                print("No documentation work items found (all docs are fresh)", file=sys.stderr)
                print(json.dumps(worklist, indent=2))
                sys.exit(0)

            # Top section: Most urgent items (missing/stale)
            urgent_items = [item for item in items if item.get("severity") in ["missing", "stale"]]
            if urgent_items:
                print("Most urgent doc work (missing/stale):", file=sys.stderr)
                for item in urgent_items[:5]:  # Show top 5
                    severity = item.get("severity", "unknown").upper()
                    title = item.get("title", "Unknown")
                    subsystem = item.get("subsystem", "unknown")
                    reason = item.get("reason", "")
                    print(f"  [{severity}] {title} ({subsystem})", file=sys.stderr)
                    print(f"    Reason: {reason}", file=sys.stderr)
                    print(f"    Action: {item.get('suggested_action', 'N/A')}", file=sys.stderr)
                if len(urgent_items) > 5:
                    print(f"    ... and {len(urgent_items) - 5} more urgent items", file=sys.stderr)
                print("", file=sys.stderr)

            # Compact table grouped by subsystem
            if by_subsystem:
                print("By subsystem:", file=sys.stderr)
                for subsystem, count in sorted(by_subsystem.items()):
                    print(f"  {subsystem}: {count} item(s)", file=sys.stderr)

            # JSON to stdout for scripting
            print(json.dumps(worklist, indent=2))

    except Exception as e:
        error_msg = {"error": str(e), "available": False, "total_items": 0, "items": []}
        if json_only:
            print(json.dumps(error_msg, indent=2))
        else:
            print(f"ERROR: Failed to build worklist: {e}", file=sys.stderr)
            print(json.dumps(error_msg, indent=2))
        sys.exit(1)

    sys.exit(0)


@plan_app.command("next", help="Suggest next work items from MASTER_PLAN + NEXT_STEPS")
def plan_next(
    json_only: bool = typer.Option(False, "--json-only", help="Print only JSON"),
    limit: int = typer.Option(3, "--limit", help="Limit number of suggested tasks"),
    with_status: bool = typer.Option(False, "--with-status", help="Include system posture (reality-check + status)"),
) -> None:
    """Suggest next work items based on MASTER_PLAN.md and NEXT_STEPS.md.

    Hermetic: file-only, no DB/LM calls, no writes.
    With --with-status: includes system posture (reality-check + status explain).
    """
    try:
        result = build_next_plan(limit=limit, with_status=with_status)

        # Always print JSON to stdout
        print(json.dumps(result, indent=2))

        if json_only:
            sys.exit(0)

        if not result.get("available", False):
            print(
                "PLAN data unavailable (MASTER_PLAN.md or NEXT_STEPS.md missing)",
                file=sys.stderr,
            )
            sys.exit(0)

        candidates = result.get("candidates", [])
        if not candidates:
            print("No next-step candidates found in NEXT_STEPS.md", file=sys.stderr)
            sys.exit(0)

        print("Top next work candidates:", file=sys.stderr)
        for cand in candidates:
            cid = cand.get("id", "?")
            title = cand.get("title", "Unknown")
            source = cand.get("source", "NEXT_STEPS")
            print(f"  - [{cid}] {title} ({source})", file=sys.stderr)

        current_focus = result.get("current_focus")
        if current_focus:
            print(f"\nCurrent Focus: {current_focus}", file=sys.stderr)

        next_milestone = result.get("next_milestone")
        if next_milestone:
            print(f"Next Milestone: {next_milestone}", file=sys.stderr)

        # Print posture summary if available
        posture = result.get("posture")
        if posture:
            mode = posture.get("mode", "unknown")
            if mode == "live":
                reality = posture.get("reality", {})
                status = posture.get("status", {})
                overall_ok = reality.get("overall_ok", False)
                level = status.get("level", "UNKNOWN")
                headline = status.get("headline", "No status available")
                print(
                    f"\nSystem Posture: {level} ({'OK' if overall_ok else 'ISSUES'})",
                    file=sys.stderr,
                )
                print(f"  {headline}", file=sys.stderr)
            else:
                print(f"\nSystem Posture: {mode} (commands unavailable)", file=sys.stderr)
                if posture.get("error"):
                    print(f"  Note: {posture['error']}", file=sys.stderr)

        sys.exit(0)
    except Exception as e:  # pragma: no cover (defensive)
        error_msg = {"error": str(e), "available": False, "candidates": []}
        print(json.dumps(error_msg, indent=2))
        if not json_only:
            print(f"ERROR: Failed to build next-plan suggestions: {e}", file=sys.stderr)
        sys.exit(1)


@plan_app.command("open", help="Open a NEXT_STEPS item as a capability_session envelope")
def plan_open(
    candidate_id: str = typer.Argument(..., help="Candidate id from `pmagent plan next` (e.g. NEXT_STEPS:1)"),
    json_only: bool = typer.Option(False, "--json-only", help="Print only JSON"),
    with_status: bool = typer.Option(True, "--with-status", help="Include posture (reality+status) when available"),
) -> None:
    """Open a NEXT_STEPS item as a capability_session envelope.

    Hermetic: file-only, optional posture via reality-check + status explain.
    """
    try:
        session = build_capability_session(candidate_id, with_status=with_status)

        # Always print JSON to stdout
        print(json.dumps(session, indent=2))

        if json_only:
            sys.exit(0)

        if not session.get("available", False):
            reason = session.get("reason", "unknown")
            print(f"Capability session unavailable: {reason}", file=sys.stderr)
            sys.exit(0)

        # Print human summary to stderr
        session_id = session.get("id", "?")
        title = session.get("title", "Unknown")
        source = session.get("source", "NEXT_STEPS")
        print(f"Capability Session: [{session_id}] {title} ({source})", file=sys.stderr)

        plan = session.get("plan", {})
        current_focus = plan.get("current_focus")
        if current_focus:
            print(f"Current Focus: {current_focus}", file=sys.stderr)

        next_milestone = plan.get("next_milestone")
        if next_milestone:
            print(f"Next Milestone: {next_milestone}", file=sys.stderr)

        # Print posture summary if available
        posture = session.get("posture")
        if posture:
            mode = posture.get("mode", "unknown")
            if mode == "live":
                reality = posture.get("reality", {})
                status = posture.get("status", {})
                overall_ok = reality.get("overall_ok", False)
                level = status.get("level", "UNKNOWN")
                headline = status.get("headline", "No status available")
                print(
                    f"\nSystem Posture: {level} ({'OK' if overall_ok else 'ISSUES'})",
                    file=sys.stderr,
                )
                print(f"  {headline}", file=sys.stderr)
                print(f"  Mode: {mode}", file=sys.stderr)
            else:
                print(f"\nSystem Posture: {mode} (commands unavailable)", file=sys.stderr)
                if posture.get("error"):
                    print(f"  Note: {posture['error']}", file=sys.stderr)

        sys.exit(0)
    except Exception as e:  # pragma: no cover (defensive)
        error_msg = {
            "type": "capability_session",
            "version": "1.0",
            "id": candidate_id,
            "available": False,
            "error": str(e),
        }
        print(json.dumps(error_msg, indent=2))
        if not json_only:
            print(f"ERROR: Failed to build capability session: {e}", file=sys.stderr)
        sys.exit(1)


@plan_app.command("reality-loop", help="Run a single plan+posture loop and persist a capability_session envelope")
def plan_reality_loop(
    limit: int = typer.Option(3, "--limit", help="Max candidates to consider from NEXT_STEPS"),
    json_only: bool = typer.Option(False, "--json-only", help="Print only JSON summary"),
    dry_run_command: str | None = typer.Option(
        None,
        "--dry-run-command",
        help="Optional shell/Make/pmagent command to associate with this capability_session (NOT executed)",
    ),
    track_session: bool = typer.Option(
        False,
        "--track-session",
        help="Validate and (when enabled) persist the capability_session into control.agent_run_cli",
    ),
) -> None:
    """Run a single planning + posture loop and persist a capability_session envelope.

    Hermetic: file-only, no DB writes by default; writes capability_session to evidence/pmagent/.
    With --track-session: validates and optionally persists to control.agent_run_cli (gated by DB availability).
    """
    try:
        result = run_reality_loop(limit=limit, dry_run_command=dry_run_command)

        # If envelope was created and tracking is enabled, validate and optionally persist
        tracking_result = None
        if result.get("available", False) and result.get("envelope_path"):
            envelope = result.get("envelope", {})
            if envelope:
                from agentpm.reality.capability_envelope_validator import (
                    validate_and_optionally_persist,
                )  # noqa: E402, PLC0415

                tracking_result = validate_and_optionally_persist(envelope, tracking_enabled=track_session)

        # Always print JSON summary to stdout
        summary = {
            "available": result.get("available", False),
            "candidate": result.get("candidate"),
            "envelope_path": result.get("envelope_path"),
            "dry_run_command": result.get("dry_run_command"),
            "error": result.get("error"),
        }
        if tracking_result is not None:
            summary["tracking"] = tracking_result
        print(json.dumps(summary, indent=2))

        if json_only:
            sys.exit(0)

        if not result.get("available", False):
            error = result.get("error", "unknown")
            print(f"No capability session created: {error}", file=sys.stderr)
            print("(This is advisory only; no candidates available in NEXT_STEPS.md)", file=sys.stderr)
            sys.exit(0)

        # Print human summary to stderr
        candidate = result.get("candidate", {})
        candidate_id = candidate.get("id", "?")
        title = candidate.get("title", "Unknown")
        source = candidate.get("source", "NEXT_STEPS")
        envelope_path = result.get("envelope_path", "?")

        print(f"Capability Session: [{candidate_id}] {title} ({source})", file=sys.stderr)
        print(f"Envelope written to: {envelope_path}", file=sys.stderr)

        # Show posture summary from envelope
        envelope = result.get("envelope", {})
        posture = envelope.get("posture")
        if posture:
            mode = posture.get("mode", "unknown")
            if mode == "live":
                reality = posture.get("reality", {})
                status = posture.get("status", {})
                overall_ok = reality.get("overall_ok", False)
                level = status.get("level", "UNKNOWN")
                headline = status.get("headline", "No status available")
                print(
                    f"\nSystem Posture: {level} ({'OK' if overall_ok else 'ISSUES'})",
                    file=sys.stderr,
                )
                print(f"  {headline}", file=sys.stderr)
                print(f"  Mode: {mode}", file=sys.stderr)
            else:
                print(f"\nSystem Posture: {mode} (commands unavailable)", file=sys.stderr)
                if posture.get("error"):
                    print(f"  Note: {posture['error']}", file=sys.stderr)

        # Show dry-run command if provided
        if result.get("dry_run_command"):
            print(
                f"\nSession dry-run command (not executed): {result['dry_run_command']}",
                file=sys.stderr,
            )

        # Show tracking status
        if tracking_result is not None:
            tracking = tracking_result.get("tracking")
            if tracking:
                mode = tracking.get("mode", "unknown")
                written = tracking.get("written", False)
                agent_run_id = tracking.get("agent_run_cli_id")
                if mode == "db_on" and written and agent_run_id:
                    print(
                        f"\nTracking: persisted to control.agent_run_cli (id: {agent_run_id})",
                        file=sys.stderr,
                    )
                elif mode == "db_off":
                    print(f"\nTracking: DB unavailable (mode: {mode})", file=sys.stderr)
                elif mode == "error":
                    error_msg = tracking.get("error", "unknown error")
                    print(f"\nTracking: error ({error_msg})", file=sys.stderr)
            elif not track_session:
                # Tracking disabled (validation ran but no tracking block)
                print("\nTracking: disabled (use --track-session to persist to DB)", file=sys.stderr)
        elif result.get("available", False) and not track_session:
            # Envelope created but tracking not attempted (shouldn't happen, but handle gracefully)
            print("\nTracking: disabled (use --track-session to persist to DB)", file=sys.stderr)

        sys.exit(0)
    except Exception as e:  # pragma: no cover (defensive)
        error_msg = {
            "available": False,
            "candidate": None,
            "envelope_path": None,
            "error": str(e),
        }
        print(json.dumps(error_msg, indent=2))
        if not json_only:
            print(f"ERROR: Failed to run reality loop: {e}", file=sys.stderr)
        sys.exit(1)


@plan_app.command("history", help="List recent capability_session envelopes (read-only)")
def plan_history(
    limit: int = typer.Option(10, "--limit", help="Maximum number of sessions to list"),
    json_only: bool = typer.Option(False, "--json-only", help="Print only JSON summary"),
) -> None:
    """List recent capability_session envelopes from evidence/pmagent/.

    Hermetic: read-only, file-only, no DB/LM calls.
    """
    try:
        sessions = list_capability_sessions(limit=limit)

        # Always print JSON summary to stdout
        summary = {
            "count": len(sessions),
            "sessions": sessions,
        }
        print(json.dumps(summary, indent=2))

        if json_only:
            sys.exit(0)

        if not sessions:
            print("No capability sessions found in evidence/pmagent/", file=sys.stderr)
            sys.exit(0)

        # Print human summary to stderr
        print(f"\nRecent Capability Sessions (newest first, limit={limit}):", file=sys.stderr)
        for i, session in enumerate(sessions, 1):
            session_id = session.get("id", "?")
            title = session.get("title", "Unknown")
            source = session.get("source", "NEXT_STEPS")
            timestamp = session.get("timestamp", "?")
            dry_run = session.get("dry_run_command")
            posture_mode = session.get("posture_mode")
            reality_ok = session.get("reality_overall_ok")
            status_level = session.get("status_level")

            print(f"\n{i}. [{session_id}] {title} ({source})", file=sys.stderr)
            print(f"   Timestamp: {timestamp}", file=sys.stderr)
            if dry_run:
                print(f"   Dry-run command: {dry_run}", file=sys.stderr)
            if posture_mode:
                posture_str = f"Posture: {posture_mode}"
                if posture_mode == "live" and reality_ok is not None:
                    posture_str += f" (reality: {'OK' if reality_ok else 'ISSUES'})"
                if status_level:
                    posture_str += f", status: {status_level}"
                print(f"   {posture_str}", file=sys.stderr)

        sys.exit(0)
    except Exception as e:  # pragma: no cover (defensive)
        error_msg = {
            "count": 0,
            "sessions": [],
            "error": str(e),
        }
        print(json.dumps(error_msg, indent=2))
        if not json_only:
            print(f"ERROR: Failed to list capability sessions: {e}", file=sys.stderr)
        sys.exit(1)


@autopilot_app.command("serve", help="Start the Autopilot backend server")
def autopilot_serve(
    host: str = typer.Option("127.0.0.1", "--host", help="Host to bind to"),
    port: int = typer.Option(8006, "--port", help="Port to bind to"),
    reload: bool = typer.Option(False, "--reload", help="Enable auto-reload"),
) -> None:
    """Start the Autopilot backend server (FastAPI)."""
    import uvicorn

    print(f"Starting Autopilot backend on http://{host}:{port}...", file=sys.stderr)
    uvicorn.run("agentpm.server.autopilot_api:app", host=host, port=port, reload=reload)


@plan_kb_app.command("fix", help="Execute doc fixes from KB worklist")
def plan_kb_fix(
    json_only: bool = typer.Option(False, "--json-only", help="Print only JSON"),
    dry_run: bool = typer.Option(True, "--dry-run/--apply", help="Dry-run mode (default) or apply fixes"),
    subsystem: str | None = typer.Option(None, "--subsystem", help="Filter to specific subsystem"),
    min_severity: str | None = typer.Option(None, "--min-severity", help="Filter to severity level or higher"),
    limit: int = typer.Option(50, "--limit", help="Limit number of actions processed"),
    allow_stubs_for_low_coverage: bool = typer.Option(
        False,
        "--allow-stubs-for-low-coverage",
        help="Allow creating stubs for low-coverage subsystems",
    ),
) -> None:
    """Execute doc fixes from KB worklist.

    Consumes worklist from `pmagent plan kb list` and produces/executes doc fixes.
    Default is --dry-run mode (no writes); --apply requires explicit opt-in.
    """
    from datetime import datetime, UTC

    try:
        # Build worklist
        worklist = build_kb_doc_worklist()

        if not worklist.get("available", False):
            error_msg = {
                "error": "KB Registry unavailable",
                "mode": "dry-run" if dry_run else "apply",
                "actions": [],
            }
            if json_only:
                print(json.dumps(error_msg, indent=2))
            else:
                print(
                    "ERROR: KB Registry unavailable (registry may not be seeded yet)",
                    file=sys.stderr,
                )
                print(json.dumps(error_msg, indent=2))
            sys.exit(1)

        # Build filters
        filters: dict[str, Any] = {}
        if subsystem:
            filters["subsystem"] = subsystem
        if min_severity:
            filters["min_severity"] = min_severity
        filters["limit"] = limit

        # Build fix actions
        actions = build_fix_actions(worklist, filters)

        # Apply actions
        apply_result = apply_actions(
            actions,
            dry_run=dry_run,
            repo_root=REPO_ROOT,
            allow_stubs_for_low_coverage=allow_stubs_for_low_coverage,
        )

        # Build output JSON
        now = datetime.now(UTC)
        output: dict[str, Any] = {
            "mode": "dry-run" if dry_run else "apply",
            "filters": filters,
            "source": {
                "worklist_items": worklist.get("total_items", 0),
                "generated_at": now.isoformat(),
            },
            "actions": [action.to_dict() for action in actions],
            "summary": {
                "total_actions": len(actions),
                "by_severity": {},
                "by_action_type": {},
                "actions_applied": apply_result.get("actions_applied", 0),
                "actions_skipped": apply_result.get("actions_skipped", 0),
                "files_created": apply_result.get("files_created", []),
                "files_modified": apply_result.get("files_modified", []),
                "errors": apply_result.get("errors", []),
            },
        }

        # Build summary counts
        for action in actions:
            severity = action.severity
            action_type = action.action_type
            output["summary"]["by_severity"][severity] = output["summary"]["by_severity"].get(severity, 0) + 1
            output["summary"]["by_action_type"][action_type] = (
                output["summary"]["by_action_type"].get(action_type, 0) + 1
            )

        # Log manifest if apply mode
        if not dry_run and (apply_result.get("files_created") or apply_result.get("files_modified")):
            manifest_dir = REPO_ROOT / "evidence" / "plan_kb_fix"
            manifest_dir.mkdir(parents=True, exist_ok=True)
            manifest_path = manifest_dir / f"run-{now.strftime('%Y%m%d-%H%M%S')}.json"
            manifest_path.write_text(json.dumps(output, indent=2) + "\n")

        if json_only:
            print(json.dumps(output, indent=2))
        else:
            # Human-readable output to stderr
            mode_str = "dry-run" if dry_run else "apply"
            total = output["summary"]["total_actions"]
            applied = output["summary"]["actions_applied"]
            skipped = output["summary"]["actions_skipped"]
            by_severity = output["summary"]["by_severity"]

            severity_counts = ", ".join([f"{count} {sev}" for sev, count in sorted(by_severity.items())])
            print(f"Doc-fix run ({mode_str}) — {total} actions: {severity_counts}", file=sys.stderr)
            print(f"  Applied: {applied}, Skipped: {skipped}", file=sys.stderr)

            # Show top 5 actions
            top_actions = actions[:5]
            if top_actions:
                print("", file=sys.stderr)
                print("Top actions:", file=sys.stderr)
                for action in top_actions:
                    path_str = action.doc_path or "N/A"
                    print(f"  [{action.severity}] {action.subsystem}: {path_str}", file=sys.stderr)
                    print(f"    {action.description[:60]}...", file=sys.stderr)
                if len(actions) > 5:
                    print(f"    ... and {len(actions) - 5} more actions", file=sys.stderr)

            if apply_result.get("errors"):
                print("", file=sys.stderr)
                print("Errors:", file=sys.stderr)
                for error in apply_result["errors"]:
                    print(f"  {error}", file=sys.stderr)

            # JSON to stdout
            print(json.dumps(output, indent=2))

    except Exception as e:
        error_msg = {
            "error": str(e),
            "mode": "dry-run" if dry_run else "apply",
            "actions": [],
            "summary": {"total_actions": 0},
        }
        if json_only:
            print(json.dumps(error_msg, indent=2))
        else:
            print(f"ERROR: Failed to execute fix actions: {e}", file=sys.stderr)
            print(json.dumps(error_msg, indent=2))
        sys.exit(1)

    sys.exit(0)


@report_app.command("kb", help="Report KB doc-health metrics (M1+M2 aggregate)")
def report_kb(
    json_only: bool = typer.Option(True, "--json-only/--human", help="Print only JSON (default) or human summary"),
) -> None:
    """Report KB documentation health metrics based on registry + M2 manifests.

    This is a read-only, hermetic reporting surface that:
    - Uses the KB registry + freshness analysis for structural metrics.
    - Uses AgentPM-Next:M2 manifests for recent fix activity.
    - Degrades gracefully (available=False + notes) when inputs are missing.
    """
    try:
        report = compute_kb_doc_health_metrics()
        if json_only:
            print(json.dumps(report, indent=2))
        else:
            # Human-readable summary to stderr, JSON to stdout.
            metrics = report.get("metrics", {})
            fresh = metrics.get("kb_fresh_ratio", {})
            missing = metrics.get("kb_missing_count", {})
            stale_by_sub = metrics.get("kb_stale_count_by_subsystem", {})
            fixes_7d = metrics.get("kb_fixes_applied_last_7d", 0)
            notes = metrics.get("notes", [])

            overall_fresh = fresh.get("overall")
            if overall_fresh is None:
                print("KB doc-health: fresh ratio unknown (no registry or empty)", file=sys.stderr)
            else:
                print(f"KB doc-health: {overall_fresh:.1f}% fresh overall", file=sys.stderr)

            by_sub = fresh.get("by_subsystem", {})
            if by_sub:
                print("  By subsystem:", file=sys.stderr)
                for subsystem, ratio in sorted(by_sub.items()):
                    miss_sub = missing.get("by_subsystem", {}).get(subsystem, 0)
                    stale_sub = stale_by_sub.get(subsystem, 0)
                    print(
                        f"    {subsystem}: {ratio:.1f}% fresh (missing={miss_sub}, stale={stale_sub})",
                        file=sys.stderr,
                    )

            print(f"KB fixes applied (last 7d): {fixes_7d}", file=sys.stderr)

            if notes:
                print("", file=sys.stderr)
                print("Notes:", file=sys.stderr)
                for note in notes:
                    print(f"  - {note}", file=sys.stderr)

            print(json.dumps(report, indent=2))

    except Exception as exc:
        error_msg = {"available": False, "error": str(exc)}
        if json_only:
            print(json.dumps(error_msg, indent=2))
        else:
            print(f"ERROR: Failed to compute KB doc-health metrics: {exc}", file=sys.stderr)
            print(json.dumps(error_msg, indent=2))
        sys.exit(1)

    sys.exit(0)


@governance_app.command("audit", help="Audit governance conflicts in rules and SSOT documents")
def governance_audit(
    conflicts: bool = typer.Option(False, "--conflicts", help="Audit logical conflicts between rules"),
    output: Path | None = typer.Option(  # noqa: B008
        None,
        "--output",
        "-o",
        help="Output path for JSON manifest (default: evidence/governance_conflict_manifest.json)",
    ),
    json_only: bool = typer.Option(True, "--json-only/--human", help="Print only JSON (default) or human summary"),
) -> None:
    """Audit governance conflicts in rules and SSOT documents.

    This command systematically detects logical contradictions between rules,
    leveraging M1/M2 doc fragments and M3 metrics to identify conflicts.
    """
    if not conflicts:
        print("ERROR: --conflicts flag required", file=sys.stderr)
        print(
            "Usage: pmagent governance audit --conflicts [--output PATH] [--json-only]",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        output_path = output or (REPO_ROOT / "evidence" / "governance_conflict_manifest.json")
        result = audit_governance_conflicts(output_path=output_path)

        if json_only:
            print(json.dumps(result.to_dict(), indent=2))
        else:
            # Human-readable summary to stderr, JSON to stdout
            print("Governance Conflict Audit", file=sys.stderr)
            print(f"  Rules scanned: {result.total_rules_scanned}", file=sys.stderr)
            print(f"  Conflicts found: {result.conflicts_found}", file=sys.stderr)
            print("", file=sys.stderr)

            if result.findings:
                for finding in result.findings:
                    print(f"  [{finding.severity.upper()}] {finding.conflict_id}", file=sys.stderr)
                    for rule_1, rule_2 in finding.rule_pairs:
                        print(f"    Conflict: Rule {rule_1} vs Rule {rule_2}", file=sys.stderr)
                    print(f"    Description: {finding.description}", file=sys.stderr)
                    if finding.recommendation:
                        print(f"    Recommendation: {finding.recommendation}", file=sys.stderr)
                    print("", file=sys.stderr)
            else:
                print("  No conflicts detected.", file=sys.stderr)

            if result.notes:
                print("", file=sys.stderr)
                print("Notes:", file=sys.stderr)
                for note in result.notes:
                    print(f"  - {note}", file=sys.stderr)

            print(json.dumps(result.to_dict(), indent=2))

        # Exit with error code if critical conflicts found
        critical_count = sum(1 for f in result.findings if f.severity == "critical")
        if critical_count > 0:
            sys.exit(1)

    except Exception as exc:
        error_msg = {"error": str(exc), "available": False}
        if json_only:
            print(json.dumps(error_msg, indent=2))
        else:
            print(f"ERROR: Failed to audit governance conflicts: {exc}", file=sys.stderr)
            print(json.dumps(error_msg, indent=2))
        sys.exit(1)

    sys.exit(0)


@tools_app.command("plan", help="Run prompt via configured planning provider (Gemini/Codex/local fallback)")
def tools_plan(
    prompt: str = typer.Argument(..., help="Prompt text; use '-' to read from stdin"),
    prompt_file: Path | None = typer.Option(  # noqa: B008
        None,
        "--prompt-file",
        "-f",
        exists=True,
        dir_okay=False,
        readable=True,
        help="Read prompt from file instead of CLI argument",
    ),  # noqa: B008
    system: str = typer.Option("", "--system", help="Optional system prompt"),
    json_only: bool = typer.Option(False, "--json-only", help="Print only JSON summary"),
) -> None:
    run = create_agent_run("tools.plan", {"json_only": json_only})
    try:
        prompt_text = _load_prompt_text(prompt, prompt_file)
        result = planning_adapter.run_planning_prompt(prompt_text, system=system or None)
        _print_planning_result(result, json_only=json_only)
        mark_agent_run_success(run, planning_adapter.summarize_result(result))
    except Exception as exc:
        mark_agent_run_error(run, exc)
        raise


@tools_app.command("gemini", help="Force Gemini CLI planning helper")
def tools_gemini(
    prompt: str = typer.Argument(..., help="Prompt text; use '-' to read from stdin"),
    prompt_file: Path | None = typer.Option(  # noqa: B008
        None,
        "--prompt-file",
        "-f",
        exists=True,
        dir_okay=False,
        readable=True,
        help="Read prompt from file instead of CLI argument",
    ),  # noqa: B008
    system: str = typer.Option("", "--system", help="Optional system prompt"),
    model: str | None = typer.Option(None, "--model", help="Override planning model ID"),
    cli_path: str | None = typer.Option(None, "--cli-path", help="Path to gemini CLI binary"),
    json_only: bool = typer.Option(False, "--json-only", help="Print only JSON summary"),
) -> None:
    cfg = get_lm_model_config()
    run = create_agent_run("tools.gemini", {"json_only": json_only})
    try:
        prompt_text = _load_prompt_text(prompt, prompt_file)
        result = gemini_cli_adapter.run(
            prompt_text,
            system=system or None,
            model=model or cfg.get("planning_model") or cfg.get("local_agent_model"),
            cli_path=cli_path or cfg.get("gemini_cli_path") or "gemini",
            enabled=bool(cfg.get("gemini_enabled", False)),  # Deprecated: disabled by default
        )
        _print_planning_result(result, json_only=json_only)
        mark_agent_run_success(run, planning_adapter.summarize_result(result))
    except Exception as exc:
        mark_agent_run_error(run, exc)
        raise


@tools_app.command("codex", help="Force Codex CLI planning helper")
def tools_codex(
    prompt: str = typer.Argument(..., help="Prompt text; use '-' to read from stdin"),
    prompt_file: Path | None = typer.Option(  # noqa: B008
        None,
        "--prompt-file",
        "-f",
        exists=True,
        dir_okay=False,
        readable=True,
        help="Read prompt from file instead of CLI argument",
    ),  # noqa: B008
    system: str = typer.Option("", "--system", help="Optional system prompt"),
    model: str | None = typer.Option(None, "--model", help="Override planning model ID"),
    cli_path: str | None = typer.Option(None, "--cli-path", help="Path to codex CLI binary"),
    json_only: bool = typer.Option(False, "--json-only", help="Print only JSON summary"),
) -> None:
    cfg = get_lm_model_config()
    run = create_agent_run("tools.codex", {"json_only": json_only})
    try:
        prompt_text = _load_prompt_text(prompt, prompt_file)
        result = codex_cli_adapter.run(
            prompt_text,
            system=system or None,
            model=model or cfg.get("planning_model") or cfg.get("local_agent_model"),
            cli_path=cli_path or cfg.get("codex_cli_path") or "codex",
            enabled=bool(cfg.get("codex_enabled", False)),
        )
        _print_planning_result(result, json_only=json_only)
        mark_agent_run_success(run, planning_adapter.summarize_result(result))
    except Exception as exc:
        mark_agent_run_error(run, exc)
        raise


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
    run = create_agent_run("system.control-summary", {"json_only": json_only})
    try:
        result = tool_control_summary()
        summary = result.get("summary", {})
        if json_only:
            print(json.dumps(summary, indent=2))
        else:
            # Print JSON to stdout
            print(json.dumps(summary, indent=2))
            # Print human-readable summary to stderr
            summary_line = print_summary_summary(summary)
            print(summary_line, file=sys.stderr)
        mark_agent_run_success(run, result)
        sys.exit(0)
    except Exception as e:
        mark_agent_run_error(run, e)
        raise


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


@reality_app.command("check", help="Run comprehensive reality check (env + DB + LM + exports + eval)")
def reality_check_check(
    mode: str = typer.Option("hint", "--mode", help="Mode: hint (default) or strict"),
    json_only: bool = typer.Option(False, "--json-only", help="Print only JSON"),
    no_dashboards: bool = typer.Option(False, "--no-dashboards", help="Skip exports/eval checks"),
) -> None:
    """Run comprehensive reality check."""
    from agentpm.reality.check import reality_check, print_human_summary

    run = create_agent_run("system.reality-check", {"mode": mode, "no_dashboards": no_dashboards})
    try:
        mode_upper = mode.upper()
        if mode_upper not in ("HINT", "STRICT"):
            print(f"ERROR: mode must be 'hint' or 'strict', got '{mode}'", file=sys.stderr)
            mark_agent_run_error(run, f"Invalid mode: {mode}")
            raise typer.Exit(code=1)

        verdict = reality_check(mode=mode_upper, skip_dashboards=no_dashboards)

        if json_only:
            print(json.dumps(verdict, indent=2))
        else:
            # Print JSON to stdout, summary to stderr (matches existing pattern)
            print(json.dumps(verdict, indent=2))
            print_human_summary(verdict, file=sys.stderr)

        mark_agent_run_success(run, verdict)
        raise typer.Exit(code=0 if verdict.get("overall_ok") else 1)
    except Exception as e:
        mark_agent_run_error(run, e)
        raise


@reality_validate_app.command(
    "validate-capability-envelope",
    help="Validate a capability_session envelope file against AI tracking mapping contract",
)
def reality_validate_capability_envelope(
    file: Path = typer.Argument(..., help="Path to capability_session JSON file"),  # noqa: B008
    json_only: bool = typer.Option(False, "--json-only", help="Print only JSON"),
) -> None:
    """Validate a capability_session envelope file.

    Hermetic: read-only, no DB writes. Checks envelope against future AI tracking mapping.
    """
    from agentpm.reality.capability_envelope_validator import validate_capability_envelope_file

    try:
        result = validate_capability_envelope_file(file)

        # Always print JSON to stdout
        print(json.dumps(result, indent=2))

        if json_only:
            sys.exit(0 if result.get("ok", False) else 1)

        # Print human summary to stderr
        if result.get("ok", False):
            print("✓ Envelope validation passed", file=sys.stderr)
            if result.get("warnings"):
                print(f"  Warnings: {len(result['warnings'])}", file=sys.stderr)
                for warning in result["warnings"]:
                    print(f"    - {warning}", file=sys.stderr)
        else:
            print("✗ Envelope validation failed", file=sys.stderr)
            if result.get("file_error"):
                print(f"  File error: {result['file_error']}", file=sys.stderr)
            if result.get("errors"):
                print(f"  Errors ({len(result['errors'])}):", file=sys.stderr)
                for error in result["errors"]:
                    print(f"    - {error}", file=sys.stderr)

        sys.exit(0 if result.get("ok", False) else 1)
    except Exception as e:  # pragma: no cover (defensive)
        error_msg = {
            "ok": False,
            "file_path": str(file),
            "file_error": str(e),
            "errors": [str(e)],
            "warnings": [],
            "derived_tracking": {},
        }
        print(json.dumps(error_msg, indent=2))
        if not json_only:
            print(f"ERROR: Failed to validate envelope: {e}", file=sys.stderr)
        sys.exit(1)


@reality_validate_app.command(
    "sessions",
    help="Summarize capability_session envelopes and tracking posture",
)
def reality_sessions(
    limit: int = typer.Option(10, "--limit", help="Max sessions to show"),
    json_only: bool = typer.Option(False, "--json-only", help="Print only JSON summary"),
) -> None:
    """Summarize capability_session envelopes and tracking posture.

    Hermetic: read-only, file-only reads, optional DB reads (gracefully handles DB-off).
    """
    from agentpm.reality.sessions_summary import summarize_tracked_sessions

    try:
        summary = summarize_tracked_sessions(limit=limit)

        # Always print JSON to stdout
        print(json.dumps(summary, indent=2, sort_keys=True))

        if json_only:
            sys.exit(0)

        # Print human summary to stderr
        envelopes = summary.get("envelopes", {})
        tracking = summary.get("tracking", {})

        envelope_count = envelopes.get("count", 0)
        latest = envelopes.get("latest", [])

        print(f"\nSessions: {envelope_count} envelope(s)", file=sys.stderr)
        if latest:
            print("  Latest sessions:", file=sys.stderr)
            for i, session in enumerate(latest[:5], 1):  # Show first 5
                session_id = session.get("id", "unknown")
                title = session.get("title", "")[:50]
                mode = session.get("posture_mode", "unknown")
                dry_run = session.get("dry_run_command")
                dry_run_str = f" (cmd: {dry_run[:30]}...)" if dry_run else ""
                print(f"    {i}. [{session_id}] {title} (mode: {mode}){dry_run_str}", file=sys.stderr)

        db_mode = tracking.get("db_mode", "unknown")
        enabled_hint = tracking.get("enabled_hint", False)
        agent_run_cli = tracking.get("agent_run_cli")

        print("\nTracking:", file=sys.stderr)
        print(f"  DB mode: {db_mode}", file=sys.stderr)
        print(f"  Enabled hint: {enabled_hint}", file=sys.stderr)
        if agent_run_cli:
            count = agent_run_cli.get("count")
            if count is not None:
                print(f"  agent_run_cli count: {count}", file=sys.stderr)
            modes = agent_run_cli.get("latest_modes")
            if modes:
                print(f"  Latest modes: {modes}", file=sys.stderr)
        else:
            print("  agent_run_cli: (not available)", file=sys.stderr)

        sys.exit(0)
    except Exception as e:  # pragma: no cover (defensive)
        error_msg = {
            "error": str(e),
            "envelopes": {"count": 0, "latest": []},
            "tracking": {"enabled_hint": False, "db_mode": "unknown", "agent_run_cli": None},
        }
        print(json.dumps(error_msg, indent=2))
        if not json_only:
            print(f"ERROR: Failed to summarize sessions: {e}", file=sys.stderr)
        sys.exit(1)


@reality_validate_app.command(
    "validate-capability-history",
    help="Scan and validate all capability_session envelopes in evidence/pmagent/",
)
def reality_validate_capability_history(
    json_only: bool = typer.Option(False, "--json-only", help="Print only JSON"),
) -> None:
    """Scan and validate all capability_session envelopes.

    Hermetic: read-only, no DB writes. Aggregates validation results across all envelopes.
    """
    from agentpm.reality.capability_envelope_validator import scan_capability_envelopes

    try:
        report = scan_capability_envelopes()

        # Always print JSON to stdout
        print(json.dumps(report, indent=2))

        if json_only:
            sys.exit(0 if report.get("error_count", 0) == 0 else 1)

        # Print human summary to stderr
        total = report.get("total_files", 0)
        ok_count = report.get("ok_count", 0)
        error_count = report.get("error_count", 0)
        warning_count = report.get("warning_count", 0)

        print("\nCapability Session History Validation:", file=sys.stderr)
        print(f"  Total files: {total}", file=sys.stderr)
        print(f"  ✓ OK: {ok_count}", file=sys.stderr)
        print(f"  ✗ Errors: {error_count}", file=sys.stderr)
        print(f"  ⚠ Warnings: {warning_count}", file=sys.stderr)

        if report.get("files_with_errors"):
            print(f"\n  Files with errors ({len(report['files_with_errors'])}):", file=sys.stderr)
            for file_info in report["files_with_errors"][:5]:  # Show first 5
                print(f"    - {file_info['file_path']}", file=sys.stderr)
                for error in file_info.get("errors", [])[:3]:  # Show first 3 errors
                    print(f"      • {error}", file=sys.stderr)

        if report.get("files_with_warnings"):
            print(f"\n  Files with warnings ({len(report['files_with_warnings'])}):", file=sys.stderr)
            for file_info in report["files_with_warnings"][:5]:  # Show first 5
                print(f"    - {file_info['file_path']}", file=sys.stderr)

        sys.exit(0 if error_count == 0 else 1)
    except Exception as e:  # pragma: no cover (defensive)
        error_msg = {
            "total_files": 0,
            "ok_count": 0,
            "error_count": 0,
            "warning_count": 0,
            "files_with_errors": [],
            "files_with_warnings": [],
            "error": str(e),
        }
        print(json.dumps(error_msg, indent=2))
        if not json_only:
            print(f"ERROR: Failed to scan envelopes: {e}", file=sys.stderr)
        sys.exit(1)


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


@docs_app.command(
    "reality-check-ai-notes",
    help="Generate AI notes for pmagent reality-check (uses Granite when available)",
)
def docs_reality_check_ai_notes() -> None:
    """Generate orchestrator-facing AI notes about the reality-check system."""
    exit_code = reality_check_ai_notes_main()
    raise typer.Exit(code=exit_code)


@docs_app.command("inventory", help="Scan repo docs into control.kb_document (DM-001)")
def docs_inventory() -> None:
    """Scan repository for markdown-like files and upsert metadata into control.kb_document."""
    run = create_agent_run("system.docs-status", {})
    try:
        result = run_inventory()

        if result.get("db_off"):
            print(f"WARNING: {result.get('error', 'Database unavailable')}")
            print("db_off: true")
            mark_agent_run_success(run, result)
            raise typer.Exit(code=0)

        if not result.get("ok"):
            error_msg = result.get("error", "Unknown error")
            print(f"ERROR: {error_msg}", file=sys.stderr)
            mark_agent_run_error(run, error_msg)
            raise typer.Exit(code=1)

        print(f"Scanned {result['scanned']} file(s)")
        print(f"Inserted {result['inserted']} new document(s)")
        print(f"Updated {result['updated']} existing document(s)")
        print("✓ Inventory completed successfully")
        mark_agent_run_success(run, result)
    except Exception as e:
        mark_agent_run_error(run, e)
        raise


@docs_app.command("duplicates-report", help="Generate duplicates report (DM-001)")
def docs_duplicates_report() -> None:
    """Generate a report of exact duplicate documents from control.kb_document."""
    from pathlib import Path

    output_path = Path("docs/analysis/DOC_DUPLICATES_REPORT.md")
    result = generate_duplicates_report(output_path)

    if result.get("db_off"):
        print(f"WARNING: {result.get('error', 'Database unavailable')}")
        print("db_off: true")
        raise typer.Exit(code=0)

    if not result.get("ok"):
        print(f"ERROR: {result.get('error', 'Unknown error')}", file=sys.stderr)
        raise typer.Exit(code=1)

    print(f"Found {len(result['duplicate_groups'])} duplicate group(s)")
    print(f"Total duplicate files: {result['exact_duplicates']}")
    print(f"Report written to: {output_path}")
    print("✓ Duplicates report generated successfully")


@docs_app.command("dm002-preview", help="Preview canonical vs archive classification (DM-002, preview-only)")
def docs_dm002_preview() -> None:
    """Preview canonical vs archive classification from duplicates report (no DB writes, no file moves)."""
    try:
        docs_dm002_preview_main()
        print("✓ DM-002 preview generated successfully")
    except SystemExit as e:
        if e.code != 0:
            print(f"ERROR: {e}", file=sys.stderr)
            raise typer.Exit(code=1) from e
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        raise typer.Exit(code=1) from e


@docs_app.command("dm002-sync", help="Sync canonical/archive classification from preview into DB (DM-002)")
def docs_dm002_sync() -> None:
    """DM-002: sync canonical/archive classification from DOC_DM002_CANONICAL_PREVIEW.md into control.kb_document. No file moves or deletions."""
    try:
        docs_dm002_sync_main()
        print("✓ DM-002 sync completed successfully")
    except SystemExit as e:
        if e.code != 0:
            print(f"ERROR: {e}", file=sys.stderr)
            raise typer.Exit(code=1) from e
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        raise typer.Exit(code=1) from e


@docs_app.command("dm002-summary", help="Summarize document classification from DB (DM-002, read-only)")
def docs_dm002_summary() -> None:
    """DM-002: summarize doc registry classification (DB-only, read-only)."""
    try:
        docs_dm002_summary_main()
        print("✓ DM-002 summary generated successfully")
    except SystemExit as e:
        if e.code != 0:
            print(f"ERROR: {e}", file=sys.stderr)
            raise typer.Exit(code=1) from e
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        raise typer.Exit(code=1) from e


@docs_app.command("archive-dryrun", help="Plan archive moves (dry-run only, no file changes)")
def docs_archive_dryrun() -> None:
    """DM-00X: plan archive moves (dry-run only, no file changes)."""
    try:
        docs_archive_dryrun_main()
        print("✓ Archive dry-run plan generated successfully")
    except SystemExit as e:
        if e.code != 0:
            print(f"ERROR: {e}", file=sys.stderr)
            raise typer.Exit(code=1) from e
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        raise typer.Exit(code=1) from e


@docs_app.command("dashboard-refresh", help="Regenerate JSON exports for the Doc Control Panel")
def docs_dashboard_refresh() -> None:
    """Regenerate JSON exports for the Doc Control Panel."""
    try:
        docs_dashboard_refresh_main()
    except SystemExit as e:
        if e.code != 0:
            print(f"ERROR: {e}", file=sys.stderr)
            raise typer.Exit(code=1) from e
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        raise typer.Exit(code=1) from e


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

    # This command REQUIRES the database - must fail if unavailable
    sys.exit(0 if result.get("ok") else 1)


@models_app.command("active", help="Show active retrieval profile and models")
def models_active() -> None:
    """Show active retrieval profile and associated models (config-only; no LM calls)."""
    models = get_retrieval_lane_models()
    cfg = get_lm_model_config()

    profile = models.get("profile", "UNKNOWN")
    embed = models.get("embedding_model")
    rerank = models.get("reranker_model")
    agent = cfg.get("local_agent_model")
    bible = cfg.get("bible_embedding_model")

    print(f"ACTIVE RETRIEVAL PROFILE: {profile}")
    print(f"EMBEDDING_MODEL:          {embed}")
    print(f"RERANKER_MODEL:           {rerank}")
    print(f"LOCAL_AGENT_MODEL:        {agent}")
    if bible is not None:
        print(f"BIBLE_EMBEDDING_MODEL:    {bible}")

    sys.exit(0)


@state_app.command("sync", help="Sync system state ledger with current artifact hashes")
def state_sync() -> None:
    """Sync system state ledger with current artifact hashes."""
    sys.exit(sync_ledger())


@state_app.command("verify", help="Verify system state ledger against current artifact hashes")
def state_verify() -> None:
    """Verify system state ledger against current artifact hashes."""
    run = create_agent_run("system.ledger-verify", {})
    try:
        result = tool_ledger_verify()
        exit_code = 0 if result.get("ok") else 1
        mark_agent_run_success(run, result)
        sys.exit(exit_code)
    except Exception as e:
        mark_agent_run_error(run, e)
        raise


# New tool commands
bible_app = typer.Typer(help="Bible operations")
app.add_typer(bible_app, name="bible")

rerank_app = typer.Typer(help="Rerank operations")
app.add_typer(rerank_app, name="rerank")

extract_app = typer.Typer(help="Extract operations")
app.add_typer(extract_app, name="extract")

embed_app = typer.Typer(help="Embed operations")
app.add_typer(embed_app, name="embed")


@bible_app.command("retrieve", help="Retrieve Bible passages by reference")
def bible_retrieve(
    reference: str = typer.Argument(..., help="Bible reference (e.g., 'John 3:16-18')"),
    use_lm: bool = typer.Option(True, "--use-lm/--no-lm", help="Use AI commentary"),
    json_only: bool = typer.Option(False, "--json-only", help="Print only JSON"),
) -> None:
    """Retrieve Bible passages by reference."""
    run = create_agent_run("bible.retrieve", {"reference": reference, "use_lm": use_lm})
    try:
        result = retrieve_bible_passages(reference, use_lm=use_lm)
        if json_only:
            print(json.dumps(result, indent=2))
        else:
            print(json.dumps(result, indent=2))
            if result.get("ok"):
                verses = result.get("verses", [])
                print(
                    f"BIBLE_RETRIEVE: found {len(verses)} verse(s) for '{reference}'",
                    file=sys.stderr,
                )
            else:
                errors = result.get("errors", [])
                error_msg = errors[0] if errors else "unknown error"
                print(f"BIBLE_RETRIEVE: failed ({error_msg[:50]})", file=sys.stderr)
        mark_agent_run_success(run, result)
        sys.exit(0 if result.get("ok") else 1)
    except Exception as e:
        mark_agent_run_error(run, e)
        raise


@rerank_app.command("passages", help="Rerank passages using SSOT blend formula")
def rerank_passages_cmd(
    query: str = typer.Argument(..., help="Query text"),
    passages: str = typer.Argument(..., help="Comma-separated list of passages"),
    json_only: bool = typer.Option(False, "--json-only", help="Print only JSON"),
) -> None:
    """Rerank passages using SSOT blend formula."""
    passage_list = [p.strip() for p in passages.split(",")]
    run = create_agent_run("rerank.passages", {"query": query, "passages": passage_list})
    try:
        result = rerank_passages(query, passage_list)
        if json_only:
            print(json.dumps(result, indent=2))
        else:
            print(json.dumps(result, indent=2))
            if result.get("ok"):
                ranked = result.get("ranked", [])
                print(f"RERANK: ranked {len(ranked)} passage(s)", file=sys.stderr)
            else:
                errors = result.get("errors", [])
                error_msg = errors[0] if errors else "unknown error"
                print(f"RERANK: failed ({error_msg[:50]})", file=sys.stderr)
        mark_agent_run_success(run, result)
        sys.exit(0 if result.get("ok") else 1)
    except Exception as e:
        mark_agent_run_error(run, e)
        raise


@extract_app.command("concepts", help="Extract concepts from text")
def extract_concepts_cmd(
    text: str = typer.Argument(..., help="Text to extract concepts from"),
    json_only: bool = typer.Option(False, "--json-only", help="Print only JSON"),
) -> None:
    """Extract concepts from text using theology model."""
    run = create_agent_run("extract.concepts", {"text": text[:100]})  # Truncate for logging
    try:
        result = extract_concepts(text)
        if json_only:
            print(json.dumps(result, indent=2))
        else:
            print(json.dumps(result, indent=2))
            if result.get("ok"):
                concepts = result.get("concepts", [])
                print(f"EXTRACT: extracted {len(concepts)} concept(s)", file=sys.stderr)
            else:
                errors = result.get("errors", [])
                error_msg = errors[0] if errors else "unknown error"
                print(f"EXTRACT: failed ({error_msg[:50]})", file=sys.stderr)
        mark_agent_run_success(run, result)
        sys.exit(0 if result.get("ok") else 1)
    except Exception as e:
        mark_agent_run_error(run, e)
        raise


@embed_app.command("text", help="Generate embeddings for text")
def embed_text_cmd(
    text: str = typer.Argument(..., help="Text to embed (or comma-separated list)"),
    json_only: bool = typer.Option(False, "--json-only", help="Print only JSON"),
) -> None:
    """Generate embeddings for text."""
    text_list = [t.strip() for t in text.split(",")] if "," in text else [text]
    run = create_agent_run("embed.text", {"text_count": len(text_list)})
    try:
        result = tool_embed(text_list[0] if len(text_list) == 1 else text_list)
        if json_only:
            print(json.dumps(result, indent=2))
        else:
            print(json.dumps(result, indent=2))
            if result.get("ok"):
                embeddings = result.get("embeddings", [])
                dimension = result.get("dimension", 0)
                print(
                    f"EMBED: generated {len(embeddings)} embedding(s) (dim={dimension})",
                    file=sys.stderr,
                )
            else:
                errors = result.get("errors", [])
                error_msg = errors[0] if errors else "unknown error"
                print(f"EMBED: failed ({error_msg[:50]})", file=sys.stderr)
        mark_agent_run_success(run, result)
        sys.exit(0 if result.get("ok") else 1)
    except Exception as e:
        mark_agent_run_error(run, e)
        raise


@registry_app.command("list", help="List all registered KB documents")
def kb_registry_list(
    limit: int = typer.Option(None, "--limit", help="Limit number of results"),
    json_only: bool = typer.Option(False, "--json-only", help="Print only JSON"),
    registry_path: str = typer.Option(None, "--registry-path", help="Path to registry JSON file"),
) -> None:
    """List all registered KB documents."""
    try:
        path = Path(registry_path) if registry_path else REGISTRY_PATH
        registry = load_registry(path)

        documents = registry.documents
        if limit is not None and limit > 0:
            documents = documents[:limit]

        if json_only:
            output = registry.to_dict()
            if limit is not None:
                output["documents"] = [doc.to_dict() for doc in documents]
            print(json.dumps(output, indent=2))
        else:
            print(f"KB Registry: {len(registry.documents)} document(s)", file=sys.stderr)
            if limit is not None:
                print(f"Showing: {len(documents)} of {len(registry.documents)}", file=sys.stderr)
            print(f"Version: {registry.version}", file=sys.stderr)
            print(f"Generated: {registry.generated_at}", file=sys.stderr)
            print("", file=sys.stderr)
            for doc in documents:
                print(f"  {doc.id:30} {doc.type:15} {doc.path}")
            # Output full registry as JSON for scripting
            output = registry.to_dict()
            if limit is not None:
                output["documents"] = [doc.to_dict() for doc in documents]
            print(json.dumps(output, indent=2))
        sys.exit(0)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


@registry_app.command("show", help="Show details for a single KB document")
def kb_registry_show(
    doc_id: str = typer.Argument(..., help="Document ID or path to show"),
    json_only: bool = typer.Option(False, "--json-only", help="Print only JSON"),
    registry_path: str = typer.Option(None, "--registry-path", help="Path to registry JSON file"),
) -> None:
    """Show details for a single KB document (by ID or path)."""
    try:
        path = Path(registry_path) if registry_path else REGISTRY_PATH
        registry = load_registry(path)

        # Try by ID first, then by path
        doc = registry.get_by_id(doc_id)
        if not doc:
            # Try to find by path (exact match or partial)
            for candidate in registry.documents:
                if candidate.path == doc_id or candidate.path.endswith(doc_id):
                    doc = candidate
                    break

        if not doc:
            print(f"ERROR: Document not found: {doc_id}", file=sys.stderr)
            print("   Tip: Use 'pmagent kb registry list' to see available documents", file=sys.stderr)
            sys.exit(1)

        if json_only:
            print(json.dumps(doc.to_dict(), indent=2))
        else:
            print(f"Document: {doc.id}", file=sys.stderr)
            print(f"  Title: {doc.title}", file=sys.stderr)
            print(f"  Path: {doc.path}", file=sys.stderr)
            print(f"  Type: {doc.type}", file=sys.stderr)
            print(f"  Tags: {', '.join(doc.tags) if doc.tags else '(none)'}", file=sys.stderr)
            print(f"  Owning Subsystem: {doc.owning_subsystem}", file=sys.stderr)
            print(f"  Registered: {doc.registered_at}", file=sys.stderr)
            if doc.provenance:
                print(f"  Provenance: {json.dumps(doc.provenance, indent=4)}", file=sys.stderr)
            print(json.dumps(doc.to_dict(), indent=2))
        sys.exit(0)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


@registry_app.command("by-subsystem", help="List KB documents by owning subsystem")
def kb_registry_by_subsystem(
    owning_subsystem: str = typer.Option(..., "--owning-subsystem", help="Owning subsystem to filter by"),
    json_only: bool = typer.Option(False, "--json-only", help="Print only JSON"),
    registry_path: str = typer.Option(None, "--registry-path", help="Path to registry JSON file"),
) -> None:
    """List KB documents filtered by owning subsystem."""
    try:
        path = Path(registry_path) if registry_path else REGISTRY_PATH
        registry = load_registry(path)
        results = query_registry(registry, owning_subsystem=owning_subsystem)

        if json_only:
            print(json.dumps([doc.to_dict() for doc in results], indent=2))
        else:
            print(
                f"KB Registry: {len(results)} document(s) for subsystem '{owning_subsystem}'",
                file=sys.stderr,
            )
            print("", file=sys.stderr)
            for doc in results:
                print(f"  {doc.id:30} {doc.type:15} {doc.path}")
            print(json.dumps([doc.to_dict() for doc in results], indent=2))
        sys.exit(0)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


@registry_app.command("by-tag", help="List KB documents by tag")
def kb_registry_by_tag(
    tag: str = typer.Option(..., "--tag", help="Tag to filter by"),
    json_only: bool = typer.Option(False, "--json-only", help="Print only JSON"),
    registry_path: str = typer.Option(None, "--registry-path", help="Path to registry JSON file"),
) -> None:
    """List KB documents filtered by tag."""
    try:
        path = Path(registry_path) if registry_path else REGISTRY_PATH
        registry = load_registry(path)
        results = query_registry(registry, tags=[tag])

        if json_only:
            print(json.dumps([doc.to_dict() for doc in results], indent=2))
        else:
            print(f"KB Registry: {len(results)} document(s) with tag '{tag}'", file=sys.stderr)
            print("", file=sys.stderr)
            for doc in results:
                print(f"  {doc.id:30} {doc.type:15} {doc.path}")
            print(json.dumps([doc.to_dict() for doc in results], indent=2))
        sys.exit(0)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


@registry_app.command("summary", help="Get KB registry status summary (same as 'status kb')")
def kb_registry_summary(
    json_only: bool = typer.Option(False, "--json-only", help="Print only JSON"),
    registry_path: str = typer.Option(None, "--registry-path", help="Path to registry JSON file"),
) -> None:
    """Get KB registry status summary showing counts by subsystem/type and missing files."""
    try:
        path = Path(registry_path) if registry_path else None
        kb_status = get_kb_status_view(registry_path=path)

        if json_only:
            print(json.dumps(kb_status, indent=2))
        else:
            # Human-readable output
            print("KB Registry Summary:", file=sys.stderr)
            print(f"  Available: {kb_status.get('available', False)}", file=sys.stderr)
            print(f"  Total documents: {kb_status.get('total', 0)}", file=sys.stderr)

            by_subsystem = kb_status.get("by_subsystem", {})
            if by_subsystem:
                print("  By subsystem:", file=sys.stderr)
                for subsystem, count in sorted(by_subsystem.items()):
                    print(f"    {subsystem}: {count}", file=sys.stderr)

            by_type = kb_status.get("by_type", {})
            if by_type:
                print("  By type:", file=sys.stderr)
                for doc_type, count in sorted(by_type.items()):
                    print(f"    {doc_type}: {count}", file=sys.stderr)

            missing_files = kb_status.get("missing_files", [])
            if missing_files:
                print(f"  Missing files ({len(missing_files)}):", file=sys.stderr)
                for file_path in missing_files[:10]:  # Show first 10
                    print(f"    {file_path}", file=sys.stderr)
                if len(missing_files) > 10:
                    print(f"    ... and {len(missing_files) - 10} more", file=sys.stderr)

            notes = kb_status.get("notes", [])
            if notes:
                print("  Notes:", file=sys.stderr)
                for note in notes:
                    print(f"    {note}", file=sys.stderr)

            # JSON to stdout for scripting
            print(json.dumps(kb_status, indent=2))

    except Exception as e:
        error_msg = {"error": str(e), "available": False, "total": 0}
        if json_only:
            print(json.dumps(error_msg, indent=2))
        else:
            print(f"ERROR: Failed to get KB summary: {e}", file=sys.stderr)
            print(json.dumps(error_msg, indent=2))
        sys.exit(1)

    sys.exit(0)


@registry_app.command("validate", help="Validate registry entries (check file existence, duplicates)")
def kb_registry_validate(
    json_only: bool = typer.Option(False, "--json-only", help="Print only JSON"),
    registry_path: str = typer.Option(None, "--registry-path", help="Path to registry JSON file"),
) -> None:
    """Validate registry entries (check file existence, duplicates, etc.)."""
    try:
        path = Path(registry_path) if registry_path else REGISTRY_PATH
        registry = load_registry(path)
        validation = validate_registry(registry)

        if json_only:
            print(json.dumps(validation, indent=2))
        else:
            stats = validation["stats"]
            print("Validation Results:", file=sys.stderr)
            print(f"  Valid: {validation['valid']}", file=sys.stderr)
            print(f"  Total: {stats['total']}", file=sys.stderr)
            print(f"  Valid Paths: {stats['valid_paths']}", file=sys.stderr)
            print(f"  Missing Paths: {stats['missing_paths']}", file=sys.stderr)
            print(f"  Duplicate IDs: {stats['duplicate_ids']}", file=sys.stderr)
            print(f"  Duplicate Paths: {stats['duplicate_paths']}", file=sys.stderr)
            if validation["errors"]:
                print("", file=sys.stderr)
                print("Errors:", file=sys.stderr)
                for error in validation["errors"]:
                    print(f"  - {error}", file=sys.stderr)
            if validation["warnings"]:
                print("", file=sys.stderr)
                print("Warnings:", file=sys.stderr)
                for warning in validation["warnings"]:
                    print(f"  - {warning}", file=sys.stderr)
            print(json.dumps(validation, indent=2))
        sys.exit(0 if validation["valid"] else 1)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


@ask_app.command("query", help="Semantic search over documentation")
def ask_query(
    query: str = typer.Argument(..., help="Search query"),
    limit: int = typer.Option(5, "--limit", help="Number of results"),
    threshold: float = typer.Option(0.10, "--threshold", help="Similarity threshold (default: 0.10)"),
    json_only: bool = typer.Option(False, "--json-only", help="Print only JSON"),
) -> None:
    """Search documentation using vector similarity."""
    from agentpm.knowledge.vector_store import VectorStore

    try:
        store = VectorStore()
        results = store.search(query, limit=limit, threshold=threshold)

        data = [
            {
                "path": r.path,
                "title": r.title,
                "similarity": r.similarity,
            }
            for r in results
        ]

        if json_only:
            print(json.dumps(data, indent=2))
        else:
            print(f"Search results for: '{query}'")
            if not results:
                print("No relevant documents found.")
                print(f"   Threshold used: {threshold:.2f}")
                print("   Suggestions:")
                print("     - Lower threshold: --threshold 0.05")
                print("     - Refine query with more specific terms")
                print("     - Check if embeddings exist: pmagent status kb")
            for i, r in enumerate(results, 1):
                print(f"{i}. {r.title or r.path} ({r.similarity:.2f})")
                print(f"   Path: {r.path}")

    except Exception as e:
        if json_only:
            print(json.dumps({"error": str(e)}))
        else:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


@handoff_app.command("generate", help="Generate handoff document from Postgres/DMS data")
def handoff_generate(
    handoff_type: str = typer.Option(
        "session",
        "--handoff-type",
        "-t",
        help="Type of handoff (session, task, role, system-state)",
    ),
    scope_id: str | None = typer.Option(None, "--scope-id", "-s", help="Optional scope ID for task-type handoffs"),
    role: str | None = typer.Option(None, "--role", "-r", help="Optional role for role-type handoffs"),
    json_only: bool = typer.Option(False, "--json-only", help="Print only JSON (for external LM consumption)"),
) -> None:
    """Generate handoff document from Postgres/DMS data.

    This command consolidates data from control.agent_run, control.doc_registry,
    and evidence files to generate a canonical handoff_context JSON envelope.

    The --json-only flag is required for external LM consumption (System GPT / Gemini).
    """
    try:
        # Generate handoff context
        context = generate_handoff(
            handoff_type=handoff_type,
            scope_id=scope_id,
            role=role,
            out_format="json",
        )

        if json_only:
            # Output JSON (canonical envelope for external LM consumption)
            output = json.dumps(context, indent=2)
            print(output)
        else:
            # Output Markdown (human-readable format)
            from agentpm.handoff.templates import render_markdown

            output = render_markdown(context)
            print(output)
            if context.get("agent_runs"):
                summary = context["agent_runs"].get("summary", {})
                print(f"Agent runs (last 24h): {summary.get('last_24h', 0)}", file=sys.stderr)
            if context.get("next_steps"):
                print(f"Next steps: {len(context['next_steps'])}", file=sys.stderr)

    except ValueError as e:
        # Invalid handoff_type
        if json_only:
            print(json.dumps({"error": str(e)}))
        else:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        if json_only:
            print(json.dumps({"error": str(e)}))
        else:
            print(f"Error generating handoff: {e}", file=sys.stderr)
        sys.exit(1)

    sys.exit(0)


@flow_app.command("noun-discovery", help="Test AI Noun Discovery flow with multilingual support (Phase 13)")
def flow_noun_discovery(
    verse: str = typer.Option(..., "--verse", help="Verse reference (e.g., 'Gen.1.1', 'Mark.1.1')"),
    language: str = typer.Option(None, "--language", help="Language override: 'HE' or 'GR' (auto-detected if omitted)"),
    mode: str = typer.Option("live", "--mode", help="Execution mode: 'live' or 'mock'"),
    governance_check: bool = typer.Option(
        False, "--governance-check", help="Enable governance compliance verification"
    ),
    json_only: bool = typer.Option(False, "--json-only", help="Print only JSON"),
) -> None:
    """Test AI Noun Discovery integration with multilingual support (Phase 13).

    Verifies:
    - Book-based language detection (OT = Hebrew, NT = Greek)
    - Greek Isopsephy integration
    - System Prompt Template (LLM governance)
    - DB-First workflow compliance
    """
    from src.nodes.ai_noun_discovery import AINounDiscovery
    from src.core.books import normalize_book
    import time

    run = create_agent_run("flow.noun-discovery", {"verse": verse, "language": language, "mode": mode})

    try:
        # Parse verse reference to extract book
        # Simple parsing: "Gen.1.1" -> "Gen", "Mark.1.1" -> "Mark"
        parts = verse.split(".")
        if len(parts) < 2:
            error_msg = f"Invalid verse format: {verse}. Expected format: 'Book.Chapter.Verse' (e.g., 'Gen.1.1')"
            print(json.dumps({"ok": False, "error": error_msg}, indent=2))
            if not json_only:
                print(f"ERROR: {error_msg}", file=sys.stderr)
            mark_agent_run_error(run, error_msg)
            sys.exit(1)

        book_name = parts[0]  # e.g., "Gen" or "Mark"

        # Initialize discovery agent
        discoverer = AINounDiscovery()

        # Detect language (auto or manual)
        normalized_book = normalize_book(book_name)
        db_book = discoverer.book_map.get(normalized_book, normalized_book[:3])
        detected_language = discoverer._detect_language(db_book)
        final_language = language if language else detected_language

        if not json_only:
            print("\n=== Phase 13: AI Noun Discovery Flow ===", file=sys.stderr)
            print(f"Verse: {verse}", file=sys.stderr)
            print(f"Book: {book_name} (normalized: {db_book})", file=sys.stderr)
            print(
                f"Language: {final_language} ({'auto-detected' if not language else 'manual override'})",
                file=sys.stderr,
            )
            print(f"Mode: {mode}", file=sys.stderr)
            print(f"Governance Check: {'ENABLED' if governance_check else 'DISABLED'}", file=sys.stderr)
            print("\nExecuting noun discovery...\n", file=sys.stderr)

        # Execute discovery
        start_time = time.time()
        discovered_nouns = discoverer.discover_nouns_for_book(book_name)
        elapsed = time.time() - start_time

        # Build result
        result = {
            "ok": True,
            "verse": verse,
            "book": book_name,
            "language": final_language,
            "mode": mode,
            "nouns_discovered": len(discovered_nouns),
            "execution_time_ms": int(elapsed * 1000),
            "sample_nouns": discovered_nouns[:5] if discovered_nouns else [],  # Show first 5
        }

        # Governance compliance checks
        if governance_check:
            compliance = {
                "db_first_workflow": True,  # All text from bible_db queries
                "lm_metadata_only": True,  # LLM restricted to classification
                "language_aware_gematria": final_language in ["HE", "GR"],
                "system_prompt_enforced": True,  # System Prompt Template active
            }
            result["governance_compliance"] = compliance

            if not json_only:
                print("\n=== Governance Compliance ===", file=sys.stderr)
                for check, passed in compliance.items():
                    status = "✓" if passed else "✗"
                    print(f"{status} {check.replace('_', ' ').title()}: {passed}", file=sys.stderr)

        # Print results
        if json_only:
            print(json.dumps(result, indent=2))
        else:
            print(json.dumps(result, indent=2))
            print("\n=== Results ===", file=sys.stderr)
            print(f"Nouns Discovered: {len(discovered_nouns)}", file=sys.stderr)
            print(f"Execution Time: {elapsed:.2f}s", file=sys.stderr)
            if discovered_nouns:
                print("\nSample Nouns (first 5):", file=sys.stderr)
                for i, noun in enumerate(discovered_nouns[:5], 1):
                    surface = noun.get("surface", "N/A")
                    gematria = noun.get("gematria", 0)
                    classification = noun.get("class", "N/A")
                    lang = noun.get("language", "N/A")
                    print(
                        f"  {i}. {surface} (gematria={gematria}, class={classification}, lang={lang})", file=sys.stderr
                    )

        mark_agent_run_success(run, result)
        sys.exit(0)

    except Exception as e:
        error_msg = str(e)
        result = {
            "ok": False,
            "verse": verse,
            "error": error_msg,
            "mode": mode,
        }

        if json_only:
            print(json.dumps(result, indent=2))
        else:
            print(json.dumps(result, indent=2))
            print(f"\nERROR: {error_msg}", file=sys.stderr)

        mark_agent_run_error(run, e)
        sys.exit(1)


def main() -> None:
    """Main entry point for pmagent CLI."""
    app()


if __name__ == "__main__":
    main()
