#!/usr/bin/env python3
import json
import sys
from pathlib import Path

try:
    from jsonschema import ValidationError, validate
except Exception:
    print("[sample.check] install jsonschema: pip install jsonschema", file=sys.stderr)
    sys.exit(2)

SCHEMA = json.loads(Path("examples/enrichment/enrichment_row.schema.json").read_text(encoding="utf-8"))


def latest_sample():
    # prefer real run logs; look for JSONL enrichment output files
    cands = []
    for base in ("logs/book", "logs/probes"):
        p = Path(base)
        if p.exists():
            # Look for .out files (enrichment output) and .jsonl files
            cands += sorted(p.glob("*.out")) + sorted(p.glob("*.jsonl"))
    return cands[-1] if cands else None


def extract_enrichment_from_logs(log_text: str) -> list[dict]:
    """Extract enrichment records from log files."""
    rows = []
    for line in log_text.splitlines():
        line = line.strip()
        if not line.startswith('{"level": "INFO"'):
            continue
        try:
            log_entry = json.loads(line)
            if log_entry.get("logger") == "gemantria.enrichment" and log_entry.get("msg") == "noun_enriched":
                # Convert log entry to enrichment row format
                row = {
                    "hebrew": log_entry.get("noun", ""),
                    "name": log_entry.get("noun", ""),
                    "confidence": log_entry.get("confidence", 0.0),
                    "insights": "",  # Log doesn't contain full insights, just metadata
                    "tokens": log_entry.get("tokens", 0),
                    "source": "lm",
                }
                rows.append(row)
        except json.JSONDecodeError:
            continue
    return rows


def main():
    p = latest_sample()
    if not p:
        print("[sample.check] no sample found in logs/", file=sys.stderr)
        return 2
    print(f"[sample.check] validating {p}")
    txt = p.read_text(encoding="utf-8")

    # Parse based on file type
    if p.suffix == ".out":
        # Extract enrichment records from log files
        rows = extract_enrichment_from_logs(txt)
    elif p.suffix == ".jsonl":
        # Parse JSONL format
        rows = [json.loads(line) for line in txt.splitlines() if line.strip()]
    else:
        # Single JSON file
        rows = [json.loads(txt)]

    if not rows:
        print(f"[sample.check] no enrichment records found in {p}", file=sys.stderr)
        return 2

    bad = 0
    ok = 0
    for i, row in enumerate(rows, 1):
        try:
            validate(row, SCHEMA)
            ok += 1
        except ValidationError as e:
            print(f"[sample.check] FAIL {p}:{i} → {e.message}")
            bad += 1
    if bad:
        print(f"[sample.check] {bad} invalid / {ok} valid")
        return 1
    print(f"[sample.check] OK ({ok} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
