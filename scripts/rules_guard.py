#!/usr/bin/env python3
"""
rules_guard.py — System-level enforcement so rules aren't just words.

Fail-closed if:
- Code changed without matching docs/AGENTS.md or ADR updates.
- Forest not refreshed (overview too old) unless ALLOW_OLD_FOREST=1 (never on CI).
- Required SSOT schemas missing or invalid JSON.
- PR template sections not present / unchecked (on CI via env vars).
- Evidence missing when stats/correlations/exports changed.

Spec linkage: ADR-013 doc sync; docs/README workflow; .cursor rule governance.
"""
import json
import os
import re
import subprocess
import sys
import time
from contextlib import suppress
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
SSOT = DOCS / "SSOT"
FOREST = DOCS / "forest"
ADR = DOCS / "ADRs"
CURSOR_RULES = ROOT / ".cursor" / "rules"

CI = os.environ.get("CI") == "true"
PR_BODY = os.environ.get("PR_BODY", "")
BASE_REF_ENV = os.environ.get("BASE_REF", "")


def sh(cmd: str) -> str:
    return subprocess.check_output(cmd, shell=True, text=True).strip()


def merge_base() -> str:
    # Prefer merge-base with origin/main for robust local/CI behavior
    with suppress(Exception):
        sh("git fetch -q origin +refs/remotes/origin/*:refs/remotes/origin/*")
    try:
        return sh("git merge-base origin/main HEAD")
    except Exception:
        return BASE_REF_ENV or "HEAD~1"


def changed_files() -> list[str]:
    try:
        staged = sh("git diff --name-only --cached").splitlines()
    except Exception:
        staged = []
    if staged:
        return staged
    base = merge_base()
    try:
        return sh(f"git diff --name-only {base}...HEAD").splitlines()
    except Exception:
        return []


def require(cond: bool, msg: str):
    if not cond:
        print(f"[rules_guard] FAIL: {msg}", file=sys.stderr)
        sys.exit(2)


def file_exists(p: Path) -> bool:
    return p.exists() and p.stat().st_size > 0


def load_json(p: Path):
    with p.open() as f:
        return json.load(f)


def validate_json_schema(instance_path: Path, schema_path: Path):
    try:
        from jsonschema import Draft202012Validator, validate

        instance = load_json(instance_path)
        schema = load_json(schema_path)
        Draft202012Validator.check_schema(schema)
        validate(instance=instance, schema=schema)
    except Exception as e:
        require(False, f"Schema validation failed for {instance_path}: {e}")


def main():
    files = changed_files()
    if not files:
        print("[rules_guard] PASS (no changes detected)")
        return

    code_dirs = ("src/", "scripts/", "migrations/", "webui/")

    code_touched = any(f.startswith(code_dirs) for f in files)
    docs_touched = any(
        f.startswith("docs/") or f.endswith("README.md") or f.endswith("AGENTS.md")
        for f in files
    )

    # 1) Doc sync if code touched
    if code_touched:
        require(
            docs_touched,
            "Code changed but no docs updated (AGENTS.md/ADR/SSOT/README). See docs workflow.",
        )

    # 2) ADR linkage on rules or migrations
    rules_touched = any(f.startswith(".cursor/rules/") for f in files)
    migrations_touched = any(f.startswith("migrations/") for f in files)
    if rules_touched or migrations_touched:
        require(
            any(f.startswith("docs/ADRs/") for f in files),
            "Rules or migrations changed but no ADR updated/added.",
        )

    # 3) Forest freshness (Rule: overview <24h)
    ov = FOREST / "overview.md"
    require(
        file_exists(ov),
        "Forest overview missing. Run: python scripts/generate_forest.py",
    )
    max_age = 60 * 60 * 24
    age = time.time() - ov.stat().st_mtime
    allow_old = os.environ.get("ALLOW_OLD_FOREST") == "1"
    if CI:
        # On CI we never allow stale forest unless explicitly allowed (rare hotfix)
        require(
            age <= max_age or (allow_old and not CI),
            "Forest overview older than 24h. Regenerate forest.",
        )
    else:
        require(
            age <= max_age or allow_old,
            "Forest overview older than 24h. Regenerate forest or set "
            "ALLOW_OLD_FOREST=1 (not allowed on CI).",
        )

    # 4) SSOT schemas present (presence)
    stats_schema = SSOT / "graph-stats.schema.json"
    cor_schema = SSOT / "graph-correlations.schema.json"
    require(
        file_exists(stats_schema),
        "Missing SSOT schema: docs/SSOT/graph-stats.schema.json",
    )
    # correlations schema optional unless correlations present

    # 5) If exports changed, validate JSON against schemas and require PR evidence markers (CI only)
    exports_changed = any(
        f in files or f.startswith("exports/")
        for f in [
            "exports/graph_stats.json",
            "exports/graph_correlations.json",
            "scripts/export_stats.py",
        ]
    )
    stats_path = ROOT / "exports" / "graph_stats.json"
    cor_path = ROOT / "exports" / "graph_correlations.json"

    if stats_path.exists():
        validate_json_schema(stats_path, stats_schema)
    if cor_path.exists() and file_exists(cor_schema):
        validate_json_schema(cor_path, cor_schema)

    if CI and exports_changed:
        have_evidence = any(
            k in PR_BODY.lower()
            for k in ["graph_stats", "graph_correlations", "verifier_pass"]
        )
        require(
            have_evidence,
            "PR body missing exports/correlations evidence "
            "(mention graph_stats/graph_correlations or VERIFIER_PASS).",
        )

    # 6) PR template checklist sanity (CI only, best-effort)
    if CI and code_touched:
        # Look for checklist marks like [x] or [X]
        checklist_ok = bool(
            re.search(r"Docs Updated\s*- \[x\]", PR_BODY, flags=re.IGNORECASE)
        )
        require(checklist_ok, "PR body must check at least one 'Docs Updated' item.")

    print("[rules_guard] PASS")


if __name__ == "__main__":
    main()
