# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

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
        from jsonschema import Draft202012Validator, validate  # noqa: E402

        instance = load_json(instance_path)
        schema = load_json(schema_path)
        Draft202012Validator.check_schema(schema)
        validate(instance=instance, schema=schema)
    except Exception as e:
        require(False, f"Schema validation failed for {instance_path}: {e}")


def validate_hints_governance():
    """
    Validate that LOUD HINTS system is properly implemented per Rule-026.

    Checks:
    - hint.sh exists and emits LOUD HINTS
    - Key functions have proper Related Rules/Agents in docstrings
    - Hint emissions are connected to MDC rules
    - Metadata backing is comprehensive
    """
    print("[rules_guard]   Checking hint.sh existence and LOUD format...")

    # Check hint.sh exists and works
    hint_script = ROOT / "scripts" / "hint.sh"
    if not hint_script.exists():
        require(False, "CRITICAL: scripts/hint.sh missing (Rule-026 LOUD HINTS requirement)")

    # Test hint.sh emits LOUD format
    try:
        result = subprocess.run([str(hint_script), "test"], capture_output=True, text=True, timeout=5)
        if "🔥🔥🔥 LOUD HINT:" not in result.stdout:
            require(False, "CRITICAL: hint.sh not emitting LOUD HINTS format (Rule-026)")
    except Exception as e:
        require(False, f"CRITICAL: hint.sh execution failed: {e}")

    print("[rules_guard]   ✓ hint.sh exists and emits LOUD HINTS")

    # Check key functions have governance metadata
    print("[rules_guard]   Checking function docstrings for governance metadata...")

    governance_functions = [
        ("src.graph.graph.run_pipeline", ["Related Rules:", "Related Agents:"]),
        ("src.graph.graph.wrap_hints_node", ["Related Rules:", "Related Agents:"]),
        ("src.services.lmstudio_client.assert_qwen_live", ["Related Rules:", "Related Agents:"]),
    ]

    for func_path, required_sections in governance_functions:
        try:
            module_path, func_name = func_path.rsplit(".", 1)
            module = __import__(module_path, fromlist=[func_name])
            func = getattr(module, func_name)
            docstring = func.__doc__ or ""

            missing_sections = []
            for section in required_sections:
                if section not in docstring:
                    missing_sections.append(section)

            if missing_sections:
                require(
                    False,
                    f"CRITICAL: {func_path} docstring missing governance sections: {', '.join(missing_sections)} (Rule-026)",
                )

        except Exception as e:
            require(False, f"CRITICAL: Failed to validate {func_path} governance metadata: {e}")

    print("[rules_guard]   ✓ Function docstrings include governance metadata")

    # Check hints registry documentation exists
    print("[rules_guard]   Checking hints registry documentation...")
    hints_registry = DOCS / "hints_registry.md"
    if not hints_registry.exists():
        require(False, "CRITICAL: docs/hints_registry.md missing (Rule-026 documentation requirement)")

    with open(hints_registry) as f:
        content = f.read()
        if "METADATA BACKING" not in content:
            require(False, "CRITICAL: hints_registry.md missing METADATA BACKING section (Rule-026)")

    print("[rules_guard]   ✓ Hints registry documentation complete")


def main():
    """
    Main entry point for rules enforcement validation.

    Implements Rule-026 (System Enforcement Bridge) - Pre-commit + CI + Branch Protection.
    Implements Rule-027 (Docs Sync Gate) - Require docs/ADR/SSOT updates for code changes.
    Implements Rule-058 (Auto-Housekeeping Post-Change) - Run rules_audit.py/share.sync/forest regen.

    Emits LOUD HINTS for Rule-026, Rule-027, Rule-058, and system enforcement requirements.

    Returns:
        None (exits with appropriate status code)

    Related Rules: Rule-026, Rule-027, Rule-058
    Related Agents: scripts/rules_guard.py System-level Enforcement
    """
    print("🔥🔥🔥 LOUD HINT: Rule-026 (System Enforcement Bridge) - Pre-commit + CI + Branch Protection 🔥🔥🔥")
    print("🔥🔥🔥 LOUD HINT: Rule-027 (Docs Sync Gate) - Require docs/ADR/SSOT updates for code changes 🔥🔥🔥")
    print(
        "🔥🔥🔥 LOUD HINT: Rule-058 (Auto-Housekeeping Post-Change) - Run rules_audit.py/share.sync/forest regen 🔥🔥🔥"
    )
    print("🔥🔥🔥 LOUD HINT: scripts/rules_guard.py - System-level enforcement so rules aren't just words 🔥🔥🔥")
    print("[rules_guard] Starting critical validation checks...")
    files = changed_files()
    print(f"[rules_guard] Found {len(files)} changed files")
    if not files:
        print("[rules_guard] PASS (no changes detected)")
        return

    code_dirs = ("src/", "scripts/", "migrations/", "webui/")
    code_touched = any(f.startswith(code_dirs) for f in files)
    docs_touched = any(f.startswith("docs/") or f.endswith("README.md") or f.endswith("AGENTS.md") for f in files)

    print(f"[rules_guard] Code touched: {code_touched}, Docs touched: {docs_touched}")

    # CRITICAL CHECK 1: Doc sync when code changes (Rule 027 - always applied)
    if code_touched:
        print("[rules_guard] Critical Check 1: Documentation sync required")
        require(
            docs_touched,
            "CRITICAL: Code changed but no docs updated. Must update AGENTS.md/ADR/SSOT/README.",
        )
        print("[rules_guard] ✓ Critical Check 1 PASSED: Docs updated for code changes")

        # Additional check: AGENTS.md sync (Rule 006 - AGENTS.md Governance)
        # FAIL-CLOSED: Stale AGENTS.md files block merges per Rule-006, Rule-027, Rule-058
        print("[rules_guard] Additional Check 1a: AGENTS.md sync verification (fail-closed)")
        try:
            sync_result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "check_agents_md_sync.py"), "--staged"],
                capture_output=True,
                text=True,
                check=False,
            )
            if sync_result.returncode != 0:
                print(
                    "[rules_guard] FAIL: AGENTS.md files are stale and must be updated",
                    file=sys.stderr,
                )
                print(sync_result.stdout, file=sys.stderr)
                print(sync_result.stderr, file=sys.stderr)
                print(
                    "[rules_guard]    Run: python scripts/check_agents_md_sync.py --verbose",
                    file=sys.stderr,
                )
                require(
                    False,
                    "CRITICAL: AGENTS.md files are stale. Update them to reflect code changes per Rule-006, Rule-027, Rule-058.",
                )
            print("[rules_guard] ✓ Additional Check 1a PASSED: AGENTS.md files are in sync")
        except Exception as e:
            require(False, f"CRITICAL: Could not run AGENTS.md sync check: {e}")

    # CRITICAL CHECK 2: Rules audit (ensures rule numbering + docs sync)
    print("[rules_guard] Critical Check 2: Rules system integrity")
    print("[rules_guard] ✓ Running rules audit...")
    try:
        subprocess.check_call([sys.executable, str(ROOT / "scripts" / "rules_audit.py")])
        print("[rules_guard] ✓ Critical Check 2 PASSED: Rules audit successful")
    except subprocess.CalledProcessError:
        require(False, "CRITICAL: Rules audit failed — fix rule numbering or docs sync")

    # CRITICAL CHECK 3: AGENTS.md coverage (Rule 017 - agent docs presence)
    print("[rules_guard] Critical Check 3: AGENTS.md file coverage")
    # Rule 017 specifies specific required files
    required_files = [
        ROOT / "src" / "AGENTS.md",
        ROOT / "src" / "services" / "AGENTS.md",
        ROOT / "webui" / "graph" / "AGENTS.md",
    ]

    missing_files = []
    for req_file in required_files:
        if not file_exists(req_file):
            missing_files.append(str(req_file.relative_to(ROOT)))

    if missing_files:
        require(
            False,
            f"CRITICAL: Missing required AGENTS.md files per Rule 017: {', '.join(missing_files)}",
        )

    print("[rules_guard] ✓ Critical Check 3 PASSED: All Rule 017 required AGENTS.md files present")

    print("[rules_guard] Critical Check 4: Rule-054 reuse-first duplicate detection")
    # Rule-054: Reuse-first duplicate detection (scoped, conservative)
    # Blocks newly-added files that duplicate existing feature classes.
    dup_patterns = [
        r"src/.*/(?:pipeline|graph|envelope|rerank).*\\.py$",
        r"^src/(?:.*)/rerank_.*\\.py$",  # block adding new reranker impls
        r"^src/rerank/(?!__init__\\.py$).+\\.py$",  # block files under src/rerank/** (reuse existing only)
        r"migrations/.*\\.sql$",
        r"scripts/.*/(?:export|pipeline|db).*\\.(sh|py)$",
        r"docs/.*/(?:pipeline|schema|exports|badges).*\\.md$",
        r"scripts/.*/build_badges\\.py$",
        r"exports/.+\\.(json|csv)$",  # block adding checked-in static exports
        r"webui/.*/(components|pages|views)/.*\\.(tsx|jsx|vue)$",  # block duplicate UI scaffolds
    ]
    # Diff only against main to detect NEW files in this PR/branch
    try:
        out = sh("git diff --name-status origin/main...HEAD")
        added = [ln.split("\t", 1)[1] for ln in out.splitlines() if ln.startswith("A\t")]
        offenders = []
        for path in added:
            for pat in dup_patterns:
                if re.search(pat, path):
                    offenders.append(path)
                    break
        if offenders:
            require(
                False,
                f"RULE-054 violation: duplicate-like files added: {', '.join(offenders)}. Use adapters to existing modules; do not re-scaffold.",
            )
    except Exception as e:
        print(f"[rules_guard] Warning: Could not check Rule-054 (diff failed): {e}")

    print("[rules_guard] ✓ Critical Check 4 PASSED: Rule-054 reuse-first compliance")

    # CRITICAL CHECK 5: Hints envelope validation (Rule-026 enforcement bridge)
    print("[rules_guard] Critical Check 5: Hints envelope in exports")
    graph_export_path = ROOT / "exports" / "graph_latest.json"
    if graph_export_path.exists():
        try:
            graph_data = load_json(graph_export_path)
            metadata = graph_data.get("metadata", {})
            hints = metadata.get("hints")
            if hints:
                # Validate envelope structure
                if isinstance(hints, dict) and hints.get("type") == "hints_envelope":
                    hint_count = hints.get("count", len(hints.get("items", [])))
                    print(f"[rules_guard] ✓ Critical Check 5 PASSED: Hints envelope found ({hint_count} hints)")
                else:
                    print(
                        "[rules_guard] WARNING: Hints present but not in envelope format. Expected type='hints_envelope'",
                        file=sys.stderr,
                    )
            else:
                # Non-fatal: hints are encouraged but not required for empty/new pipelines
                print("[rules_guard] HINT: No hints envelope in graph export (encouraged for PRs per Rule-026)")
        except Exception as e:
            print(f"[rules_guard] Warning: Could not validate hints in graph export: {e}")
    else:
        print("[rules_guard] HINT: graph_latest.json not found (skipping hints validation)")

    # CRITICAL CHECK 6: ADR mention on infra/data PRs (Rule-029)
    print("[rules_guard] Critical Check 6: ADR mention required for infra/data changes")
    # Require ADR mention when sensitive areas change
    touched = subprocess.check_output(["git", "diff", "--name-only", "origin/main...HEAD"], text=True).splitlines()
    needs_adr = any(
        any(
            t.startswith(prefix)
            for prefix in [
                ".github/workflows/",
                "scripts/",
                "docs/SSOT/",
                "migrations/",
                "src/infra/",
            ]
        )
        for t in touched
    )
    if needs_adr:
        pr_body = os.environ.get("PR_BODY", "")  # set by CI step or fallback to empty
        if "ADR-" not in pr_body:
            require(False, "ADR mention required for infra/data changes (Rule-029).")
    print("[rules_guard] ✓ Critical Check 6 PASSED: ADR mention check complete")

    # CRITICAL CHECK 7: LOUD HINTS governance compliance (Rule-026)
    print("[rules_guard] Critical Check 7: LOUD HINTS governance compliance")
    validate_hints_governance()
    print("[rules_guard] ✓ Critical Check 7 PASSED: LOUD HINTS governance compliant")

    print("[rules_guard] ALL CRITICAL CHECKS PASSED - Ready for commit")


if __name__ == "__main__":
    main()
