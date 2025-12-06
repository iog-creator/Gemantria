#!/usr/bin/env python3
"""
Phase-3A Graph Stats Importer — Import exports/graph_stats.json into database.

Usage:
    python -m scripts.db_import_graph_stats --source exports/graph_stats.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from uuid import UUID, uuid4

from sqlalchemy import insert
from sqlalchemy.exc import OperationalError, ProgrammingError

from pmagent.db.loader import DbDriverMissingError, DbUnavailableError, get_control_engine
from pmagent.db.models_graph_stats import Base, GraphStatsSnapshot

# Add project root to path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def flatten_metrics(data: dict, prefix: str = "") -> list[tuple[str, float | int | dict]]:
    """
    Flatten graph_stats JSON into (metric_name, value) tuples.

    Examples:
        {"nodes": 100} -> [("nodes", 100)]
        {"centrality": {"avg_degree": 0.5}} -> [("centrality.avg_degree", 0.5)]
        {"centrality": {...}} -> [("centrality", {...})]  # for complex objects
    """
    metrics: list[tuple[str, float | int | dict]] = []

    for key, value in data.items():
        full_key = f"{prefix}.{key}" if prefix else key

        if isinstance(value, (int, float)):
            metrics.append((full_key, value))
        elif isinstance(value, dict):
            # For complex objects like centrality, store both flattened and full object
            # Store the full object as JSON
            metrics.append((full_key, value))
            # Also flatten nested keys
            metrics.extend(flatten_metrics(value, prefix=full_key))
        elif isinstance(value, list):
            # Lists are stored as JSON
            metrics.append((full_key, value))
        else:
            # Other types (strings, etc.) stored as JSON
            metrics.append((full_key, value))

    return metrics


def import_graph_stats(source_path: Path, snapshot_id: UUID | None = None) -> dict:
    """
    Import graph_stats.json into database.

    Args:
        source_path: Path to graph_stats.json file.
        snapshot_id: Optional UUID for snapshot grouping (generated if None).

    Returns:
        Dictionary with import result:
        {
            "ok": bool,
            "inserted": int,
            "errors": list[str],
            "source_path": str,
            "snapshot_id": str (UUID),
        }
    """
    result: dict = {
        "ok": False,
        "inserted": 0,
        "errors": [],
        "source_path": str(source_path),
        "snapshot_id": None,
    }

    # Check if source file exists
    if not source_path.exists():
        result["errors"].append("missing_export: source file does not exist")
        return result

    # Generate snapshot ID
    if snapshot_id is None:
        snapshot_id = uuid4()
    result["snapshot_id"] = str(snapshot_id)

    # Load JSON
    try:
        with open(source_path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        result["errors"].append(f"invalid_json: {e}")
        return result
    except Exception as e:
        result["errors"].append(f"read_error: {e}")
        return result

    # Get database engine
    try:
        engine = get_control_engine()
    except DbDriverMissingError as e:
        result["errors"].append("db_driver_missing: database driver not installed")
        result["mode"] = "db_off"
        return result
    except DbUnavailableError as e:
        result["errors"].append(f"db_unavailable: {e}")
        result["mode"] = "db_off"
        return result

    # Ensure table exists (create if needed)
    try:
        Base.metadata.create_all(engine, tables=[GraphStatsSnapshot.__table__])
    except Exception as e:
        result["errors"].append(f"table_creation_error: {e}")
        return result

    # Flatten metrics
    metrics = flatten_metrics(data)

    # Insert rows
    try:
        with engine.begin() as conn:
            rows_to_insert = []
            for metric_name, metric_value in metrics:
                # Determine if value should go in metric_value or metric_json
                if isinstance(metric_value, (int, float)):
                    rows_to_insert.append(
                        {
                            "snapshot_id": snapshot_id,
                            "metric_name": metric_name,
                            "metric_value": float(metric_value),
                            "metric_json": None,
                        }
                    )
                else:
                    # Store complex values as JSON
                    rows_to_insert.append(
                        {
                            "snapshot_id": snapshot_id,
                            "metric_name": metric_name,
                            "metric_value": None,
                            "metric_json": metric_value,
                        }
                    )

            if rows_to_insert:
                stmt = insert(GraphStatsSnapshot).values(rows_to_insert)
                result_obj = conn.execute(stmt)
                result["inserted"] = result_obj.rowcount or len(rows_to_insert)
                result["ok"] = True
            else:
                result["errors"].append("no_metrics: no metrics found in JSON")
                return result

    except ProgrammingError as e:
        if "does not exist" in str(e) or "relation" in str(e).lower():
            result["errors"].append(f"table_missing: {e}")
        else:
            result["errors"].append(f"sql_error: {e}")
        return result
    except OperationalError as e:
        result["errors"].append(f"db_connection_error: {e}")
        return result
    except Exception as e:
        result["errors"].append(f"unexpected_error: {e}")
        return result

    return result


def main() -> int:
    """CLI entrypoint."""
    import argparse

    parser = argparse.ArgumentParser(description="Import graph_stats.json into database")
    parser.add_argument(
        "--source",
        type=Path,
        default=Path("exports/graph_stats.json"),
        help="Path to graph_stats.json file (default: exports/graph_stats.json)",
    )
    args = parser.parse_args()

    result = import_graph_stats(args.source)

    # Output JSON result
    import json as json_module

    print(json_module.dumps(result, indent=2, default=str))

    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
