#!/usr/bin/env python3

import json, sys
from pathlib import Path

SCHEMA_PATH = Path("configs/strongs_class_overrides.schema.json")
OVERRIDES_PATH = Path("configs/strongs_class_overrides.json")


def die(msg, code=2):
    print(msg, file=sys.stderr)
    sys.exit(code)


try:
    import jsonschema
except Exception:
    die("ERROR: jsonschema not installed; add it to dev deps.", 2)

if not SCHEMA_PATH.exists():
    die(f"ERROR: missing {SCHEMA_PATH}", 2)

if not OVERRIDES_PATH.exists():
    print("OK: overrides file absent (optional).")
    sys.exit(0)

schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
data = json.loads(OVERRIDES_PATH.read_text(encoding="utf-8"))

try:
    jsonschema.validate(data, schema)
except jsonschema.ValidationError as e:
    die(f"ERROR: overrides invalid: {e.message}", 2)

print("OK: strongs_class_overrides.json valid.")
