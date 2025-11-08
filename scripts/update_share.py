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
import shutil
import sys
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "docs" / "SSOT" / "SHARE_MANIFEST.json"
SHARE = ROOT / "share"


def ensure_dir(p: Path):
    p.parent.mkdir(parents=True, exist_ok=True)


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
        return True  # File was copied
    return False  # File was unchanged


def head_json(src: Path, dst: Path, max_bytes: int) -> bool:
    ensure_dir(dst)
    if not src.exists():
        content = json.dumps({"preview_head": ""})
        if not dst.exists() or dst.read_text() != content:
            dst.write_text(content)
            return True
        return False

    data = src.read_bytes()[:max_bytes]
    text = data.decode("utf-8", errors="ignore")

    # Try full JSON first
    try:
        json.loads(text)
        if not dst.exists() or dst.read_text() != text:
            dst.write_text(text)
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
                return True
            return False
        except Exception:
            continue

    # Fallback: preview wrapper
    content = json.dumps({"preview_head": text})
    if not dst.exists() or dst.read_text() != content:
        dst.write_text(content)
        return True
    return False


def main():
    if not MANIFEST.exists():
        print(f"[update_share] Missing manifest: {MANIFEST}", file=sys.stderr)
        sys.exit(2)

    spec = json.loads(MANIFEST.read_text())
    items = spec.get("items", [])
    # Optional safety: enforce low file count
    if len(items) > 25:
        print("[update_share] ERROR: more than 25 items; trim manifest.", file=sys.stderr)
        sys.exit(2)

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

        if gen == "head_json":
            src = ROOT / src_rel
            if head_json(src, dst, max_bytes):
                copied_count += 1
                changed_files.append(str(dst.relative_to(ROOT)))
            continue

        if not src_rel:
            print(f"[update_share] Missing 'src' for item: {it}", file=sys.stderr)
            sys.exit(2)

        src = ROOT / src_rel
        if not src.exists():
            print(f"[update_share] ERROR: source not found: {src}", file=sys.stderr)
            sys.exit(2)

        if copy_file(src, dst):
            copied_count += 1
            changed_files.append(str(dst.relative_to(ROOT)))

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
