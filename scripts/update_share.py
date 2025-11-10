# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
"""
update_share.py — refresh a flat share/ folder with current canonical files.

- Reads share/SHARE_MANIFEST.json
- Copies/overwrites each item into share/ (flat)
- For large JSON exports, writes a small head preview as valid JSON when possible
- Reports which files were changed
- Exits nonzero if files were changed (useful for CI/change detection)

USAGE:
  python scripts/update_share.py          # Sync and report changes
  make share.sync                        # Same via Makefile

HOUSEKEEPING CHANGE DETECTION:
  To see what changed since last housekeeping, run:
    make housekeeping 2>&1 | grep -A 50 "HOUSEKEEPING CHANGE LOG"
"""

import json
import os
import shutil
import sys
import hashlib
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "docs" / "SSOT" / "SHARE_MANIFEST.json"
SHARE = ROOT / "share"

# Database integration (optional - hermetic behavior per Rule 046)
try:
    import psycopg

    GEMATRIA_DSN = os.environ.get("GEMATRIA_DSN")
    DB_AVAILABLE = bool(GEMATRIA_DSN)
except ImportError:
    DB_AVAILABLE = False
    GEMATRIA_DSN = None


def ensure_dir(p: Path):
    p.parent.mkdir(parents=True, exist_ok=True)


def check_db_available() -> bool:
    """Check if database is available for tracking."""
    if not DB_AVAILABLE:
        return False
    try:
        with psycopg.connect(GEMATRIA_DSN, connect_timeout=2) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        return True
    except (psycopg.OperationalError, psycopg.Error):
        return False


def get_file_checksum(filepath: Path) -> str | None:
    """Calculate SHA-256 checksum of a file."""
    try:
        if not filepath.exists():
            return None
        with open(filepath, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception:
        return None


def track_share_item(
    item_id: str,
    src_path: str,
    dst_path: str,
    generate_type: str | None,
    max_bytes: int | None,
    checksum: str | None,
    src_checksum: str | None,
    sync_status: str,
    error_message: str | None = None,
):
    """Track share manifest item in database."""
    if not check_db_available():
        return

    try:
        with psycopg.connect(GEMATRIA_DSN) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT update_share_manifest_item(%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (
                        item_id,
                        src_path,
                        dst_path,
                        generate_type,
                        max_bytes,
                        checksum,
                        src_checksum,
                        sync_status,
                        error_message,
                    ),
                )
                conn.commit()
    except Exception as e:
        # Hermetic: don't fail if DB tracking fails
        print(f"HINT: share.tracking: Database tracking failed (hermetic behavior): {e}", file=sys.stderr)


def track_manifest_metadata(
    manifest_path: str,
    manifest_checksum: str,
    total_items: int,
    evidence_paths: list[str],
):
    """Track share manifest metadata in database."""
    if not check_db_available():
        return

    try:
        with psycopg.connect(GEMATRIA_DSN) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT update_share_manifest_metadata(%s, %s, %s, %s)",
                    (manifest_path, manifest_checksum, total_items, evidence_paths),
                )
                conn.commit()
    except Exception as e:
        # Hermetic: don't fail if DB tracking fails
        print(f"HINT: share.tracking: Database metadata tracking failed (hermetic behavior): {e}", file=sys.stderr)


def files_differ(src: Path, dst: Path) -> bool:
    """Check if source and destination files differ by comparing content hashes."""
    if not dst.exists():
        return True

    try:
        src_hash = hashlib.sha256(src.read_bytes()).hexdigest()
        dst_hash = hashlib.sha256(dst.read_bytes()).hexdigest()
        return src_hash != dst_hash
    except Exception:
        # If we can't read either file, assume they differ to be safe
        return True


def copy_file(src: Path, dst: Path):
    ensure_dir(dst)
    if files_differ(src, dst):
        shutil.copy2(src, dst)
        # Update mtime to current time so sync timestamp is visible
        current_time = time.time()
        os.utime(dst, (current_time, current_time))
        return True  # File was copied
    return False  # File was unchanged


def head_json(src: Path, dst: Path, max_bytes: int) -> bool:
    ensure_dir(dst)
    if not src.exists():
        content = json.dumps({"preview_head": ""})
        if not dst.exists() or dst.read_text() != content:
            dst.write_text(content)
            # Update mtime to current time so sync timestamp is visible
            current_time = time.time()
            os.utime(dst, (current_time, current_time))
            return True
        return False

    data = src.read_bytes()[:max_bytes]
    text = data.decode("utf-8", errors="ignore")

    # Try full JSON first
    try:
        json.loads(text)
        if not dst.exists() or dst.read_text() != text:
            dst.write_text(text)
            # Update mtime to current time so sync timestamp is visible
            current_time = time.time()
            os.utime(dst, (current_time, current_time))
            return True
        return False
    except Exception:
        pass

    # Try NDJSON first valid line
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            json.loads(line)
            content = line + "\n"
            if not dst.exists() or dst.read_text() != content:
                dst.write_text(content)
                # Update mtime to current time so sync timestamp is visible
                current_time = time.time()
                os.utime(dst, (current_time, current_time))
                return True
            return False
        except Exception:
            continue

    # Fallback: preview wrapper
    content = json.dumps({"preview_head": text})
    if not dst.exists() or dst.read_text() != content:
        dst.write_text(content)
        # Update mtime to current time so sync timestamp is visible
        current_time = time.time()
        os.utime(dst, (current_time, current_time))
        return True
    return False


def main():
    if not MANIFEST.exists():
        print(f"[update_share] Missing manifest: {MANIFEST}", file=sys.stderr)
        sys.exit(2)

    # Track manifest metadata
    manifest_content = MANIFEST.read_text()
    manifest_checksum = hashlib.sha256(manifest_content.encode()).hexdigest()
    spec = json.loads(manifest_content)
    items = spec.get("items", [])
    evidence_paths = spec.get("evidence", [])

    # Optional safety: enforce low file count
    if len(items) > 25:
        print("[update_share] ERROR: more than 25 items; trim manifest.", file=sys.stderr)
        sys.exit(2)

    # Track manifest metadata in database
    track_manifest_metadata(
        str(MANIFEST.relative_to(ROOT)),
        manifest_checksum,
        len(items),
        evidence_paths,
    )

    # Ensure share/ exists; **flat** layout only
    SHARE.mkdir(parents=True, exist_ok=True)

    copied_count = 0
    total_count = 0
    changed_files = []

    for it in items:
        src_rel = it.get("src")
        dst_rel = it.get("dst")
        gen = it.get("generate")
        max_bytes = int(it.get("max_bytes", 4096))

        if not dst_rel:
            print(f"[update_share] Missing 'dst' for item: {it}", file=sys.stderr)
            sys.exit(2)

        dst = ROOT / dst_rel
        total_count += 1

        # Generate unique item ID for tracking
        item_id = f"{src_rel}:{dst_rel}" if src_rel else dst_rel

        if gen == "head_json":
            src = ROOT / src_rel if src_rel else None
            if src and src.exists():
                src_checksum = get_file_checksum(src)
                if head_json(src, dst, max_bytes):
                    copied_count += 1
                    changed_files.append(str(dst.relative_to(ROOT)))
                    dst_checksum = get_file_checksum(dst)
                    track_share_item(
                        item_id,
                        src_rel or "",
                        dst_rel,
                        gen,
                        max_bytes,
                        dst_checksum,
                        src_checksum,
                        "synced",
                    )
                else:
                    # File unchanged, but still track
                    dst_checksum = get_file_checksum(dst)
                    track_share_item(
                        item_id,
                        src_rel or "",
                        dst_rel,
                        gen,
                        max_bytes,
                        dst_checksum,
                        src_checksum,
                        "synced",
                    )
            else:
                # Source missing
                track_share_item(
                    item_id,
                    src_rel or "",
                    dst_rel,
                    gen,
                    max_bytes,
                    None,
                    None,
                    "missing_source",
                    f"Source file not found: {src_rel}",
                )
            continue

        if not src_rel:
            print(f"[update_share] Missing 'src' for item: {it}", file=sys.stderr)
            sys.exit(2)

        src = ROOT / src_rel
        if not src.exists():
            print(f"[update_share] ERROR: source not found: {src}", file=sys.stderr)
            track_share_item(
                item_id,
                src_rel,
                dst_rel,
                None,
                None,
                None,
                None,
                "missing_source",
                f"Source file not found: {src_rel}",
            )
            continue

        src_checksum = get_file_checksum(src)
        if copy_file(src, dst):
            copied_count += 1
            changed_files.append(str(dst.relative_to(ROOT)))
            dst_checksum = get_file_checksum(dst)
            track_share_item(
                item_id,
                src_rel,
                dst_rel,
                None,
                None,
                dst_checksum,
                src_checksum,
                "synced",
            )
        else:
            # File unchanged, but still track
            dst_checksum = get_file_checksum(dst)
            track_share_item(
                item_id,
                src_rel,
                dst_rel,
                None,
                None,
                dst_checksum,
                src_checksum,
                "synced",
            )

    if copied_count == 0:
        print("[update_share] OK — share/ up to date (no changes)")
    else:
        print(f"[update_share] OK — share/ refreshed ({copied_count}/{total_count} files updated)")
        print("[update_share] CHANGED FILES:")
        for f in changed_files:
            print(f"  - {f}")

    # Return exit code based on whether files were changed (useful for CI)
    return copied_count > 0


if __name__ == "__main__":
    # Exit with code indicating if files were changed
    changed = main()
    sys.exit(0 if not changed else 1)
