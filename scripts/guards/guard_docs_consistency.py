# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
"""
PLAN-072: DMS Guard — Documentation Management System consistency validation.

Hermetic guard (no network/DB dependencies) that validates documentation consistency
across key governance files. Ensures required patterns are present and bad patterns are absent.

Related: Rule-027 (Docs Sync Gate), Rule-055 (Auto-Docs Sync Pass)
"""
from pathlib import Path
import re
import sys
import json

# Files/directories to scan for consistency patterns
roots = [
    "AGENTS.md",
    "RULES_INDEX.md",
    "GPT_REFERENCE_GUIDE.md",
    "MASTER_PLAN.md",
    "README.md",
    "README_FULL.md",
    ".cursor/rules",
]

# Required patterns (all must be present)
must = [
    r"HINT-only.*STRICT_RFC3339=0",
    r"STRICT.*STRICT_RFC3339=1",
    r'metadata\.source="?fallback_fast_lane"?',
    r"generated_at.*RFC3339",
    r"\bmake housekeeping\b",
]

# Forbidden patterns (none should be present)
bad = [
    r"generated_at.*\b\d{10}(\.\d+)?\b",  # epoch examples (should use RFC3339)
    r"orchestrator.*--limit",  # disallowed flag
    r"\bfast[- ]lane\b.*optional",  # contract is permanent
]


def hitset(patterns, text):
    """Return list of patterns that match in text."""
    return [p for p in patterns if re.search(p, text, re.I | re.M)]


def main():
    """Main guard execution — hermetic, no I/O beyond file system."""
    fails = []
    scanned = []
    errors = []

    for root in roots:
        try:
            for p in Path(".").glob(root):
                if not p.exists():
                    continue
                if p.is_dir():
                    for f in p.rglob("*.md"):
                        try:
                            s = f.read_text(errors="ignore")
                            scanned.append(str(f))
                            # Check for bad patterns
                            bad_matches = hitset(bad, s)
                            # Check for missing required patterns
                            missing_must = [m for m in must if not hitset([m], s)]
                            if bad_matches or missing_must:
                                fails.append(str(f))
                                if bad_matches:
                                    errors.append(f"{f}: found forbidden patterns: {bad_matches}")
                                if missing_must:
                                    errors.append(f"{f}: missing required patterns: {missing_must}")
                        except Exception as e:
                            errors.append(f"{f}: read error: {e}")
                elif p.is_file():
                    try:
                        s = p.read_text(errors="ignore")
                        scanned.append(str(p))
                        bad_matches = hitset(bad, s)
                        missing_must = [m for m in must if not hitset([m], s)]
                        if bad_matches or missing_must:
                            fails.append(str(p))
                            if bad_matches:
                                errors.append(f"{p}: found forbidden patterns: {bad_matches}")
                            if missing_must:
                                errors.append(f"{p}: missing required patterns: {missing_must}")
                    except Exception as e:
                        errors.append(f"{p}: read error: {e}")
        except Exception as e:
            errors.append(f"Error scanning {root}: {e}")

    ok = set(scanned) - set(fails)
    result = {
        "scanned": len(scanned),
        "ok": len(ok),
        "fails": len(fails),
        "fail_list": sorted(set(fails)),
        "errors": errors if errors else None,
    }

    print(json.dumps(result, indent=2))

    if errors:
        print("\n[guard_docs_consistency] Errors encountered:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)

    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
