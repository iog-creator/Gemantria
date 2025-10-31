#!/usr/bin/env python3
import json
import pathlib
import sys

from jsonschema import Draft202012Validator, validate

ROOT = pathlib.Path(__file__).resolve().parents[2]
EVAL = ROOT / "share" / "eval"
SC = ROOT / "scripts" / "eval" / "schemas"


def _check(path: pathlib.Path, schema_name: str) -> int:
    schema = json.loads((SC / schema_name).read_text(encoding="utf-8"))
    data = json.loads(path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validate(instance=data, schema=schema)
    print(f"[schema] OK: {path.relative_to(ROOT)} ~ {schema_name}")
    return 0


def main() -> int:
    rc = 0
    try:
        rc |= _check(EVAL / "graph_latest.json", "graph_latest.schema.json")
    except Exception as e:
        print("[schema] FAIL graph_latest.json:", e)
        rc |= 1
    try:
        rc |= _check(EVAL / "centrality.json", "centrality.schema.json")
    except Exception as e:
        print("[schema] FAIL centrality.json:", e)
        rc |= 1
    try:
        rc |= _check(EVAL / "release_manifest.json", "release_manifest.schema.json")
    except Exception as e:
        print("[schema] FAIL release_manifest.json:", e)
        rc |= 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
