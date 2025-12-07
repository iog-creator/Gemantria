import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def check_adrs_namespace() -> dict:
    """
    Ensure ADRs live only in docs/ADRs/, not docs/adr/.
    """
    docs_adrs = REPO_ROOT / "docs" / "ADRs"
    docs_adr = REPO_ROOT / "docs" / "adr"

    issues = []

    # Canonical ADR dir should exist and be non-empty
    if not docs_adrs.exists():
        issues.append("Canonical ADR directory docs/ADRs/ does not exist")
    else:
        adrs = list(docs_adrs.glob("*.md"))
        if not adrs:
            issues.append("Canonical ADR directory docs/ADRs/ contains no .md files")

    # Legacy dir should not contain .md files anymore (excluding AGENTS.md which is directory docs)
    if docs_adr.exists():
        legacy_md = [f for f in docs_adr.glob("*.md") if f.name != "AGENTS.md"]
        if legacy_md:
            issues.append(
                f"Legacy ADR directory docs/adr/ still contains {len(legacy_md)} .md file(s): {[f.name for f in legacy_md]}"
            )

    ok = not issues
    return {
        "ok": ok,
        "issues": issues,
        "canonical": str(docs_adrs),
        "legacy": str(docs_adr),
    }


def main() -> int:
    checks = {
        "adrs": check_adrs_namespace(),
    }
    ok = all(c["ok"] for c in checks.values())
    result = {"ok": ok, "checks": checks}
    json.dump(result, sys.stdout, indent=2)
    print()
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
