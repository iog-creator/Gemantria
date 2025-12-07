import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def check_adrs_namespace() -> dict:
    """
    Ensure ADRs live only in docs/ADRs/, not docs/adr/.
    AGENTS metadata under docs/adr/ is allowed (non-ADR).
    """
    docs_adrs = REPO_ROOT / "docs" / "ADRs"
    docs_adr = REPO_ROOT / "docs" / "adr"

    issues = []

    # Canonical ADR dir should exist and be non-empty
    if not docs_adrs.exists():
        issues.append("Canonical ADR directory docs/ADRs/ does not exist")
    else:
        adrs = [p for p in docs_adrs.glob("*.md")]
        if not adrs:
            issues.append("Canonical ADR directory docs/ADRs/ contains no .md files")

    # Legacy dir should not contain ADR .md files anymore
    if docs_adr.exists():
        legacy_md = [p for p in docs_adr.glob("*.md") if p.name.lower() != "agents.md"]
        if legacy_md:
            issues.append(
                f"Legacy ADR directory docs/adr/ still contains {len(legacy_md)} ADR .md file(s)"
            )

    ok = not issues
    return {
        "ok": ok,
        "issues": issues,
        "canonical": str(docs_adrs),
        "legacy": str(docs_adr),
    }


def check_schemas_namespace() -> dict:
    """
    Ensure JSON schema files live under schemas/ (machine) and docs/schemas/ (docs),
    not at the repo root or under docs/schema/.
    """
    schemas_dir = REPO_ROOT / "schemas"
    docs_schemas_dir = REPO_ROOT / "docs" / "schemas"
    legacy_docs_schema_dir = REPO_ROOT / "docs" / "schema"

    issues = []

    # Canonical schemas dir should exist (may be empty, but typically has .json files)
    if not schemas_dir.exists():
        issues.append("Canonical schema directory schemas/ does not exist")
    else:
        # It's okay if there are zero .json files, but warn if so
        json_schemas = list(schemas_dir.glob("*.json"))
        if not json_schemas:
            issues.append("Canonical schema directory schemas/ contains no .json files")

    # docs/schemas is optional but if docs/schema exists, that's a problem
    if legacy_docs_schema_dir.exists():
        # Any content in docs/schema is considered legacy at this point
        # Exclude AGENTS.md (directory documentation, not a schema)
        legacy_items = list(legacy_docs_schema_dir.glob("**/*"))
        legacy_items = [p for p in legacy_items if p.is_file() and p.name.lower() != "agents.md"]
        if legacy_items:
            issues.append(
                f"Legacy schema directory docs/schema/ still contains {len(legacy_items)} file(s)"
            )

    # Check for stray *.schema.json at repo root
    root_schema_files = [
        p for p in REPO_ROOT.glob("*.schema.json")
        if not p.is_dir()
    ]
    if root_schema_files:
        issues.append(
            f"Found {len(root_schema_files)} *.schema.json file(s) at repo root (expected under schemas/)"
        )

    ok = not issues
    return {
        "ok": ok,
        "issues": issues,
        "canonical_schemas": str(schemas_dir),
        "canonical_docs_schemas": str(docs_schemas_dir),
        "legacy_docs_schema": str(legacy_docs_schema_dir),
    }


def main() -> int:
    checks = {
        "adrs": check_adrs_namespace(),
        "schemas": check_schemas_namespace(),
    }
    ok = all(c["ok"] for c in checks.values())
    result = {"ok": ok, "checks": checks}
    json.dump(result, sys.stdout, indent=2)
    print()
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
