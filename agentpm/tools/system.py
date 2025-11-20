#!/usr/bin/env python3
"""
System Tools - Health, control summary, docs status, ledger verify, reality check.
"""

from __future__ import annotations

from typing import Any

from scripts.control.control_summary import compute_control_summary
from scripts.guards.guard_db_health import check_db_health
from scripts.guards.guard_lm_health import check_lm_health
from scripts.graph.graph_overview import compute_graph_overview
from scripts.system.system_health import compute_system_health
from agentpm.scripts.state.ledger_verify import verify_ledger
from agentpm.reality.check import reality_check as check_reality
from agentpm.scripts.docs_inventory import run_inventory


def health(**kwargs: Any) -> dict[str, Any]:
    """System health check (DB + LM + Graph).

    Returns:
        Dict with health status for DB, LM, and Graph components.
    """
    db_health = check_db_health()
    lm_health = check_lm_health()
    graph_overview = compute_graph_overview()
    system_health = compute_system_health()

    return {
        "ok": True,
        "db": db_health,
        "lm": lm_health,
        "graph": graph_overview,
        "system": system_health,
    }


def control_summary(**kwargs: Any) -> dict[str, Any]:
    """Control-plane summary (aggregated status).

    Returns:
        Dict with control-plane status summary.
    """
    summary = compute_control_summary()
    return {
        "ok": True,
        "summary": summary,
    }


def docs_status(**kwargs: Any) -> dict[str, Any]:
    """Documentation status and inventory.

    Returns:
        Dict with documentation inventory and status.
    """
    inventory = run_inventory()
    return {
        "ok": True,
        "inventory": inventory,
    }


def ledger_verify(**kwargs: Any) -> dict[str, Any]:
    """Verify system state ledger against current artifact hashes.

    Returns:
        Dict with verification results.
    """
    exit_code, summary = verify_ledger()
    return {
        "ok": exit_code == 0,
        "exit_code": exit_code,
        "summary": summary,
    }


def reality_check(**kwargs: Any) -> dict[str, Any]:
    """Reality check for automated bring-up.

    Returns:
        Dict with reality check results.
    """
    result = check_reality(**kwargs)
    return {
        "ok": result.get("overall_ok", False),
        "result": result,
    }
