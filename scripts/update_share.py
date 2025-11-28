# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
"""
update_share.py — refresh a flat share/ folder with current canonical files.

CRITICAL BEHAVIOR:
- share/ contains ONLY the files specified in SHARE_MANIFEST.json (flat, no subdirectories)
- All subdirectories and files not in manifest are REMOVED on each sync
- Files are generated fresh from Postgres when needed (e.g., pm.snapshot.md)
- This ensures share/ is a clean, flat directory ready for PM handoff

SYNC PROCESS:
1. Reads docs/SSOT/SHARE_MANIFEST.json
2. REMOVES all subdirectories and files not in manifest
3. Copies/overwrites each manifest item into share/ (flat layout only)
4. For large JSON exports, writes a small head preview as valid JSON when possible
5. Reports which files were changed
6. Exits nonzero if files were changed (useful for CI/change detection)

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
    from scripts.config.env import get_rw_dsn

    GEMATRIA_DSN = get_rw_dsn()
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
        print(
            f"HINT: share.tracking: Database tracking failed (hermetic behavior): {e}",
            file=sys.stderr,
        )


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
        print(
            f"HINT: share.tracking: Database metadata tracking failed (hermetic behavior): {e}",
            file=sys.stderr,
        )


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
    content_changed = files_differ(src, dst)
    if content_changed or not dst.exists():
        shutil.copy2(src, dst)
    # Always update mtime to current time so sync timestamp is visible (even if content unchanged)
    # This ensures git sees the timestamp change for all synced files
    current_time = time.time()
    os.utime(dst, (current_time, current_time))
    return content_changed  # Return True if content changed, False if only timestamp updated


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

    # Enforce 40-item limit on manifest count (per PM requirement)
    MAX_MANIFEST_ITEMS = 40
    if len(items) > MAX_MANIFEST_ITEMS:
        print(
            f"[update_share] ERROR: Manifest has {len(items)} items (max {MAX_MANIFEST_ITEMS}); trim manifest.",
            file=sys.stderr,
        )
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

    # CLEANUP: Remove all subdirectories and files not in manifest
    # This ensures share/ contains ONLY the files specified in the manifest
    manifest_dst_paths = {ROOT / it.get("dst") for it in items if it.get("dst")}
    manifest_dst_paths.add(SHARE / "SHARE_MANIFEST.json")  # Keep manifest itself

    # Remove all subdirectories
    for item in SHARE.iterdir():
        if item.is_dir():
            print(f"[update_share] Removing subdirectory: {item.relative_to(ROOT)}")
            shutil.rmtree(item)
        elif item.is_file() and item not in manifest_dst_paths:
            # Remove files not in manifest
            print(f"[update_share] Removing file not in manifest: {item.relative_to(ROOT)}")
            item.unlink()

    copied_count = 0
    timestamp_updated_count = 0
    total_count = 0
    changed_files = []
    timestamp_updated_files = []

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
        content_changed = copy_file(src, dst)
        # Always update timestamp (copy_file does this), so track it
        timestamp_updated_count += 1
        timestamp_updated_files.append(str(dst.relative_to(ROOT)))

        if content_changed:
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

    if copied_count == 0:
        print(
            f"[update_share] OK — share/ refreshed ({timestamp_updated_count}/{total_count} files synced, timestamps updated)"
        )
    else:
        print(
            f"[update_share] OK — share/ refreshed ({copied_count}/{total_count} files with content changes, {timestamp_updated_count}/{total_count} timestamps updated)"
        )
        print("[update_share] CHANGED FILES:")
        for f in changed_files:
            print(f"  - {f}")

    # Return exit code based on whether files were changed (useful for CI)
    return copied_count > 0


if __name__ == "__main__":
    # Exit with code indicating if files were changed
    changed = main()
    sys.exit(0 if not changed else 1)
