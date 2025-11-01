#!/usr/bin/env python3

import json, os, glob


def size(p):
    try:
        return os.path.getsize(p)
    except OSError:
        return 0


def main():
    # Only validate when outputs exist and are non-empty (hermetic CI)
    files = glob.glob("exports/**/*.json*", recursive=True) + glob.glob("exports/**/*.csv", recursive=True)
    files = [f for f in files if size(f) > 0]
    if not files:
        print("[validate] no exports found; skip (empty DB tolerated)")
        return 0

    # Lightweight JSON sanity (schema-level checks can be added here if needed)
    ok = True
    for f in files:
        if f.endswith((".json", ".jsonl", ".ndjson")):
            try:
                with open(f, encoding="utf-8") as fh:
                    head = fh.read(2048)
                    json.loads(head if not f.endswith(".jsonl") else "[" + ",".join(head.splitlines()[:5]) + "]")
            except Exception as e:
                ok = False
                print(f"[validate] JSON parse error in {f}: {e}")

    if not ok:
        return 2

    print(f"[validate] checked {len(files)} file(s); OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
