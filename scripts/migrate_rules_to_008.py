#!/usr/bin/env python3
"""
Migrate cursor rules to Rule 008 YAML frontmatter format.

Formatting-only migration (no content/semantics changes).
"""

from pathlib import Path

# Rule number -> (description, globs)
RULE_METADATA = {
    "039": ("Execution Contract Enforcement", []),
    "040": ("CI Triage Playbook", []),
    "041": ("PR Merge Policy", []),
    "042": ("Formatter Single Source of Truth", []),
    "043": ("CI DB Bootstrap & Empty-Data Handling", ["scripts/ci/*", ".github/workflows/*"]),
    "044": ("Share Manifest Contract", []),
    "045": ("Rerank Blend is SSOT", []),
    "046": ("Hermetic CI Fallbacks", []),
    "049": ("GPT-5 Contract v5.2", []),
    "050": ("OPS Contract v6.2.3", []),
    "051": ("Cursor Insight & Handoff", []),
    "052": ("Tool Priority & Context Guidance", []),
    "053": ("Idempotent Baseline", []),
    "054": ("Reuse-First, No-Scaffold-When-Exists", []),
    "055": ("Auto-Docs Sync Pass", []),
    "056": ("UI Generation Standard", ["ui/**", "webui/**"]),
    "059": ("Context Persistence", []),
}


def extract_content_after_header(content: str) -> str:
    """Remove existing YAML-like headers and extract content."""
    lines = content.split("\n")

    # If starts with ---, find the closing ---
    if lines[0].strip() == "---":
        end_idx = None
        for i in range(1, min(len(lines), 20)):
            if lines[i].strip() == "---":
                end_idx = i
                break
        if end_idx:
            return "\n".join(lines[end_idx + 1 :]).lstrip("\n")

    # If starts with id: or # (markdown header), keep all content
    # We'll preserve the original content and just prepend frontmatter
    return content


def add_frontmatter(rule_path: Path, description: str, globs: list[str]) -> bool:
    """Add Rule 008 YAML frontmatter to a rule file."""
    content = rule_path.read_text()

    # Check if already has proper frontmatter
    if content.strip().startswith("---"):
        lines = content.split("\n")
        if len(lines) > 1 and lines[0] == "---" and "---" in lines[1:10]:
            # Check if it has description, alwaysApply, globs
            frontmatter_end = lines.index("---", 1)
            frontmatter = "\n".join(lines[1:frontmatter_end])
            if "description:" in frontmatter and "alwaysApply:" in frontmatter:
                print(f"  ✓ {rule_path.name} already has proper frontmatter")
                return False

    # Build globs YAML
    globs_yaml = "[]"
    if globs:
        globs_yaml = "\n  - " + "\n  - ".join(f'"{g}"' for g in globs)

    # Create frontmatter
    frontmatter = f"""---
description: {description}
alwaysApply: true
globs: {globs_yaml}
---
"""

    # Remove existing YAML-like headers if present
    body = extract_content_after_header(content)

    # If body starts with custom format (id:, version:, etc.), keep it
    # But if it's just markdown, prepend frontmatter
    new_content = frontmatter + body

    rule_path.write_text(new_content)
    return True


def main():
    rules_dir = Path(".cursor/rules")

    migrated = []
    skipped = []

    for rule_num, (description, globs) in RULE_METADATA.items():
        # Find rule file
        pattern = f"{rule_num}-*.mdc"
        matches = list(rules_dir.glob(pattern))

        if not matches:
            print(f"⚠ Warning: No file found for rule {rule_num}")
            continue

        rule_file = matches[0]
        print(f"Processing {rule_file.name}...")

        if add_frontmatter(rule_file, description, globs):
            migrated.append(rule_file.name)
            print("  ✓ Migrated")
        else:
            skipped.append(rule_file.name)

    print(f"\n✓ Migration complete: {len(migrated)} migrated, {len(skipped)} skipped")
    return 0


if __name__ == "__main__":
    exit(main())
