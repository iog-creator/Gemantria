#!/usr/bin/env python3

import argparse
import fnmatch
import glob
import json
import os
import subprocess
import sys


DEFAULT_EXCLUDES = [
    "sample",
    "samples",
    "fixture",
    "fixtures",
    "guard",
    "golden",
    "demo",
    "test",
    "tests",
]
EXCLUDE_SUFFIXES = (".schema.json",)
EXCLUDE_PATH_HINTS = ("docs/SSOT/",)


def is_tag_build():
    # CI-friendly tag detection (GitHub/Git)
    if os.getenv("GITHUB_REF_TYPE") == "tag":
        return True
    try:
        out = subprocess.run(
            ["git", "describe", "--exact-match", "--tags"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=False,
        )
        return out.returncode == 0 and out.stdout.strip() != ""
    except Exception:
        return False


def find_first(name):
    # Search repo for a file with the given basename
    for root, _, files in os.walk("."):
        if name in files:
            return os.path.join(root, name)
    return None


def load_json_candidates(path):
    # Accept normal JSON or JSON Lines (best-effort)
    with open(path, encoding="utf-8") as f:
        txt = f.read().strip()
    # Try JSON first
    try:
        obj = json.loads(txt)
        return [obj]
    except Exception:
        pass
    # Try JSONL
    items = []
    for i, line in enumerate(txt.splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            items.append(json.loads(line))
        except Exception as e:
            # not valid JSONL
            return None
    return items if items else None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--name", required=True)  # logical guard name
    p.add_argument("--schema-name", required=True)  # filename to search for
    p.add_argument("--data-glob", action="append", default=[])
    p.add_argument("--filename-contains", action="append", default=[])
    p.add_argument("--exclude-glob", action="append", default=[])
    p.add_argument("--exclude-contains", action="append", default=[])
    p.add_argument(
        "--allow-empty",
        action="store_true",
        help="Allow PASS when no data files match (non-tag simulation only).",
    )
    args = p.parse_args()

    strict_env = os.getenv("STRICT_GUARDS", "0") in ("1", "true", "TRUE")
    strict = strict_env or is_tag_build()

    # Resolve schema path
    schema_path = find_first(args.schema_name)
    exists = {"schema_found": bool(schema_path), "data_files": []}
    notes = []
    errors = []
    files_checked = 0

    # Try importing jsonschema (soft dep)
    try:
        import jsonschema  # type: ignore

        have_jsonschema = True
    except Exception:
        have_jsonschema = False
        notes.append("jsonschema module not available")

    # Collect candidate data files
    candidates = []
    for g in args.data_glob or []:
        candidates.extend(glob.glob(g, recursive=True))

    # Optional filename filters
    if args.filename_contains:

        def keep(p):
            s = p.lower()
            return any(substr.lower() in s for substr in args.filename_contains)

        candidates = list(filter(keep, candidates))

    # Exclusions: default substrings + user-provided + schema files + docs/SSOT
    exclude_contains = set(x.lower() for x in DEFAULT_EXCLUDES + list(args.exclude_contains or []))
    exclude_globs = list(args.exclude_glob or [])

    def excluded(path: str) -> bool:
        low = path.lower()
        if any(hint in path for hint in EXCLUDE_PATH_HINTS):
            return True
        if any(low.endswith(suf) for suf in EXCLUDE_SUFFIXES):
            return True
        if any(sub in low for sub in exclude_contains):
            return True
        for pat in exclude_globs:
            if fnmatch.fnmatch(path, pat):
                return True
        return False

    # Deduplicate and only existing files, excluding schema files and docs/SSOT
    candidates = sorted({c for c in candidates if os.path.isfile(c) and not excluded(c)})
    exists["data_files"] = candidates
    exists["excludes"] = {
        "contains": sorted(list(exclude_contains)),
        "globs": exclude_globs,
        "suffixes": EXCLUDE_SUFFIXES,
        "path_hints": EXCLUDE_PATH_HINTS,
    }

    ok = True
    if not schema_path:
        ok = False if strict else True
        notes.append("schema not found: " + args.schema_name)

    # Handle empty-match policy:
    # - Tag builds always require data (FAIL if empty)
    # - Non-tag STRICT simulations may pass if --allow-empty is set
    if not candidates:
        if is_tag_build():
            ok = False
            notes.append("tag build requires data; no matching files")
        elif args.allow_empty:
            ok = True and ok
            notes.append("allow-empty: no matching data files (non-tag)")
        else:
            ok = ok and (not strict)
            if strict and ok:  # if previously false, keep false
                ok = False
            notes.append("no matching data files after excludes")

    if have_jsonschema and schema_path and candidates:
        with open(schema_path, encoding="utf-8") as f:
            schema = json.load(f)
        v = jsonschema.Draft202012Validator(schema)
        for path in candidates:
            items = load_json_candidates(path)
            if items is None:
                errors.append({"file": path, "error": "invalid JSON/JSONL"})
                ok = False
                continue
            for idx, obj in enumerate(items):
                errs = sorted(v.iter_errors(obj), key=lambda e: e.path)
                if errs:
                    ok = False
                    errors.append(
                        {
                            "file": path,
                            "idx": idx,
                            "message": errs[0].message,
                            "at": list(errs[0].path),
                        }
                    )
            files_checked += 1
    else:
        if strict and schema_path and not candidates and not args.allow_empty and not is_tag_build():
            ok = False

    out = {
        "guard": args.name,
        "strict": bool(strict),
        "ok": bool(ok),
        "exists": exists,
        "stats": {"files_checked": files_checked},
        "notes": notes,
        "errors": errors[:5],
    }
    print(json.dumps(out, indent=2))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
