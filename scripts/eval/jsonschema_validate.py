#!/usr/bin/env python3
from __future__ import annotations

import argparse
import glob
import json
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any

"""
Hermetic SSOT JSON validation (no network, no pip).
Supports a pragmatic subset of JSON Schema:
 - type: object/array/string/number/integer/boolean/null (or union list)
 - required: [keys]
 - properties: { key: {type, properties, required, items, enum, minimum, maximum} }
 - items: {type, properties, required, enum, minimum, maximum}
 - enum, minimum, maximum
Globs in --instance are expanded; non-matches are skipped with a HINT (no failure).
"""


def _load_json(p: Path) -> Any:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        raise SystemExit(f"[schema] FAIL: cannot parse JSON: {p} -> {e}") from e


def _is_type(val: Any, type_decl: Any) -> bool:
    def check_one(t: str) -> bool:
        if t == "object":
            return isinstance(val, dict)
        if t == "array":
            return isinstance(val, list)
        if t == "string":
            return isinstance(val, str)
        if t == "number":
            return isinstance(val, int | float) and not isinstance(val, bool)
        if t == "integer":
            return isinstance(val, int) and not isinstance(val, bool)
        if t == "boolean":
            return isinstance(val, bool)
        if t == "null":
            return val is None
        return True  # unknown -> don't fail

    if isinstance(type_decl, list):
        return any(check_one(t) for t in type_decl)
    if isinstance(type_decl, str):
        return check_one(type_decl)
    return True


def _validate(instance: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    errs: list[str] = []
    t = schema.get("type")
    if t and not _is_type(instance, t):
        errs.append(f"{path}: expected type {t}, got {type(instance).__name__}")
        return errs
    if "enum" in schema and instance not in schema["enum"]:
        errs.append(f"{path}: value {instance!r} not in enum {schema['enum']}")
    if isinstance(instance, int | float) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errs.append(f"{path}: {instance} < minimum {schema['minimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            errs.append(f"{path}: {instance} > maximum {schema['maximum']}")
    if isinstance(instance, dict):
        req = schema.get("required", [])
        for k in req:
            if k not in instance:
                errs.append(f"{path}: missing required key {k!r}")
        props = schema.get("properties", {})
        for k, sub in props.items():
            if k in instance:
                errs.extend(_validate(instance[k], sub, f"{path}.{k}"))
    if isinstance(instance, list):
        items = schema.get("items")
        if isinstance(items, dict):
            for i, el in enumerate(instance):
                errs.extend(_validate(el, items, f"{path}[{i}]"))
    return errs


def _expand_instances(args: Iterable[str]) -> list[Path]:
    out: list[Path] = []
    for pat in args:
        matches = [Path(p) for p in glob.glob(pat)]
        if not matches:
            print(f"HINT: no matches for pattern {pat!r}; skipping", file=sys.stderr)
            continue
        out.extend(matches)
    # de-dup
    uniq: dict[str, Path] = {str(p): p for p in out}
    return list(uniq.values())


def validate_one(instance_path: Path, schema_path: Path) -> list[str]:
    inst = _load_json(instance_path)
    schema = _load_json(schema_path)
    return _validate(inst, schema, str(instance_path))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--schema", required=True, help="Path to schema JSON file")
    ap.add_argument(
        "--instance", required=True, nargs="+", help="JSON instances (glob ok)"
    )
    args = ap.parse_args()
    schema_path = Path(args.schema)

    inst_paths = _expand_instances(args.instance)
    if not inst_paths:
        print("HINT: no instance files found; treating as pass (nothing to validate)")
        print(f"[schema] OK: 0 file(s) valid against {schema_path.name}")
        raise SystemExit(0)

    errs_total: list[str] = []
    for ip in inst_paths:
        errs_total.extend(validate_one(ip, schema_path))
    if errs_total:
        print("[schema] Validation errors:")
        for line in errs_total:
            print(" -", line)
        raise SystemExit(2)
    print(f"[schema] OK: {len(inst_paths)} file(s) valid against {schema_path.name}")


if __name__ == "__main__":
    main()
