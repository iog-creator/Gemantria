# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3

"""

Temporal validation adapter (reuse-first).

- Reads existing exports/** (json/jsonl/ndjson).

- If SSOT schemas (e.g., schemas/SSOT_temporal-patterns.schema.json) exist, run light checks.

- If no exports or schemas, exit 0 with a clear skip line (hermetic-friendly).

"""

import os, json, glob

SSOT_DIR = os.getenv("SSOT_DIR", "schemas")

CAND_EXPORTS = glob.glob("exports/**/*.json*", recursive=True)


def head_json(path, limit=200):
    try:
        with open(path, encoding="utf-8") as fh:
            if path.endswith((".jsonl", ".ndjson")):
                return [json.loads(x) for x in fh.readlines()[:limit] if x.strip()]
            return json.load(fh)
    except Exception as e:
        print(f"[temporal.validate] skip {path}: {e}")
        return None


def looks_temporal(obj):
    # heuristic: presence of time-like keys
    KEYS = {"ts", "timestamp", "date", "datetime", "period", "year", "month", "day"}
    if isinstance(obj, dict):
        keys = set(k.lower() for k in obj.keys())
        return bool(KEYS & keys)
    if isinstance(obj, list) and obj and isinstance(obj[0], dict):
        keys = set(k.lower() for k in obj[0].keys())
        return bool(KEYS & keys)
    return False


def main():
    if not CAND_EXPORTS:
        print("[temporal.validate] no exports found; skip (empty DB tolerated)")
        return 0
    temporal_files = []
    for p in CAND_EXPORTS:
        obj = head_json(p)
        if obj is not None and looks_temporal(obj):
            temporal_files.append(p)
    if not temporal_files:
        print("[temporal.validate] no temporal-looking exports; skip")
        return 0

    # SSOT schema hint (optional)
    ssot_files = glob.glob(os.path.join(SSOT_DIR, "SSOT_*temporal*.schema.json"))
    if not ssot_files:
        print("[temporal.validate] SSOT schemas not found; heuristic-only validation OK")
        print(f"[temporal.validate] checked {len(temporal_files)} file(s); OK")
        return 0

    # lightweight checks against expected keys (no strict jsonschema to avoid deps)
    required_any = [{"period", "value"}, {"date", "count"}, {"timestamp", "value"}]
    ok = True
    for p in temporal_files:
        obj = head_json(p)
        rows = obj if isinstance(obj, list) else [obj]
        sample = rows[0] if rows and isinstance(rows[0], dict) else {}
        if not any(req.issubset(set(k.lower() for k in sample.keys())) for req in required_any):
            ok = False
            print(f"[temporal.validate] WARN: {p} missing expected temporal keys in first record")
    print(f"[temporal.validate] checked {len(temporal_files)} file(s); {'OK' if ok else 'WARN'}")
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
