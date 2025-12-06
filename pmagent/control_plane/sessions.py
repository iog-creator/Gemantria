from scripts.config.env import get_rw_dsn
# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

"""Capability session management with PoR checklist."""

import json
import pathlib
from typing import Any, Dict, List

try:
    import psycopg
except ImportError:
    psycopg = None

from pmagent.control_plane.doc_fragments import (
    compute_sha256,
    get_required_fragments,
    resolve_anchor,
    verify_fragment,
)


def build_por_checklist(project_id: int, repo_root: pathlib.Path | None = None) -> List[Dict[str, Any]]:
    """
    Build PoR checklist from required document fragments.
    Returns list of fragment entries with src, anchor, sha256, uri.
    """
    if repo_root is None:
        repo_root = pathlib.Path(__file__).resolve().parents[3]

    checklist = []
    required = get_required_fragments()

    for src, anchor in required:
        filepath = repo_root / src
        if not filepath.exists():
            continue

        content = filepath.read_text(encoding="utf-8")
        if anchor:
            fragment_content = resolve_anchor(content, anchor)
            if fragment_content is None:
                # Use full file if anchor not found
                fragment_content = content
        else:
            fragment_content = content

        sha256_hash = compute_sha256(fragment_content)

        checklist.append(
            {
                "src": src,
                "anchor": anchor,
                "sha256": sha256_hash,
                "uri": f"file://{filepath}",
            }
        )

    return checklist


def create_session(
    project_id: int,
    rule_id: str,
    tiny_menu: List[str],
    ttl_s: int = 3600,
    repo_root: pathlib.Path | None = None,
) -> str:
    """
    Create a capability session with PoR checklist.
    Returns session ID (UUID as string).
    """
    if psycopg is None:
        raise RuntimeError("psycopg not available")

    por_checklist = build_por_checklist(project_id, repo_root)
    por_json = {"fragments": por_checklist, "count": len(por_checklist)}

    dsn = get_rw_dsn()
    if not dsn:
        raise RuntimeError("GEMATRIA_DSN not set")

    with psycopg.connect(dsn) as conn, conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO control.capability_session
            (project_id, rule_id, por_json, tiny_menu, ttl_s)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
            """,
            (project_id, rule_id, json.dumps(por_json), tiny_menu, ttl_s),
        )
        session_id = cur.fetchone()[0]
        conn.commit()
        return str(session_id)


def get_session(session_id: str) -> Dict[str, Any] | None:
    """Get session by ID. Returns None if not found or expired."""
    if psycopg is None:
        return None

    dsn = get_rw_dsn()
    if not dsn:
        return None

    try:
        with psycopg.connect(dsn) as conn, conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, project_id, rule_id, por_json, tiny_menu, ttl_s, created_at
                FROM control.capability_session
                WHERE id = %s
                """,
                (session_id,),
            )
            row = cur.fetchone()
            if row is None:
                return None

            # Check TTL
            import datetime

            created_at = row[6]
            ttl_s = row[5]
            age_s = (datetime.datetime.now(datetime.UTC) - created_at).total_seconds()
            if age_s > ttl_s:
                return None  # Expired

            return {
                "id": str(row[0]),
                "project_id": row[1],
                "rule_id": str(row[2]),
                "por_json": row[3],
                "tiny_menu": row[4],
                "ttl_s": row[5],
                "created_at": row[6].isoformat(),
            }
    except Exception:
        return None


def verify_por_checklist(project_id: int, por_json: Dict[str, Any]) -> bool:
    """
    Verify PoR checklist fragments match current document state.
    Returns True if all fragments match, False otherwise.
    """
    fragments = por_json.get("fragments", [])
    if not fragments:
        return False

    for frag in fragments:
        src = frag.get("src")
        anchor = frag.get("anchor", "")
        expected_sha256 = frag.get("sha256")

        if not src or not expected_sha256:
            return False

        if not verify_fragment(project_id, src, anchor, expected_sha256):
            return False

    return True
