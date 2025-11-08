# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
import json
import sys
from pathlib import Path

try:
    from jsonschema import ValidationError, validate
except Exception:
    print(
        "[goldens.enrichment] install jsonschema: pip install jsonschema",
        file=sys.stderr,
    )
    sys.exit(2)

SCHEMA = json.loads(Path("examples/enrichment/enrichment_row.schema.json").read_text(encoding="utf-8"))
GOLDEN = Path("examples/enrichment/golden_enrichment.jsonl")  # your current golden


def main():
    if not GOLDEN.exists():
        print(f"[goldens.enrichment] missing {GOLDEN}", file=sys.stderr)
        return 2
    bad = 0
    ok = 0
    for i, line in enumerate(GOLDEN.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            validate(json.loads(line), SCHEMA)
            ok += 1
        except ValidationError as e:
            print(f"[goldens.enrichment] FAIL line {i}: {e.message}")
            bad += 1
    if bad:
        print(f"[goldens.enrichment] {bad} invalid / {ok} valid")
        return 1
    print(f"[goldens.enrichment] OK ({ok} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
