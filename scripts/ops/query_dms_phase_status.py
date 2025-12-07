#!/usr/bin/env python3
"""
Query DMS for phase status using proper DSN loaders.

This script demonstrates the correct pattern for querying the DMS:
1. Pre-flight DB check (mandatory - Rule 050 evidence-first)
2. Use centralized DSN loaders from scripts.config.env
3. Handle db_off mode gracefully
4. Return structured JSON output
"""

import sys
import json
import subprocess
from pathlib import Path

# Add project root to path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

# Pre-flight DB check (mandatory before DMS queries)
preflight_script = REPO / "scripts" / "ops" / "preflight_db_check.py"
result = subprocess.run([sys.executable, str(preflight_script), "--mode", "strict"], capture_output=True)
if result.returncode != 0:
    print(result.stderr.decode(), file=sys.stderr)
    sys.exit(result.returncode)

from scripts.config.env import get_rw_dsn
import psycopg


def query_phase_documents() -> list[dict]:
    """Query doc_registry for phase-related documents."""
    dsn = get_rw_dsn()
    if not dsn:
        return []

    try:
        with psycopg.connect(dsn) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT path, tags, enabled, last_refreshed_at 
                    FROM control.doc_registry 
                    WHERE path LIKE '%PHASE%' 
                       OR tags @> '["phase-16"]' 
                       OR tags @> '["phase-17"]' 
                       OR tags @> '["phase-18"]'
                    ORDER BY path 
                    LIMIT 20
                """)
                rows = cur.fetchall()
                return [
                    {
                        "path": row[0],
                        "tags": row[1],
                        "enabled": row[2],
                        "last_refreshed_at": row[3].isoformat() if row[3] else None,
                    }
                    for row in rows
                ]
    except psycopg.OperationalError:
        return []


def query_phase_governance_artifacts() -> list[dict]:
    """Query governance_artifacts for phase completion status."""
    dsn = get_rw_dsn()
    if not dsn:
        return []

    try:
        with psycopg.connect(dsn) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT artifact_type, artifact_id, 
                           metadata->>'phase' as phase, 
                           metadata->>'status' as status, 
                           created_at 
                    FROM public.governance_artifacts 
                    WHERE artifact_type LIKE '%phase%' 
                       OR metadata->>'phase' IS NOT NULL 
                    ORDER BY created_at DESC 
                    LIMIT 15
                """)
                rows = cur.fetchall()
                return [
                    {
                        "artifact_type": row[0],
                        "artifact_id": row[1],
                        "phase": row[2],
                        "status": row[3],
                        "created_at": row[4].isoformat() if row[4] else None,
                    }
                    for row in rows
                ]
    except psycopg.OperationalError:
        return []


def main() -> int:
    """Main entry point."""
    phase_docs = query_phase_documents()
    phase_artifacts = query_phase_governance_artifacts()

    result = {
        "phase_documents": phase_docs,
        "phase_governance_artifacts": phase_artifacts,
        "db_available": len(phase_docs) > 0 or len(phase_artifacts) > 0,
    }

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
