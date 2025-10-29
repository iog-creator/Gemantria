#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def load_json(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        raise SystemExit(f"[schema] FAIL: cannot parse JSON: {p} -> {e}") from e


def validate_one(instance_path: Path, schema_path: Path) -> list[str]:
    # Lazy import so script works even if jsonschema is not installed locally.
    try:
        import jsonschema
    except ImportError:
        print("[schema] Installing jsonschema for this run...", file=sys.stderr)
        # Local runs might not have it; CI will pre-install. Do a best-effort here.
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "jsonschema>=4.21,<5"]
        )
        import jsonschema

    instance = load_json(instance_path)
    schema = load_json(schema_path)
    validator = jsonschema.Draft202012Validator(schema)
    errors = []
    for err in sorted(validator.iter_errors(instance), key=lambda e: e.path):
        loc = "/".join(str(x) for x in err.path) or "$"
        errors.append(f"{instance_path}: {loc}: {err.message}")
    return errors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--schema", required=True, help="Path to schema JSON file")
    ap.add_argument(
        "--instance", required=True, nargs="+", help="Paths to instance JSON files"
    )
    args = ap.parse_args()

    schema_path = Path(args.schema)
    errs_total: list[str] = []
    for ip in args.instance:
        errs_total.extend(validate_one(Path(ip), schema_path))

    if errs_total:
        print("[schema] Validation errors:")
        for line in errs_total:
            print(" -", line)
        raise SystemExit(2)
    print(f"[schema] OK: {len(args.instance)} file(s) valid against {schema_path.name}")


if __name__ == "__main__":
    main()
