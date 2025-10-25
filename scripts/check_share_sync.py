#!/usr/bin/env python3
"""
check_share_sync.py — verify a flat share/ folder is up-to-date.

- Reads share/SHARE_MANIFEST.json
- For non-generated items: compares byte-for-byte (sha256) and mtime freshness
- For head_json item: asserts share file exists, <= max_bytes, non-empty
- Fails fast with a clear message if any check fails
"""

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "share" / "SHARE_MANIFEST.json"


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def fail(msg: str):
    print(f"[share.check] FAIL: {msg}", file=sys.stderr)
    sys.exit(2)


def main():
    if not MANIFEST.exists():
        fail(f"Missing manifest: {MANIFEST}")

    spec = json.loads(MANIFEST.read_text())
    items = spec.get("items", [])
    if not items:
        fail("Manifest has no items.")

    for it in items:
        src_rel = it.get("src")
        dst_rel = it.get("dst")
        gen = it.get("generate")
        max_bytes = int(it.get("max_bytes", 4096))

        if not dst_rel:
            fail(f"Item missing 'dst': {it}")

        dst = ROOT / dst_rel
        if gen == "head_json":
            # Head preview must exist, be <= max_bytes, and non-empty
            if not dst.exists():
                fail(f"Missing head preview in share/: {dst_rel}")
            size = dst.stat().st_size
            if size == 0:
                fail(f"Head preview is empty: {dst_rel}")
            if size > max_bytes:
                fail(
                    f"Head preview exceeds max_bytes ({size} > {max_bytes}): {dst_rel}"
                )
            continue

        if not src_rel:
            fail(f"Item missing 'src': {it}")

        src = ROOT / src_rel
        if not src.exists():
            fail(f"Source missing: {src_rel}")

        if not dst.exists():
            fail(f"Share copy missing: {dst_rel}")

        # Must be byte-identical and at least as new as source
        if sha256(src) != sha256(dst):
            fail(f"Content mismatch: {src_rel} -> {dst_rel} (run `make share.refresh`)")

        if dst.stat().st_mtime < src.stat().st_mtime:
            fail(
                f"Share copy is older than source: {dst_rel} (run `make share.refresh`)"
            )

    print("[share.check] PASS — share/ is flat and current")


if __name__ == "__main__":
    main()
