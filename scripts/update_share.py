#!/usr/bin/env python3
"""
update_share.py — refresh a flat share/ folder with current canonical files.

- Reads share/SHARE_MANIFEST.json
- Copies/overwrites each item into share/ (flat)
- For large JSON exports, writes a small head preview as valid JSON when possible
- Exits nonzero on errors
"""

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "share" / "SHARE_MANIFEST.json"
SHARE = ROOT / "share"


def ensure_dir(p: Path):
    p.parent.mkdir(parents=True, exist_ok=True)


def copy_file(src: Path, dst: Path):
    ensure_dir(dst)
    shutil.copy2(src, dst)


def head_json(src: Path, dst: Path, max_bytes: int):
    ensure_dir(dst)
    if not src.exists():
        dst.write_text(json.dumps({"preview_head": ""}))
        return
    data = src.read_bytes()[:max_bytes]
    text = data.decode("utf-8", errors="ignore")
    # Try full JSON first
    try:
        json.loads(text)
        dst.write_text(text)
        return
    except Exception:
        pass
    # Try NDJSON first valid line
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            json.loads(line)
            dst.write_text(line + "\n")
            return
        except Exception:
            continue
    # Fallback: preview wrapper
    dst.write_text(json.dumps({"preview_head": text}))


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

    for it in items:
        src_rel = it.get("src")
        dst_rel = it.get("dst")
        gen = it.get("generate")
        max_bytes = int(it.get("max_bytes", 4096))

        if not dst_rel:
            print(f"[update_share] Missing 'dst' for item: {it}", file=sys.stderr)
            sys.exit(2)

        dst = ROOT / dst_rel

        if gen == "head_json":
            src = ROOT / src_rel
            head_json(src, dst, max_bytes)
            continue

        if not src_rel:
            print(f"[update_share] Missing 'src' for item: {it}", file=sys.stderr)
            sys.exit(2)

        src = ROOT / src_rel
        if not src.exists():
            print(f"[update_share] ERROR: source not found: {src}", file=sys.stderr)
            sys.exit(2)

        copy_file(src, dst)

    print("[update_share] OK — share/ refreshed (flat, overwritten)")


if __name__ == "__main__":
    main()
