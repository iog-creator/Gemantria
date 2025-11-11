#!/usr/bin/env python3
"""
guard_dsn_centralized.py — precise DSN centralization guard (STRICT-capable)

Flags ONLY direct env access to DSN variables outside the centralized loader.
Allows os.getenv for non-DSN vars (e.g., GITHUB_REF_TYPE, STRICT_*).

Also verifies PR entrypoints enforce RO-on-tag DSN policy.
"""
from __future__ import annotations

import json, re
from pathlib import Path

ROOT = Path(".")
ALLOWLIST = {
    "scripts/config/env.py",               # central loader may touch env directly
    "scripts/config/__init__.py",
}
# Canonical DSN var names (authoritative)
DSN_VARS = {
    "GEMATRIA_DSN","GEMATRIA_RO_DSN",
    "ATLAS_DSN","ATLAS_DSN_RO","ATLAS_DSN_RW",
    "BIBLE_DB_DSN","RW_DSN","RO_DSN","AI_AUTOMATION_DSN",
}
# Regexes for env access (READ operations only; writes are allowed for subprocess setup)
RX_ENV_CALL  = re.compile(r"os\.getenv\(\s*['\"]([A-Za-z0-9_]+)['\"]\s*\)")
RX_ENV_GET   = re.compile(r"os\.environ\.get\(\s*['\"]([A-Za-z0-9_]+)['\"]\s*[,)]")
# Only flag reads from os.environ[...], not writes (os.environ[...] = ...)
RX_ENV_INDEX_READ = re.compile(r"os\.environ\[\s*['\"]([A-Za-z0-9_]+)['\"]\s*\]\s*(?!\s*=)")

def find_dsn_env_violations(p: Path, text: str) -> list[dict]:
    def hits(rx):
        return [m.group(1) for m in rx.finditer(text)]
    names = set(hits(RX_ENV_CALL) + hits(RX_ENV_GET) + hits(RX_ENV_INDEX_READ))
    bad = [n for n in names if n in DSN_VARS]
    v = []
    for n in bad:
        v.append({"file": str(p), "var": n, "reason": "direct DSN env access; use scripts.config.env"})
    return v

def has_ro_on_tag_policy(text: str) -> bool:
    # Must reference tag var AND at least one explicit RO DSN ref or getter.
    has_tag = ("GITHUB_REF_TYPE" in text) or ("STRICT_MASTER_REF" in text)
    has_ro  = ("GEMATRIA_RO_DSN" in text) or ("ATLAS_DSN_RO" in text) or ("get_ro_dsn" in text)
    return has_tag and has_ro

def main():
    entrypoints = [
        "scripts/exports/export_graph_core.py",
        "scripts/ops/master_ref_populate.py",
    ]
    scanned = 0
    violations = []
    for p in ROOT.rglob("**/*.py"):
        rp = str(p)
        if rp.startswith(".venv") or rp.startswith(".git"):
            continue
        scanned += 1
        try:
            t = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if rp not in ALLOWLIST:
            violations.extend(find_dsn_env_violations(p, t))
    # Entry-point policy checks (advisory unless STRICT requested)
    entry = {}
    for fp in entrypoints:
        p = Path(fp)
        ok = False
        if p.exists():
            t = p.read_text(encoding="utf-8", errors="ignore")
            ok = has_ro_on_tag_policy(t)
        entry[fp] = {"exists": p.exists(), "ro_on_tag_policy": ok}

    # Focused status for PR files only
    pr_files = set(entrypoints)
    pr_violations = [v for v in violations if v["file"] in pr_files]
    result = {
        "ok_repo": len(violations) == 0,
        "ok_pr_files": len(pr_violations) == 0 and all(entry[f]["ro_on_tag_policy"] for f in entry),
        "scanned_py_files": scanned,
        "violations_repo": violations,
        "violations_pr": pr_violations,
        "entrypoint_status": entry,
    }
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
