#!/usr/bin/env python3
"""
KB Documentation Health Metrics (AgentPM-Next:M3 helper)

Computes doc-health metrics from the KB registry (KB-Reg) and M2 fix manifests.
Read-only, hermetic, and safe for CI (missing inputs → advisory/unknown metrics).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, UTC
from pathlib import Path
from typing import Any

import json

from agentpm.kb.registry import load_registry, analyze_freshness, REGISTRY_PATH, REPO_ROOT


@dataclass
class KBDocHealthMetrics:
    """Container for KB doc-health metrics."""

    kb_fresh_ratio_overall: float | None
    kb_fresh_ratio_by_subsystem: dict[str, float]
    kb_missing_count_overall: int
    kb_missing_count_by_subsystem: dict[str, int]
    kb_stale_count_by_subsystem: dict[str, int]
    kb_fixes_applied_last_7d: int
    kb_debt_burned_down: dict[str, Any]
    notes: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "kb_fresh_ratio": {
                "overall": self.kb_fresh_ratio_overall,
                "by_subsystem": self.kb_fresh_ratio_by_subsystem,
            },
            "kb_missing_count": {
                "overall": self.kb_missing_count_overall,
                "by_subsystem": self.kb_missing_count_by_subsystem,
            },
            "kb_stale_count_by_subsystem": self.kb_stale_count_by_subsystem,
            "kb_fixes_applied_last_7d": self.kb_fixes_applied_last_7d,
            "kb_debt_burned_down": self.kb_debt_burned_down,
            "notes": self.notes,
        }


def _safe_load_json(path: Path) -> dict[str, Any] | None:
    """Load JSON from path, returning None on any error."""
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def _compute_fixes_applied_last_7d(
    manifests_dir: Path | None = None,
    now: datetime | None = None,
) -> tuple[int, list[str]]:
    """Aggregate `actions_applied` from M2 manifests in the last 7 days."""
    if manifests_dir is None:
        manifests_dir = REPO_ROOT / "evidence" / "plan_kb_fix"
    if now is None:
        now = datetime.now(UTC)

    if not manifests_dir.exists():
        return 0, ["No plan_kb_fix manifests directory; treating fixes_applied_last_7d as 0"]

    total_applied = 0
    notes: list[str] = []
    cutoff = now - timedelta(days=7)

    for path in sorted(manifests_dir.glob("run-*.json")):
        data = _safe_load_json(path)
        if not data:
            notes.append(f"Failed to parse manifest: {path}")
            continue

        src = data.get("source", {})
        generated_at = src.get("generated_at")
        if not generated_at:
            # If timestamp missing, treat as outside window but note it.
            notes.append(f"Manifest missing generated_at timestamp: {path}")
            continue

        try:
            ts = datetime.fromisoformat(generated_at)
            # If naive, assume UTC for safety.
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=UTC)
        except Exception:
            notes.append(f"Invalid generated_at timestamp in manifest: {path}")
            continue

        if ts < cutoff:
            continue

        summary = data.get("summary", {})
        applied = summary.get("actions_applied", 0)
        if isinstance(applied, int):
            total_applied += applied
        else:
            notes.append(f"Non-integer actions_applied in manifest: {path}")

    return total_applied, notes


def compute_kb_doc_health_metrics(
    registry_path: Path | None = None,
    manifests_dir: Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Compute KB doc-health metrics for reporting surfaces.

    This helper is read-only and hermetic:
    - Uses KB registry + freshness analysis for structural metrics.
    - Uses M2 evidence manifests for recent fix activity.
    - Degrades gracefully when inputs are missing (metrics become None/0, with notes).

    Returns a dictionary matching the KBDocHealthMetrics.to_dict() shape, wrapped with:
    {
        "available": bool,
        "metrics": { ...as above... }
    }
    """
    notes: list[str] = []

    if registry_path is None:
        registry_path = REGISTRY_PATH
    if now is None:
        now = datetime.now(UTC)

    if not registry_path.exists():
        notes.append("KB registry not found; metrics unavailable")
        metrics = KBDocHealthMetrics(
            kb_fresh_ratio_overall=None,
            kb_fresh_ratio_by_subsystem={},
            kb_missing_count_overall=0,
            kb_missing_count_by_subsystem={},
            kb_stale_count_by_subsystem={},
            kb_fixes_applied_last_7d=0,
            kb_debt_burned_down={"overall": None, "by_subsystem": {}, "note": "insufficient_history"},
            notes=notes,
        )
        return {"available": False, "metrics": metrics.to_dict()}

    try:
        registry = load_registry(registry_path)
    except Exception as e:
        notes.append(f"Failed to load registry for metrics: {e}")
        metrics = KBDocHealthMetrics(
            kb_fresh_ratio_overall=None,
            kb_fresh_ratio_by_subsystem={},
            kb_missing_count_overall=0,
            kb_missing_count_by_subsystem={},
            kb_stale_count_by_subsystem={},
            kb_fixes_applied_last_7d=0,
            kb_debt_burned_down={"overall": None, "by_subsystem": {}, "note": "insufficient_history"},
            notes=notes,
        )
        return {"available": False, "metrics": metrics.to_dict()}

    try:
        freshness = analyze_freshness(registry, repo_root=REPO_ROOT, now=now)
    except Exception as e:
        notes.append(f"Freshness analysis failed for metrics: {e}")
        metrics = KBDocHealthMetrics(
            kb_fresh_ratio_overall=None,
            kb_fresh_ratio_by_subsystem={},
            kb_missing_count_overall=0,
            kb_missing_count_by_subsystem={},
            kb_stale_count_by_subsystem={},
            kb_fixes_applied_last_7d=0,
            kb_debt_burned_down={"overall": None, "by_subsystem": {}, "note": "insufficient_history"},
            notes=notes,
        )
        return {"available": False, "metrics": metrics.to_dict()}

    summary = freshness.get("summary", {})
    total = int(summary.get("total", 0) or 0)
    stale_count = int(summary.get("stale_count", 0) or 0)
    missing_count = int(summary.get("missing_count", 0) or 0)

    # Overall fresh ratio: (total - stale - missing) / total * 100
    if total > 0:
        fresh_docs_estimate = total - stale_count - missing_count
        kb_fresh_ratio_overall: float | None = max(0.0, min(100.0, (fresh_docs_estimate / total) * 100.0))
    else:
        kb_fresh_ratio_overall = None
        notes.append("Registry is empty; kb_fresh_ratio_overall is unknown")

    # Per-subsystem counts (missing + stale)
    missing_by_id = {d["id"] for d in freshness.get("missing_docs", []) if "id" in d}
    stale_by_id = {d["id"] for d in freshness.get("stale_docs", []) if "id" in d}

    total_by_subsystem: dict[str, int] = {}
    missing_by_subsystem: dict[str, int] = {}
    stale_by_subsystem: dict[str, int] = {}

    for doc in registry.documents:
        subsystem = doc.owning_subsystem
        total_by_subsystem[subsystem] = total_by_subsystem.get(subsystem, 0) + 1

        if doc.id in missing_by_id:
            missing_by_subsystem[subsystem] = missing_by_subsystem.get(subsystem, 0) + 1
        elif doc.id in stale_by_id:
            stale_by_subsystem[subsystem] = stale_by_subsystem.get(subsystem, 0) + 1

    kb_fresh_ratio_by_subsystem: dict[str, float] = {}
    for subsystem, sub_total in total_by_subsystem.items():
        if sub_total <= 0:
            continue
        sub_missing = missing_by_subsystem.get(subsystem, 0)
        sub_stale = stale_by_subsystem.get(subsystem, 0)
        sub_fresh_estimate = sub_total - sub_missing - sub_stale
        ratio = max(0.0, min(100.0, (sub_fresh_estimate / sub_total) * 100.0))
        kb_fresh_ratio_by_subsystem[subsystem] = ratio

    kb_missing_count_by_subsystem = missing_by_subsystem
    kb_stale_count_by_subsystem = stale_by_subsystem

    # Fixes applied in last 7 days from M2 manifests.
    fixes_last_7d, fix_notes = _compute_fixes_applied_last_7d(
        manifests_dir=manifests_dir,
        now=now,
    )
    notes.extend(fix_notes)

    # Debt burned down requires historical snapshots; for now, expose a placeholder.
    kb_debt_burned_down = {
        "overall": None,
        "by_subsystem": {},
        "note": "insufficient_history",
    }

    metrics = KBDocHealthMetrics(
        kb_fresh_ratio_overall=kb_fresh_ratio_overall,
        kb_fresh_ratio_by_subsystem=kb_fresh_ratio_by_subsystem,
        kb_missing_count_overall=missing_count,
        kb_missing_count_by_subsystem=kb_missing_count_by_subsystem,
        kb_stale_count_by_subsystem=kb_stale_count_by_subsystem,
        kb_fixes_applied_last_7d=fixes_last_7d,
        kb_debt_burned_down=kb_debt_burned_down,
        notes=notes,
    )

    return {"available": True, "metrics": metrics.to_dict()}
