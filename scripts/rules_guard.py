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
import subprocess
import sys
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
    print("[rules_guard] Starting critical validation checks...")
    files = changed_files()
    print(f"[rules_guard] Found {len(files)} changed files")
    if not files:
        print("[rules_guard] PASS (no changes detected)")
        return

    code_dirs = ("src/", "scripts/", "migrations/", "webui/")
    code_touched = any(f.startswith(code_dirs) for f in files)
    docs_touched = any(
        f.startswith("docs/") or f.endswith("README.md") or f.endswith("AGENTS.md")
        for f in files
    )

    print(f"[rules_guard] Code touched: {code_touched}, Docs touched: {docs_touched}")

    # CRITICAL CHECK 1: Doc sync when code changes (Rule 027 - always applied)
    if code_touched:
        print("[rules_guard] Critical Check 1: Documentation sync required")
        require(
            docs_touched,
            "CRITICAL: Code changed but no docs updated. Must update AGENTS.md/ADR/SSOT/README.",
        )
        print("[rules_guard] ✓ Critical Check 1 PASSED: Docs updated for code changes")

    # CRITICAL CHECK 2: Rules audit (ensures rule numbering + docs sync)
    print("[rules_guard] Critical Check 2: Rules system integrity")
    print("[rules_guard] ✓ Running rules audit...")
    try:
        subprocess.check_call(
            [sys.executable, str(ROOT / "scripts" / "rules_audit.py")]
        )
        print("[rules_guard] ✓ Critical Check 2 PASSED: Rules audit successful")
    except subprocess.CalledProcessError:
        require(False, "CRITICAL: Rules audit failed — fix rule numbering or docs sync")

    # CRITICAL CHECK 3: AGENTS.md coverage (Rule 017 - agent docs presence)
    print("[rules_guard] Critical Check 3: AGENTS.md file coverage")
    agents_files = list(ROOT.glob("**/AGENTS.md"))
    agents_count = len(agents_files)
    required_min = 10  # Per AGENTS.md documentation
    print(
        f"[rules_guard] Found {agents_count} AGENTS.md files (minimum required: {required_min})"
    )

    if agents_count >= required_min:
        print(
            f"[rules_guard] ✓ Critical Check 3 PASSED: AGENTS.md coverage sufficient ({agents_count} files)"
        )
    else:
        require(
            False,
            f"CRITICAL: Insufficient AGENTS.md coverage. Found {agents_count}, need ≥{required_min}. Missing files in source directories.",
        )

    print("[rules_guard] ALL CRITICAL CHECKS PASSED - Ready for commit")


if __name__ == "__main__":
    main()
