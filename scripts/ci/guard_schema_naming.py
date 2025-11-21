import json, sys, pathlib

root = pathlib.Path("schemas")

ids = []

errors = []

# Check all JSON Schema files (*.schema.json) under schemas/ (root + subdirs)
for p in root.rglob("*.schema.json"):
    data = json.load(open(p))
    path = p.as_posix()
    top = data
    # Checks
    if "$id" not in top:
        errors.append(f"{path}: missing $id")
    else:
        _id = top["$id"]
        if not _id.startswith("gemantria://v1/"):
            errors.append(f"{path}: $id must start with gemantria://v1/ (got {_id})")
    if "title" not in top or not str(top["title"]).strip():
        errors.append(f"{path}: missing or empty title")
    if top.get("type") != "object":
        # We enforce object at top-level for tool IO/common
        errors.append(f"{path}: top-level type must be 'object'")
    if top.get("additionalProperties", None) is not False:
        errors.append(f"{path}: top-level additionalProperties must be false")
    ids.append((path, top.get("$id")))

ok = not errors

out = {"ok": ok, "errors": errors, "count": len(ids)}

print(json.dumps(out, indent=2))

sys.exit(0 if ok else 1)
