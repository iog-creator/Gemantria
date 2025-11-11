#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(".")


def exists_any(paths):
    return any((ROOT / p).exists() for p in paths)


def file_contains(path, pats):
    p = ROOT / path
    if not p.exists():
        return False
    try:
        t = p.read_text(encoding="utf-8", errors="ignore")
        return all((re.search(pat, t, re.I | re.M) is not None) for pat in pats)
    except Exception:
        return False


result = {
    "sentinels": {
        "triad_rules": (
            Path("RULES_INDEX.md").exists()
            and file_contains("RULES_INDEX.md", [r"050", r"051", r"052"])
        ),
        "ssot_prompt": exists_any(
            ["docs/SSOT/GPT_SYSTEM_PROMPT.md", "GPT_SYSTEM_PROMPT.md"]
        ),
        "agents_triad": (
            Path("AGENTS.md").exists()
            and file_contains("AGENTS.md", [r"Always-Apply", r"050", r"051", r"052"])
        ),
        "dsn_loader": (
            Path("scripts/config/env.py").exists()
            and file_contains(
                "scripts/config/env.py",
                [r"def env\(", r"def get_ro_dsn\(", r"def get_rw_dsn\("],
            )
        ),
        "tagproof_exporter": Path("scripts/exports/export_graph_core.py").exists(),
        "dsn_guard_workflow": Path(".github/workflows/dsn-guard-tags.yml").exists(),
        "tagproof_workflow": Path(
            ".github/workflows/tagproof-core-export.yml"
        ).exists(),
        "masterref_runner": Path("scripts/ops/master_ref_populate.py").exists(),
        "masterref_make": (
            Path("Makefile").exists()
            and file_contains(
                "Makefile",
                [r"docs\.masterref\.populate", r"housekeeping\.masterref"],
            )
        ),
        "atlas_path": exists_any(
            [
                "docs/atlas/index.html",
                "docs/atlas",
                "webui/graph",
                "ui",
                "webui",
            ]
        ),
    }
}

critical_keys = [
    "triad_rules",
    "dsn_loader",
    "tagproof_exporter",
    "dsn_guard_workflow",
    "tagproof_workflow",
]
ok_repo = all(result["sentinels"].get(k, False) for k in critical_keys)
# In PR lane we don't have context; treat same as repo for now
result["ok_repo"] = ok_repo
print(json.dumps(result, indent=2))

