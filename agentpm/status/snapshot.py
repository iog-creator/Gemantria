#!/usr/bin/env python3
"""
System Snapshot Module

AgentPM-First:M3: Unified system snapshot helper for pm.snapshot and WebUI APIs.
Composes health, status explain, reality-check, AI tracking, and share manifest.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agentpm.kb.registry import analyze_freshness, load_registry, validate_registry
from agentpm.reality.check import reality_check as check_reality
from agentpm.status.eval_exports import get_eval_insights_summary
from agentpm.status.explain import explain_system_status
from agentpm.status.kb_metrics import compute_kb_doc_health_metrics
from agentpm.tools.system import health as tool_health
from scripts.config.env import get_rw_dsn
from scripts.guards.guard_db_health import check_db_health


def get_ai_tracking_summary() -> dict[str, Any]:
    """Get AI tracking summary from control.agent_run and control.agent_run_cli.

    Returns:
        Dictionary with AI tracking summary:
        {
            "ok": bool,
            "mode": "db_on" | "db_off",
            "summary": {
                "agent_run": {...},
                "agent_run_cli": {...}
            }
        }
    """
    try:
        import psycopg

        dsn = get_rw_dsn()
        if not dsn:
            return {
                "ok": False,
                "mode": "db_off",
                "note": "GEMATRIA_DSN not configured",
            }

        try:
            with psycopg.connect(dsn) as conn, conn.cursor() as cur:
                # Count recent agent_run records (runtime LM calls)
                cur.execute(
                    """
                    SELECT COUNT(*) as total,
                           COUNT(*) FILTER (WHERE created_at > now() - interval '24 hours') as last_24h,
                           COUNT(*) FILTER (WHERE created_at > now() - interval '7 days') as last_7d
                    FROM control.agent_run
                    """
                )
                agent_run_row = cur.fetchone()
                agent_run_total = agent_run_row[0] if agent_run_row else 0
                agent_run_24h = agent_run_row[1] if agent_run_row else 0
                agent_run_7d = agent_run_row[2] if agent_run_row else 0

                # Count recent agent_run_cli records (CLI commands)
                cur.execute(
                    """
                    SELECT COUNT(*) as total,
                           COUNT(*) FILTER (WHERE created_at > now() - interval '24 hours') as last_24h,
                           COUNT(*) FILTER (WHERE created_at > now() - interval '7 days') as last_7d,
                           COUNT(*) FILTER (WHERE status = 'success') as success_count,
                           COUNT(*) FILTER (WHERE status = 'error') as error_count
                    FROM control.agent_run_cli
                    """
                )
                agent_run_cli_row = cur.fetchone()
                agent_run_cli_total = agent_run_cli_row[0] if agent_run_cli_row else 0
                agent_run_cli_24h = agent_run_cli_row[1] if agent_run_cli_row else 0
                agent_run_cli_7d = agent_run_cli_row[2] if agent_run_cli_row else 0
                agent_run_cli_success = agent_run_cli_row[3] if agent_run_cli_row else 0
                agent_run_cli_error = agent_run_cli_row[4] if agent_run_cli_row else 0

                return {
                    "ok": True,
                    "mode": "db_on",
                    "summary": {
                        "agent_run": {
                            "total": agent_run_total,
                            "last_24h": agent_run_24h,
                            "last_7d": agent_run_7d,
                        },
                        "agent_run_cli": {
                            "total": agent_run_cli_total,
                            "last_24h": agent_run_cli_24h,
                            "last_7d": agent_run_cli_7d,
                            "success_count": agent_run_cli_success,
                            "error_count": agent_run_cli_error,
                        },
                    },
                }
        except Exception as e:
            return {
                "ok": False,
                "mode": "db_off",
                "error": f"AI tracking query failed: {e}",
            }
    except ImportError:
        # psycopg not available (hermetic mode)
        return {
            "ok": False,
            "mode": "db_off",
            "note": "psycopg not available (hermetic mode)",
        }
    except Exception as e:
        return {
            "ok": False,
            "mode": "db_off",
            "error": f"AI tracking failed: {e}",
        }


def get_kb_registry_summary(registry_path: Path | None = None) -> dict[str, Any]:
    """Get KB registry summary (advisory-only, non-gating).

    Args:
        registry_path: Path to kb_registry.json (defaults to share/kb_registry.json)

    Returns:
        Dictionary with KB registry summary:
        {
            "available": bool,
            "total": int,
            "valid": bool,
            "errors_count": int,
            "warnings_count": int,
            "note": str (if unavailable or has issues)
        }
    """
    if registry_path is None:
        repo_root = Path(__file__).resolve().parents[2]  # agentpm/status/snapshot.py -> agentpm/ -> repo root
        registry_path = repo_root / "share" / "kb_registry.json"

    try:
        # Load registry (returns empty registry if file doesn't exist)
        registry = load_registry(registry_path)

        # Run lightweight validation
        validation = validate_registry(registry)

        return {
            "available": registry_path.exists(),
            "total": len(registry.documents),
            "valid": validation["valid"],
            "errors_count": len(validation["errors"]),
            "warnings_count": len(validation["warnings"]),
        }
    except Exception as e:
        return {
            "available": False,
            "total": 0,
            "valid": False,
            "errors_count": 0,
            "warnings_count": 0,
            "note": f"Failed to load registry: {e}",
        }


def get_kb_status_view(registry_path: Path | None = None) -> dict[str, Any]:
    """Get KB-focused status view for PM/AgentPM planning (KB-Reg:M3b).

    Args:
        registry_path: Path to kb_registry.json (defaults to share/kb_registry.json)

    Returns:
        Dictionary with KB-focused status view:
        {
            "available": bool,
            "total": int,
            "by_subsystem": {subsystem: count, ...},
            "by_type": {type: count, ...},
            "missing_files": [path, ...],  # if any
            "notes": [str, ...]  # if any issues
        }
    """
    if registry_path is None:
        repo_root = Path(__file__).resolve().parents[2]  # agentpm/status/snapshot.py -> agentpm/ -> repo root
        registry_path = repo_root / "share" / "kb_registry.json"

    result: dict[str, Any] = {
        "available": False,
        "total": 0,
        "by_subsystem": {},
        "by_type": {},
        "missing_files": [],
        "notes": [],
    }

    if not registry_path.exists():
        result["notes"].append("Registry file not found")
        return result

    try:
        # Load registry
        registry = load_registry(registry_path)
        result["available"] = True
        result["total"] = len(registry.documents)

        # Determine repo_root for validation and freshness analysis
        # If registry is at share/kb_registry.json, repo_root is parent of share/
        # Otherwise, use registry_path.parent as fallback (for tests)
        if registry_path.name == "kb_registry.json" and registry_path.parent.name == "share":
            repo_root = registry_path.parent.parent
        else:
            # Fallback for test scenarios where registry is not in share/
            repo_root = registry_path.parent

        # Run validation to get missing files
        validation = validate_registry(registry, repo_root=repo_root)
        missing_files = [
            error.split(": ")[1] if ": " in error else error
            for error in validation["errors"]
            if "Missing file" in error or "does not exist" in error
        ]
        result["missing_files"] = missing_files

        # Build by_subsystem breakdown
        by_subsystem: dict[str, int] = {}
        for doc in registry.documents:
            subsystem = doc.owning_subsystem
            by_subsystem[subsystem] = by_subsystem.get(subsystem, 0) + 1
        result["by_subsystem"] = by_subsystem

        # Build by_type breakdown
        by_type: dict[str, int] = {}
        for doc in registry.documents:
            doc_type = doc.type
            by_type[doc_type] = by_type.get(doc_type, 0) + 1
        result["by_type"] = by_type

        # Add notes for validation issues
        if not validation["valid"]:
            result["notes"].append(f"Registry validation failed: {len(validation['errors'])} errors")
        if validation["warnings"]:
            result["notes"].append(f"Registry has {len(validation['warnings'])} warnings")

        # Run freshness analysis (KB-Reg:M6)
        try:
            # repo_root already determined above
            freshness = analyze_freshness(registry, repo_root=repo_root)
            result["freshness"] = freshness["summary"]
            result["freshness_details"] = {
                "stale_docs": freshness["stale_docs"],
                "missing_docs": freshness["missing_docs"],
                "out_of_sync_docs": freshness["out_of_sync_docs"],
            }
        except Exception as e:
            result["notes"].append(f"Freshness analysis failed: {e}")

    except Exception as e:
        result["notes"].append(f"Failed to load registry: {e}")

    return result


def get_kb_hints(kb_status_view: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Generate structured hints from KB registry status (KB-Reg:M4).

    Args:
        kb_status_view: KB status view from get_kb_status_view() (if None, will load it)

    Returns:
        List of hint dictionaries with structure:
        [
            {
                "level": "WARN" | "INFO",
                "code": "KB_*",
                "message": str,
                ...additional context fields...
            },
            ...
        ]
        Empty list if no issues found.
    """
    if kb_status_view is None:
        kb_status_view = get_kb_status_view()

    hints: list[dict[str, Any]] = []

    # Registry unavailable
    if not kb_status_view.get("available", False):
        hints.append(
            {
                "level": "INFO",
                "code": "KB_REGISTRY_UNAVAILABLE",
                "message": "KB registry file not found (registry may not be seeded yet)",
            }
        )
        return hints

    # Missing files
    missing_files = kb_status_view.get("missing_files", [])
    if missing_files:
        hints.append(
            {
                "level": "WARN",
                "code": "KB_MISSING_DOCS",
                "message": f"KB registry references {len(missing_files)} missing file(s)",
                "missing_count": len(missing_files),
                "missing_files": missing_files[:10],  # Limit to first 10
            }
        )

    # Low coverage subsystems (subsystems with only 1-2 docs)
    by_subsystem = kb_status_view.get("by_subsystem", {})
    low_coverage_subsystems = [
        (subsystem, count)
        for subsystem, count in by_subsystem.items()
        if count < 3 and subsystem not in ["root"]  # Exclude root as it's expected to be small
    ]
    if low_coverage_subsystems:
        for subsystem, count in low_coverage_subsystems:
            hints.append(
                {
                    "level": "INFO",
                    "code": "KB_LOW_COVERAGE_SUBSYSTEM",
                    "message": f"Subsystem '{subsystem}' has low document coverage ({count} doc(s))",
                    "subsystem": subsystem,
                    "have": count,
                }
            )

    # Validation notes (warnings/errors from registry validation)
    notes = kb_status_view.get("notes", [])
    if notes:
        for note in notes:
            if "validation" in note.lower() or "error" in note.lower() or "warning" in note.lower():
                hints.append(
                    {
                        "level": "WARN",
                        "code": "KB_VALIDATION_ISSUES",
                        "message": f"KB registry validation issue: {note}",
                    }
                )

    # Empty registry (seeded but no docs)
    total = kb_status_view.get("total", 0)
    if total == 0 and kb_status_view.get("available", False):
        hints.append(
            {
                "level": "INFO",
                "code": "KB_EMPTY_REGISTRY",
                "message": "KB registry exists but contains no documents (may need seeding)",
            }
        )

    # Freshness hints (KB-Reg:M6)
    freshness_details = kb_status_view.get("freshness_details", {})
    stale_docs = freshness_details.get("stale_docs", [])
    out_of_sync_docs = freshness_details.get("out_of_sync_docs", [])

    if stale_docs:
        hints.append(
            {
                "level": "WARN",
                "code": "KB_DOC_STALE",
                "message": f"{len(stale_docs)} document(s) are stale (exceed refresh interval)",
                "stale_count": len(stale_docs),
                "stale_docs": [
                    {"id": doc["id"], "path": doc["path"], "title": doc["title"]} for doc in stale_docs[:5]
                ],  # Limit to first 5
            }
        )

    if out_of_sync_docs:
        hints.append(
            {
                "level": "WARN",
                "code": "KB_DOC_OUT_OF_SYNC",
                "message": f"{len(out_of_sync_docs)} document(s) are out of sync (file modified after last check)",
                "out_of_sync_count": len(out_of_sync_docs),
                "out_of_sync_docs": [
                    {"id": doc["id"], "path": doc["path"], "title": doc["title"]} for doc in out_of_sync_docs[:5]
                ],  # Limit to first 5
            }
        )

    return hints


def get_share_manifest_summary(manifest_path: Path | None = None) -> dict[str, Any]:
    """Get share manifest summary.

    Args:
        manifest_path: Path to SHARE_MANIFEST.json (defaults to docs/SSOT/SHARE_MANIFEST.json)

    Returns:
        Dictionary with share manifest summary:
        {
            "ok": bool,
            "count": int,
            "items": [...]
        }
    """
    if manifest_path is None:
        # Default to repo root / docs/SSOT/SHARE_MANIFEST.json
        repo_root = Path(__file__).resolve().parents[3]
        manifest_path = repo_root / "docs" / "SSOT" / "SHARE_MANIFEST.json"

    try:
        if not manifest_path.exists():
            return {
                "ok": False,
                "count": 0,
                "error": f"Manifest file not found: {manifest_path}",
            }

        manifest_data = json.loads(manifest_path.read_text())
        if isinstance(manifest_data, dict):
            manifest_items = manifest_data.get("items", [])
            return {
                "ok": True,
                "count": len(manifest_items),
                "items": manifest_items[:10],  # First 10 items for summary
            }
        return {
            "ok": False,
            "count": 0,
            "error": "Manifest is not a dict",
        }
    except Exception as e:
        return {
            "ok": False,
            "count": 0,
            "error": f"Failed to read manifest: {e}",
        }


def get_system_snapshot(
    include_reality_check: bool = True,
    include_ai_tracking: bool = True,
    include_share_manifest: bool = True,
    include_eval_insights: bool = True,
    include_kb_registry: bool = True,
    include_kb_doc_health: bool = True,
    include_mcp_catalog: bool = True,
    reality_check_mode: str = "HINT",
    use_lm_for_explain: bool = False,
) -> dict[str, Any]:
    """Get unified system snapshot (pm.snapshot + API contract).

    Args:
        include_reality_check: Whether to include reality-check verdict
        include_ai_tracking: Whether to include AI tracking summary
        include_share_manifest: Whether to include share manifest summary
        include_eval_insights: Whether to include eval exports summary (Phase-8/10)
        include_kb_registry: Whether to include KB registry summary (advisory-only)
        include_kb_doc_health: Whether to include KB doc-health metrics (AgentPM-Next:M3)
        include_mcp_catalog: Whether to include MCP catalog summary (advisory-only)
        reality_check_mode: Mode for reality-check ("HINT" or "STRICT")
        use_lm_for_explain: Whether to use LM for status explanation

    Returns:
        Dictionary with complete system snapshot:
        {
            "overall_ok": bool,
            "generated_at": str (ISO),
            "db_health": {...},
            "system_health": {...},
            "status_explain": {...},
            "reality_check": {...} (if included),
            "ai_tracking": {...} (if included),
            "share_manifest": {...} (if included),
            "eval_insights": {...} (if included) - optional, export-driven analytics
            "kb_registry": {...} (if included) - optional, advisory-only, read-only in CI
            "kb_doc_health": {...} (if included) - optional, doc-health metrics (AgentPM-Next:M3)
            "mcp_catalog": {...} (if included) - optional, advisory-only, MCP tool catalog
        }
    """
    from datetime import datetime

    # Gather DB health
    db_health_json = {}
    try:
        db_health_json = check_db_health()
    except Exception as e:
        db_health_json = {
            "ok": False,
            "mode": "error",
            "error": f"guard_db_health failed: {e}",
        }

    # Gather system health (DB + LM + Graph)
    system_health_json = {}
    try:
        system_health_json = tool_health()
    except Exception as e:
        system_health_json = {
            "ok": False,
            "error": f"system_health failed: {e}",
            "db": db_health_json,
            "lm": {"ok": False, "mode": "error"},
            "graph": {"ok": False, "mode": "error"},
        }

    # Gather status explanation
    status_explain_json = {}
    try:
        status_explain_json = explain_system_status(use_lm=use_lm_for_explain)
    except Exception as e:
        status_explain_json = {
            "level": "ERROR",
            "headline": "Status explanation unavailable",
            "details": f"Failed to generate explanation: {e}",
        }

    # Gather reality-check verdict (if requested)
    reality_check_json = {}
    if include_reality_check:
        try:
            reality_check_json = check_reality(mode=reality_check_mode, skip_dashboards=False)
        except Exception as e:
            reality_check_json = {
                "command": "reality.check",
                "mode": reality_check_mode,
                "overall_ok": False,
                "error": f"reality_check failed: {e}",
            }

    # Gather AI tracking summary (if requested)
    ai_tracking_summary = {}
    if include_ai_tracking:
        ai_tracking_summary = get_ai_tracking_summary()

    # Gather share manifest summary (if requested)
    share_manifest_summary = {}
    if include_share_manifest:
        share_manifest_summary = get_share_manifest_summary()

    # Gather eval insights summary (if requested) - export-driven, advisory only
    eval_insights_summary = {}
    if include_eval_insights:
        try:
            eval_insights_summary = get_eval_insights_summary()
        except Exception as e:
            eval_insights_summary = {
                "note": f"Eval insights unavailable: {e}",
                "lm_indicator": {"available": False, "note": "Error loading eval insights"},
                "db_health": {"available": False, "note": "Error loading eval insights"},
                "edge_class_counts": {"available": False, "note": "Error loading eval insights"},
            }

    # Gather KB registry summary (if requested) - advisory only, non-gating
    kb_registry_summary = {}
    if include_kb_registry:
        try:
            kb_registry_summary = get_kb_registry_summary()
        except Exception as e:
            kb_registry_summary = {
                "available": False,
                "total": 0,
                "valid": False,
                "errors_count": 0,
                "warnings_count": 0,
                "note": f"KB registry unavailable: {e}",
            }

    # Gather KB doc-health metrics (if requested) - advisory only, non-gating (AgentPM-Next:M3)
    kb_doc_health_summary = {}
    if include_kb_doc_health:
        try:
            kb_doc_health_summary = compute_kb_doc_health_metrics()
        except Exception as e:
            kb_doc_health_summary = {
                "available": False,
                "metrics": {},
                "error": f"KB doc-health metrics unavailable: {e}",
            }

    # Determine overall_ok from components
    # NOTE: eval_insights and kb_registry are advisory only and do NOT affect overall_ok
    overall_ok = (
        db_health_json.get("ok", False)
        and system_health_json.get("ok", False)
        and (reality_check_json.get("overall_ok", True) if include_reality_check else True)
    )

    # Build snapshot
    snapshot = {
        "overall_ok": overall_ok,
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "db_health": db_health_json,
        "system_health": system_health_json,
        "status_explain": status_explain_json,
    }

    if include_reality_check:
        snapshot["reality_check"] = reality_check_json

    if include_ai_tracking:
        snapshot["ai_tracking"] = ai_tracking_summary

    if include_share_manifest:
        snapshot["share_manifest"] = share_manifest_summary

    if include_eval_insights:
        snapshot["eval_insights"] = eval_insights_summary

    if include_kb_registry:
        snapshot["kb_registry"] = kb_registry_summary
        # Generate KB hints from registry status (KB-Reg:M4)
        try:
            kb_status_view = get_kb_status_view()
            kb_hints = get_kb_hints(kb_status_view)
            snapshot["kb_hints"] = kb_hints
        except Exception as e:
            snapshot["kb_hints"] = [
                {
                    "level": "WARN",
                    "code": "KB_HINTS_ERROR",
                    "message": f"Failed to generate KB hints: {e}",
                }
            ]

    if include_kb_doc_health:
        snapshot["kb_doc_health"] = kb_doc_health_summary

    # Add MCP catalog summary (advisory-only, read-only)
    if include_mcp_catalog:
        try:
            from agentpm.adapters.mcp_db import catalog_read_ro

            mcp_catalog_result = catalog_read_ro()
            snapshot["mcp_catalog"] = {
                "available": mcp_catalog_result.get("ok", False),
                "tools_count": len(mcp_catalog_result.get("tools", [])),
                "error": mcp_catalog_result.get("error") if not mcp_catalog_result.get("ok", False) else None,
            }
        except Exception as e:
            snapshot["mcp_catalog"] = {
                "available": False,
                "tools_count": 0,
                "error": f"Failed to read MCP catalog: {e}",
            }

    # Add control-plane widget summaries (Phase-6D: downstream app read-only wiring)
    try:
        from agentpm.control_widgets.adapter import (
            load_biblescholar_reference_widget_props,
            load_graph_compliance_widget_props,
        )

        graph_compliance_props = load_graph_compliance_widget_props()
        biblescholar_reference_props = load_biblescholar_reference_widget_props()

        snapshot["control_widgets"] = {
            "graph_compliance": {
                "status": graph_compliance_props["status"],
                "label": graph_compliance_props["label"],
                "metrics": {
                    "totalRunsWithViolations": graph_compliance_props["metrics"]["totalRunsWithViolations"],
                    "windowDays": graph_compliance_props["metrics"]["windowDays"],
                },
            },
            "biblescholar_reference": {
                "status": biblescholar_reference_props["status"],
                "label": biblescholar_reference_props["label"],
                "metrics": {
                    "totalQuestions": biblescholar_reference_props["metrics"]["totalQuestions"],
                    "windowDays": biblescholar_reference_props["metrics"]["windowDays"],
                },
            },
        }
    except Exception as e:
        snapshot["control_widgets"] = {
            "error": f"Failed to load control-plane widgets: {e}",
            "graph_compliance": {"status": "unknown"},
            "biblescholar_reference": {"status": "unknown"},
        }

    return snapshot
