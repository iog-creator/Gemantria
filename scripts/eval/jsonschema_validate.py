#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

Json = dict | list | str | int | float | bool | None


def _load_json(p: Path) -> Json:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        raise SystemExit(f"[schema] FAIL: cannot parse JSON: {p} -> {e}") from e


def _type_ok(value: Any, t: str | list[str]) -> bool:
    def one(v: Any, name: str) -> bool:
        return (
            (name == "object" and isinstance(v, dict))
            or (name == "array" and isinstance(v, list))
            or (name == "string" and isinstance(v, str))
            or (name == "number" and isinstance(v, int | float) and not isinstance(v, bool))
            or (name == "integer" and isinstance(v, int) and not isinstance(v, bool))
            or (name == "boolean" and isinstance(v, bool))
            or (name == "null" and v is None)
        )

    if isinstance(t, list):
        return any(one(value, n) for n in t)
    return one(value, t)


def _validate(instance: Json, schema: dict[str, Any], path: list[str | int], errs: list[str]) -> None:
    # type
    if "type" in schema and not _type_ok(instance, schema["type"]):
        errs.append(f"{_loc(path)}: expected type {schema['type']}, got {type(instance).__name__}")
        return  # further checks depend on type

    # enum
    if "enum" in schema and instance not in schema["enum"]:
        errs.append(f"{_loc(path)}: value {instance!r} not in enum {schema['enum']}")

    # number/minimum/maximum
    if isinstance(instance, int | float) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errs.append(f"{_loc(path)}: {instance} < minimum {schema['minimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            errs.append(f"{_loc(path)}: {instance} > maximum {schema['maximum']}")

    # object
    if isinstance(instance, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in instance:
                errs.append(f"{_loc(path)}: missing required property '{key}'")
        props = schema.get("properties", {})
        for k, v in instance.items():
            if k in props:
                _validate(v, props[k], [*path, k], errs)

    # array
    if isinstance(instance, list):
        items = schema.get("items")
        if isinstance(items, dict):
            for i, v in enumerate(instance):
                _validate(v, items, [*path, i], errs)


def _loc(path: list[str | int]) -> str:
    return "/" + "/".join(str(x) for x in path) if path else "$"


def validate_one(instance_path: Path, schema_path: Path) -> list[str]:
    instance = _load_json(instance_path)
    schema_raw = _load_json(schema_path)
    if not isinstance(schema_raw, dict):
        return [f"[schema] FAIL: schema must be an object, got {type(schema_raw).__name__}"]
    schema: dict[str, Any] = schema_raw
    errs: list[str] = []
    _validate(instance, schema, [], errs)
    return errs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--schema", required=True)
    ap.add_argument("--instance", required=True, nargs="+")
    args = ap.parse_args()

    schema_path = Path(args.schema)
    errs_total: list[str] = []
    for ip in args.instance:
        errs_total.extend(validate_one(Path(ip), schema_path))

    if errs_total:
        print("[schema] Validation errors:")
        for line in errs_total:
            print(" -", line)
        return 2
    print(f"[schema] OK: {len(args.instance)} file(s) valid against {schema_path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
