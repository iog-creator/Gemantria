from scripts.config.env import get_rw_dsn
# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

"""Compliance exporter: reads MVs and writes JSONs to share/atlas/control_plane/."""

import json
import pathlib
from typing import Any, Dict

try:
    import psycopg
except ImportError:
    psycopg = None


def export_compliance_head() -> Dict[str, Any]:
    """
    Export latest compliance snapshot (head).
    Returns dict with window info, ratios, pointer to most recent agent_run.
    """
    if psycopg is None:
        return {"error": "psycopg not available"}

    dsn = get_rw_dsn()
    if not dsn:
        return {"error": "GEMATRIA_DSN not set"}

    try:
        with psycopg.connect(dsn) as conn, conn.cursor() as cur:
            # Get latest agent_run ID
            cur.execute(
                """
                SELECT id, created_at
                FROM control.agent_run
                ORDER BY created_at DESC
                LIMIT 1
                """
            )
            latest_run = cur.fetchone()

            # Get 7d compliance
            cur.execute("SELECT * FROM control.mv_compliance_7d")
            compliance_7d = cur.fetchone()

            # Get 30d compliance
            cur.execute("SELECT * FROM control.mv_compliance_30d")
            compliance_30d = cur.fetchone()

            result = {
                "generated_at": compliance_7d[6].isoformat() if compliance_7d else None,  # updated_at
                "windows": {
                    "7d": {
                        "runs": compliance_7d[1] if compliance_7d else 0,
                        "por_ok_ratio": float(compliance_7d[2]) if compliance_7d and compliance_7d[2] else 0.0,
                        "schema_ok_ratio": float(compliance_7d[3]) if compliance_7d and compliance_7d[3] else 0.0,
                        "provenance_ok_ratio": float(compliance_7d[4]) if compliance_7d and compliance_7d[4] else 0.0,
                    }
                    if compliance_7d
                    else {},
                    "30d": {
                        "runs": compliance_30d[1] if compliance_30d else 0,
                        "por_ok_ratio": float(compliance_30d[2]) if compliance_30d and compliance_30d[2] else 0.0,
                        "schema_ok_ratio": float(compliance_30d[3]) if compliance_30d and compliance_30d[3] else 0.0,
                        "provenance_ok_ratio": float(compliance_30d[4])
                        if compliance_30d and compliance_30d[4]
                        else 0.0,
                    }
                    if compliance_30d
                    else {},
                },
                "latest_agent_run": {
                    "id": str(latest_run[0]) if latest_run else None,
                    "created_at": latest_run[1].isoformat() if latest_run else None,
                },
            }

            return result
    except Exception as e:
        return {"error": str(e)}


def export_top_violations(window: str) -> Dict[str, Any]:
    """
    Export top violations for a window (7d or 30d).
    Returns dict with violation code frequency map.
    """
    if psycopg is None:
        return {"error": "psycopg not available"}

    dsn = get_rw_dsn()
    if not dsn:
        return {"error": "GEMATRIA_DSN not set"}

    if window not in ("7d", "30d"):
        return {"error": f"Invalid window: {window} (must be 7d or 30d)"}

    try:
        with psycopg.connect(dsn) as conn, conn.cursor() as cur:
            # Refresh MV first
            cur.execute(f"SELECT control.refresh_compliance('{window}')")

            # Get violations_top from MV
            mv_name = f"mv_compliance_{window}"
            cur.execute(f"SELECT violations_top, updated_at FROM control.{mv_name}")
            row = cur.fetchone()

            if row is None:
                return {"window": window, "violations": {}, "updated_at": None}

            violations_top = row[0] or {}
            updated_at = row[1]

            return {
                "window": window,
                "violations": violations_top,
                "updated_at": updated_at.isoformat() if updated_at else None,
            }
    except Exception as e:
        return {"error": str(e)}


def write_compliance_exports(output_dir: pathlib.Path, strict_mode: str = "HINT") -> Dict[str, Any]:
    """
    Write all compliance exports to share/atlas/control_plane/.
    Returns dict with status of each export.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    results = {}

    # Export compliance.head.json
    try:
        head_data = export_compliance_head()
        head_path = output_dir / "compliance.head.json"
        with head_path.open("w") as f:
            json.dump(head_data, f, indent=2)
        results["compliance.head.json"] = "ok"
    except Exception as e:
        results["compliance.head.json"] = f"error: {e}"
        if strict_mode == "STRICT":
            raise

    # Export top_violations_7d.json
    try:
        violations_7d = export_top_violations("7d")
        violations_7d_path = output_dir / "top_violations_7d.json"
        with violations_7d_path.open("w") as f:
            json.dump(violations_7d, f, indent=2)
        results["top_violations_7d.json"] = "ok"
    except Exception as e:
        results["top_violations_7d.json"] = f"error: {e}"
        if strict_mode == "STRICT":
            raise

    # Export top_violations_30d.json
    try:
        violations_30d = export_top_violations("30d")
        violations_30d_path = output_dir / "top_violations_30d.json"
        with violations_30d_path.open("w") as f:
            json.dump(violations_30d, f, indent=2)
        results["top_violations_30d.json"] = "ok"
    except Exception as e:
        results["top_violations_30d.json"] = f"error: {e}"
        if strict_mode == "STRICT":
            raise

    return results
