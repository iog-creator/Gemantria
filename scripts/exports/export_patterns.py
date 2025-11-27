#!/usr/bin/env python3
"""
Pattern Export Pipeline - Phase 12
Exports discovered patterns from database to JSON for visualization consumption.
"""

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.config.env import get_rw_dsn  # noqa: E402


def export_patterns():
    """Export patterns from database to exports/graph_patterns.json."""
    try:
        import psycopg2
        import psycopg2.extras
    except ImportError:
        print("ERROR: psycopg2 not available")
        return False

    dsn = get_rw_dsn()
    if not dsn:
        print("ERROR: No RW DSN available")
        return False

    try:
        conn = psycopg2.connect(dsn)
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Query all patterns with their occurrences
        query = """
            SELECT 
                p.id,
                p.name,
                p.type,
                p.definition,
                p.metadata,
                p.created_at,
                COUNT(po.id) as occurrence_count,
                COALESCE(AVG(po.score), 0) as avg_score,
                jsonb_agg(
                    jsonb_build_object(
                        'nodes', po.nodes,
                        'score', po.score
                    )
                ) FILTER (WHERE po.id IS NOT NULL) as occurrences
            FROM public.patterns p
            LEFT JOIN public.pattern_occurrences po ON p.id = po.pattern_id
            GROUP BY p.id, p.name, p.type, p.definition, p.metadata, p.created_at
            ORDER BY p.type, p.created_at DESC
        """

        cur.execute(query)
        patterns = cur.fetchall()

        # Format patterns for export
        patterns_export = []
        for p in patterns:
            pattern_data = {
                "id": str(p["id"]),
                "name": p["name"],
                "type": p["type"],
                "definition": p["definition"],
                "metadata": p["metadata"],
                "occurrence_count": p["occurrence_count"],
                "avg_score": float(p["avg_score"]),
                "occurrences": p["occurrences"] or [],
                "created_at": p["created_at"].isoformat() if p["created_at"] else None,
            }
            patterns_export.append(pattern_data)

        # Build export structure
        export_data = {
            "patterns": patterns_export,
            "metadata": {
                "total_count": len(patterns_export),
                "pattern_types": {},
                "generated_at": datetime.now(UTC).isoformat(),
                "source": "public.patterns (Phase 12)",
                "version": "1.0",
            },
        }

        # Count by type
        for p in patterns_export:
            ptype = p["type"]
            export_data["metadata"]["pattern_types"][ptype] = export_data["metadata"]["pattern_types"].get(ptype, 0) + 1

        # Write to file
        output_path = ROOT / "exports" / "graph_patterns.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        print(f"✅ Exported {len(patterns_export)} patterns to {output_path}")
        print(f"   Pattern types: {export_data['metadata']['pattern_types']}")

        cur.close()
        conn.close()

        return True

    except Exception as e:
        print(f"ERROR: Export failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = export_patterns()
    sys.exit(0 if success else 1)
