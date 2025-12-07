#!/usr/bin/env python3
"""
KB Document Worklist Builder (AgentPM-Next:M1)

Builds a prioritized worklist of documentation tasks from KB registry status and hints.
Read-only, deterministic, hermetic (no writes, no LM calls).
"""

from __future__ import annotations

from datetime import datetime, UTC
from typing import Any

from pathlib import Path

from pmagent.kb.registry import load_registry, REGISTRY_PATH
from pmagent.status.snapshot import get_kb_status_view, get_kb_hints


def build_kb_doc_worklist(now: datetime | None = None, registry_path: Path | None = None) -> dict[str, Any]:
    """Build a prioritized worklist of documentation tasks from KB registry.

    Reads kb_status_view + kb_hints and produces a prioritized worklist:
    - Grouped by subsystem (pmagent, runtime, webui, docs, rules, etc.)
    - Ordered by severity: missing > stale > out_of_sync > low_coverage > other
    - Each item: {id, title, subsystem, type, severity, reason, suggested_action}

    Args:
        now: Current datetime for comparison (defaults to now)

    Returns:
        Dictionary with worklist structure:
        {
            "available": bool,
            "total_items": int,
            "by_subsystem": {subsystem: count, ...},
            "items": [
                {
                    "id": str,
                    "title": str,
                    "subsystem": str,
                    "type": str,
                    "severity": "missing" | "stale" | "out_of_sync" | "low_coverage" | "info",
                    "reason": str,
                    "suggested_action": str
                },
                ...
            ]
        }
    """
    if now is None:
        now = datetime.now(UTC)

    result: dict[str, Any] = {
        "available": False,
        "total_items": 0,
        "by_subsystem": {},
        "items": [],
    }

    # Load KB status view and hints
    try:
        kb_status_view = get_kb_status_view(registry_path=registry_path)
        kb_hints = get_kb_hints(kb_status_view)
    except Exception:
        # Registry unavailable or error loading
        return result

    if not kb_status_view.get("available", False):
        return result

    result["available"] = True

    # Load registry for document details
    try:
        actual_registry_path = registry_path if registry_path else REGISTRY_PATH
        registry = load_registry(actual_registry_path)
    except Exception:
        # Can't load registry, return empty worklist
        return result

    # Build worklist items from hints and freshness data
    items: list[dict[str, Any]] = []

    # Severity order: missing > stale > out_of_sync > low_coverage > info
    severity_order = {
        "missing": 0,
        "stale": 1,
        "out_of_sync": 2,
        "low_coverage": 3,
        "info": 4,
    }

    # Process missing docs (from freshness_details)
    freshness_details = kb_status_view.get("freshness_details", {})
    missing_docs = freshness_details.get("missing_docs", [])
    for doc_info in missing_docs:
        doc_id = doc_info.get("id", "unknown")
        doc = registry.get_by_id(doc_id)
        if doc:
            items.append(
                {
                    "id": doc.id,
                    "title": doc.title,
                    "subsystem": doc.owning_subsystem,
                    "type": doc.type,
                    "severity": "missing",
                    "reason": f"File not found: {doc.path}",
                    "suggested_action": f"Create or restore {doc.path}",
                }
            )

    # Process stale docs (from freshness_details)
    stale_docs = freshness_details.get("stale_docs", [])
    for doc_info in stale_docs:
        doc_id = doc_info.get("id", "unknown")
        doc = registry.get_by_id(doc_id)
        if doc:
            refresh_interval = doc_info.get("refresh_interval_days", "unknown")
            items.append(
                {
                    "id": doc.id,
                    "title": doc.title,
                    "subsystem": doc.owning_subsystem,
                    "type": doc.type,
                    "severity": "stale",
                    "reason": f"Document hasn't been refreshed in {refresh_interval} days",
                    "suggested_action": f"Review and update {doc.path}",
                }
            )

    # Process out-of-sync docs (from freshness_details)
    out_of_sync_docs = freshness_details.get("out_of_sync_docs", [])
    for doc_info in out_of_sync_docs:
        doc_id = doc_info.get("id", "unknown")
        doc = registry.get_by_id(doc_id)
        if doc:
            items.append(
                {
                    "id": doc.id,
                    "title": doc.title,
                    "subsystem": doc.owning_subsystem,
                    "type": doc.type,
                    "severity": "out_of_sync",
                    "reason": "File was modified after last registry refresh",
                    "suggested_action": f"Refresh registry entry for {doc.path}",
                }
            )

    # Process low coverage subsystems (from hints)
    for hint in kb_hints:
        if hint.get("code") == "KB_LOW_COVERAGE_SUBSYSTEM":
            subsystem = hint.get("subsystem", "unknown")
            have = hint.get("have", 0)
            items.append(
                {
                    "id": f"subsystem:{subsystem}",
                    "title": f"Subsystem '{subsystem}' documentation",
                    "subsystem": subsystem,
                    "type": "other",
                    "severity": "low_coverage",
                    "reason": f"Subsystem has only {have} document(s) (low coverage)",
                    "suggested_action": f"Add more documentation for {subsystem} subsystem",
                }
            )

    # Process validation issues (from hints)
    for hint in kb_hints:
        if hint.get("code") == "KB_VALIDATION_ISSUES":
            message = hint.get("message", "Registry validation issues detected")
            items.append(
                {
                    "id": "validation:issues",
                    "title": "KB Registry validation issues",
                    "subsystem": "docs",
                    "type": "other",
                    "severity": "info",
                    "reason": message,
                    "suggested_action": "Run 'pmagent kb registry validate' to see details",
                }
            )

    # Sort items by severity (missing first, then stale, etc.)
    items.sort(key=lambda x: severity_order.get(x["severity"], 99))

    # Build by_subsystem breakdown
    by_subsystem: dict[str, int] = {}
    for item in items:
        subsystem = item["subsystem"]
        by_subsystem[subsystem] = by_subsystem.get(subsystem, 0) + 1

    result["total_items"] = len(items)
    result["by_subsystem"] = by_subsystem
    result["items"] = items

    return result
