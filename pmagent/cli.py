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

app = typer.Typer(add_completion=False, no_args_is_help=True)
health_app = typer.Typer(help="Health check commands")
app.add_typer(health_app, name="health")


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


def main() -> None:
    """Main entry point for pmagent CLI."""
    app()


if __name__ == "__main__":
    main()
