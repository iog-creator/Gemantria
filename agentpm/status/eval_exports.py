#!/usr/bin/env python3
"""
Eval Exports Helpers

AgentPM-First:M4: Shared helpers for reading Phase-8/10 eval export files.
Hermetic (file-only, no DB/LM calls) and tolerant of missing/invalid files.

These helpers are used by:
- Unified snapshot helper (agentpm/status/snapshot.py)
- API endpoints (/api/lm/indicator, /api/db/health_timeline, /api/eval/edges)
- WebUI pages (dashboard, lm-insights, db-insights)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# Standard paths for eval exports
REPO_ROOT = Path(__file__).resolve().parents[2]
LM_INDICATOR_PATH = REPO_ROOT / "share" / "atlas" / "control_plane" / "lm_indicator.json"
EDGE_CLASS_COUNTS_PATH = REPO_ROOT / "share" / "eval" / "edges" / "edge_class_counts.json"
DB_HEALTH_PATH = REPO_ROOT / "evidence" / "pm_snapshot" / "db_health.json"


def load_lm_indicator() -> dict[str, Any]:
    """Load LM indicator export (Phase-4C).

    Returns:
        Dictionary with LM indicator data or empty dict with note if missing/invalid:
        {
            "status": "offline" | "healthy" | "degraded",
            "reason": str,
            "success_rate": float,
            "error_rate": float,
            "total_calls": int,
            "db_off": bool,
            "top_error_reason": str | None,
            "window_days": int,
            "generated_at": str
        }
        Or {"note": "..."} if file is missing/invalid.
    """
    try:
        if not LM_INDICATOR_PATH.exists():
            return {
                "note": "LM indicator export not available (file missing)",
                "available": False,
            }

        data = json.loads(LM_INDICATOR_PATH.read_text(encoding="utf-8"))
        # Validate basic structure
        if not isinstance(data, dict):
            return {
                "note": "LM indicator export invalid (not a dict)",
                "available": False,
            }

        # Return with availability flag
        result = dict(data)
        result["available"] = True
        return result

    except (json.JSONDecodeError, OSError) as e:
        return {
            "note": f"LM indicator export invalid (parse error: {e})",
            "available": False,
        }
    except Exception as e:
        return {
            "note": f"LM indicator export error: {e}",
            "available": False,
        }


def load_edge_class_counts() -> dict[str, Any]:
    """Load edge class counts export (Phase-10).

    Returns:
        Dictionary with edge class counts or empty dict with note if missing/invalid:
        {
            "thresholds": {"strong": float, "weak": float},
            "counts": {"strong": int, "weak": int, "other": int}
        }
        Or {"note": "..."} if file is missing/invalid.
    """
    try:
        if not EDGE_CLASS_COUNTS_PATH.exists():
            return {
                "note": "Edge class counts export not available (file missing)",
                "available": False,
            }

        data = json.loads(EDGE_CLASS_COUNTS_PATH.read_text(encoding="utf-8"))
        # Validate basic structure
        if not isinstance(data, dict):
            return {
                "note": "Edge class counts export invalid (not a dict)",
                "available": False,
            }

        # Return with availability flag
        result = dict(data)
        result["available"] = True
        return result

    except (json.JSONDecodeError, OSError) as e:
        return {
            "note": f"Edge class counts export invalid (parse error: {e})",
            "available": False,
        }
    except Exception as e:
        return {
            "note": f"Edge class counts export error: {e}",
            "available": False,
        }


def load_db_health_snapshot() -> dict[str, Any]:
    """Load DB health snapshot (from pm.snapshot evidence).

    Returns:
        Dictionary with DB health data or empty dict with note if missing/invalid:
        {
            "ok": bool,
            "mode": "ready" | "partial" | "db_off",
            "notes": str,
            ...
        }
        Or {"note": "..."} if file is missing/invalid.
    """
    try:
        if not DB_HEALTH_PATH.exists():
            return {
                "note": "DB health snapshot not available (file missing; run `make pm.snapshot`)",
                "available": False,
            }

        data = json.loads(DB_HEALTH_PATH.read_text(encoding="utf-8"))
        # Validate basic structure
        if not isinstance(data, dict):
            return {
                "note": "DB health snapshot invalid (not a dict)",
                "available": False,
            }

        # Return with availability flag
        result = dict(data)
        result["available"] = True
        return result

    except (json.JSONDecodeError, OSError) as e:
        return {
            "note": f"DB health snapshot invalid (parse error: {e})",
            "available": False,
        }
    except Exception as e:
        return {
            "note": f"DB health snapshot error: {e}",
            "available": False,
        }


def get_eval_insights_summary() -> dict[str, Any]:
    """Get summary of all eval exports for unified snapshot.

    Returns:
        Dictionary with eval insights summary:
        {
            "lm_indicator": {...} (or {"note": "...", "available": False}),
            "db_health": {...} (or {"note": "...", "available": False}),
            "edge_class_counts": {...} (or {"note": "...", "available": False})
        }
    """
    return {
        "lm_indicator": load_lm_indicator(),
        "db_health": load_db_health_snapshot(),
        "edge_class_counts": load_edge_class_counts(),
    }
