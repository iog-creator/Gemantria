"""Document fragment management for PoR (Proof-of-Read)."""

# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

import hashlib
import pathlib
from typing import List, Tuple

from scripts.config.env import get_rw_dsn

try:
    import psycopg
except ImportError:
    psycopg = None


def compute_sha256(content: str) -> str:
    """Compute SHA256 hash of content (hex string)."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def compute_file_sha256(filepath: pathlib.Path) -> str:
    """Compute SHA256 hash of file content (hex string)."""
    h = hashlib.sha256()
    with filepath.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def resolve_anchor(content: str, anchor: str) -> str | None:
    """
    Resolve a fragment anchor from markdown content.
    Supports:
    - Section headings: "## Section Name" -> anchor "section-name"
    - Explicit anchors: "{#anchor-name}"
    - Paragraph references: "§1", "§2.3"
    Returns the fragment text or None if not found.
    """
    lines = content.split("\n")

    # Try heading-based anchor (convert to slug)
    anchor_slug = anchor.lower().replace(" ", "-").replace("_", "-")

    # Look for matching heading
    in_section = False
    section_lines = []
    for i, line in enumerate(lines):
        if line.startswith("#"):
            # Extract heading text
            heading_text = line.lstrip("#").strip()
            heading_slug = heading_text.lower().replace(" ", "-").replace("_", "-")
            if heading_slug == anchor_slug or heading_text == anchor:
                in_section = True
                section_lines = [line]
                continue

        if in_section:
            # Stop at next heading of same or higher level
            if line.startswith("#") and not line.startswith("##"):
                break
            if line.startswith("##") and i > 0:
                prev_line = lines[i - 1]
                if prev_line.startswith("#") and not prev_line.startswith("##"):
                    break
            section_lines.append(line)

    if section_lines:
        return "\n".join(section_lines).strip()

    # Try explicit anchor syntax {#anchor-name}
    for i, line in enumerate(lines):
        if f"{{#{anchor}}}" in line or f"{{#{anchor_slug}}}" in line:
            # Return the line and following content until next heading
            fragment_lines = [line]
            for j in range(i + 1, len(lines)):
                if lines[j].startswith("#"):
                    break
                fragment_lines.append(lines[j])
            return "\n".join(fragment_lines).strip()

    return None


def upsert_fragment(
    project_id: int,
    src: str,
    anchor: str,
    content: str | None = None,
    filepath: pathlib.Path | None = None,
) -> str:
    """
    Upsert a document fragment into control.doc_fragment.
    Returns the fragment ID (UUID as string).
    """
    if psycopg is None:
        raise RuntimeError("psycopg not available")

    if content is None:
        if filepath is None:
            raise ValueError("Either content or filepath must be provided")
        content = filepath.read_text(encoding="utf-8")
        if anchor:
            fragment_content = resolve_anchor(content, anchor)
            if fragment_content is None:
                raise ValueError(f"Anchor '{anchor}' not found in {src}")
            content = fragment_content

    sha256_hash = compute_sha256(content)

    dsn = get_rw_dsn()
    if not dsn:
        raise RuntimeError("GEMATRIA_DSN not set")

    with psycopg.connect(dsn) as conn, conn.cursor() as cur:
        # Check if fragment exists
        cur.execute(
            """
            SELECT id FROM control.doc_fragment
            WHERE project_id = %s AND src = %s AND anchor = %s
            """,
            (project_id, src, anchor),
        )
        existing = cur.fetchone()

        if existing:
            # Update if hash changed
            cur.execute(
                """
                UPDATE control.doc_fragment
                SET sha256 = %s
                WHERE project_id = %s AND src = %s AND anchor = %s
                RETURNING id
                """,
                (sha256_hash, project_id, src, anchor),
            )
            fragment_id = cur.fetchone()[0]
        else:
            # Insert new
            cur.execute(
                """
                INSERT INTO control.doc_fragment (project_id, src, anchor, sha256)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """,
                (project_id, src, anchor, sha256_hash),
            )
            fragment_id = cur.fetchone()[0]

        conn.commit()
        return str(fragment_id)


def verify_fragment(project_id: int, src: str, anchor: str, expected_sha256: str) -> bool:
    """Verify a fragment's SHA256 hash matches expected value."""
    if psycopg is None:
        return False

    dsn = get_rw_dsn()
    if not dsn:
        return False

    try:
        with psycopg.connect(dsn) as conn, conn.cursor() as cur:
            cur.execute(
                """
                SELECT sha256 FROM control.doc_fragment
                WHERE project_id = %s AND src = %s AND anchor = %s
                """,
                (project_id, src, anchor),
            )
            row = cur.fetchone()
            if row is None:
                return False
            return row[0] == expected_sha256
    except Exception:
        return False


def get_required_fragments() -> List[Tuple[str, str]]:
    """
    Get list of required document fragments for PoR.
    Returns list of (src, anchor) tuples.
    """
    return [
        ("AGENTS.md", "Gatekeeper/execution behavior section"),
        ("RULES_INDEX.md", "Triad 050/051/052 + DSN/SSOT basics"),
        ("docs/guarded_tool_calls_full_design.md", "Core contracts"),
    ]
