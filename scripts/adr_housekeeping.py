#!/usr/bin/env python3
"""
adr_housekeeping.py — ADR maintenance and validation per Rule-058.

Updates ADR indexes, validates ADR completeness, and ensures ADR linkage
across the system. Part of the automated housekeeping workflow.
"""

import re
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
ADRS = DOCS / "ADRs"
SSOT = DOCS / "SSOT"


def find_all_adrs() -> List[Path]:
    """Find all ADR files in the repository."""
    adrs = []
    if ADRS.exists():
        # Only consider files in the docs/ADRs/ directory that start with ADR-
        for adr_file in ADRS.glob("ADR-*.md"):
            adrs.append(adr_file)
    return sorted(adrs)


def parse_adr_metadata(content: str) -> Dict[str, str]:
    """Parse ADR metadata from content."""
    metadata = {}

    # Status patterns
    status_match = re.search(r"## Status\s*\n\s*([^\n]+)", content, re.IGNORECASE)
    if status_match:
        metadata["status"] = status_match.group(1).strip()

    # Date patterns
    date_match = re.search(r"## Date\s*\n\s*([^\n]+)", content, re.IGNORECASE)
    if date_match:
        metadata["date"] = date_match.group(1).strip()

    return metadata


def validate_adr_completeness(adr_path: Path) -> List[str]:
    """Validate ADR completeness and return issues."""
    issues = []
    content = adr_path.read_text()

    # Check for required sections
    required_sections = ["## Status", "## Context", "## Decision", "## Consequences"]

    for section in required_sections:
        if section not in content:
            issues.append(f"Missing required section: {section}")

    # Check status is valid
    metadata = parse_adr_metadata(content)
    valid_statuses = ["Proposed", "Accepted", "Rejected", "Deprecated", "Superseded"]
    if "status" in metadata and metadata["status"] not in valid_statuses:
        issues.append(f"Invalid status: {metadata['status']} (must be one of {valid_statuses})")

    # Check for ADR number in filename
    if not re.match(r".*ADR-\d+.*", str(adr_path)):
        issues.append("ADR filename should contain ADR number (ADR-XXX)")

    return issues


def update_adr_index():
    """Update the ADR index in docs/README.md or create if missing."""
    adrs = find_all_adrs()

    if not adrs:
        print("No ADRs found to index")
        return

    # Create ADR index content
    index_content = "# Architectural Decision Records (ADRs)\n\n"
    index_content += f"Total ADRs: {len(adrs)}\n\n"
    index_content += "| ADR | Title | Status | Date |\n"
    index_content += "|-----|-------|--------|------|\n"

    for adr_path in sorted(adrs):
        content = adr_path.read_text()
        metadata = parse_adr_metadata(content)

        # Extract title
        title_match = re.search(r"# (ADR-\d+:?.*)", content)
        title = title_match.group(1) if title_match else adr_path.stem

        # Get relative path
        rel_path = adr_path.relative_to(ROOT)

        index_content += f"| [{rel_path}]({rel_path}) | {title} | {metadata.get('status', 'Unknown')} | {metadata.get('date', 'Unknown')} |\n"

    # Update docs/README.md or create ADR-specific index
    readme_path = DOCS / "README.md"
    adr_index_path = DOCS / "ADR_INDEX.md"

    # Look for ADR section in README
    if readme_path.exists():
        readme_content = readme_path.read_text()
        if "## Architectural Decision Records" in readme_content:
            # Replace ADR section
            before_adr = readme_content.split("## Architectural Decision Records")[0]
            after_adr_match = re.search(r"## Architectural Decision Records.*?(?=\n## |\Z)", readme_content, re.DOTALL)
            after_adr = readme_content[after_adr_match.end() :] if after_adr_match else ""

            new_content = before_adr + "## Architectural Decision Records\n\n" + index_content + "\n" + after_adr
            readme_path.write_text(new_content)
            print(f"Updated ADR index in {readme_path}")
        else:
            # Append ADR index to README
            with open(readme_path, "a") as f:
                f.write("\n## Architectural Decision Records\n\n")
                f.write(index_content)
            print(f"Added ADR index to {readme_path}")
    else:
        # Create dedicated ADR index
        adr_index_path.write_text(index_content)
        print(f"Created ADR index at {adr_index_path}")


def validate_adr_linkage():
    """Validate that ADRs are properly linked throughout the codebase."""
    issues = []
    adrs = find_all_adrs()

    if not adrs:
        return ["No ADRs found to validate linkage"]

    # Check that ADRs reference each other when superseded
    for adr_path in adrs:
        content = adr_path.read_text()
        if "Superseded" in content:
            # Should reference the superseding ADR
            if not re.search(r"ADR-\d+", content):
                issues.append(f"{adr_path.name}: Superseded ADR should reference superseding ADR")

    # Check for orphaned ADR references
    all_md_files = list(ROOT.rglob("*.md"))
    for md_file in all_md_files:
        if md_file == DOCS / "ADR_INDEX.md":
            continue

        content = md_file.read_text()
        adr_refs = re.findall(r"ADR-(\d+)", content)

        for adr_num in adr_refs:
            adr_exists = any(f"ADR-{adr_num}" in str(adr) for adr in adrs)
            if not adr_exists:
                issues.append(f"{md_file.name}: References non-existent ADR-{adr_num}")

    return issues


def main():
    """Main ADR housekeeping function."""
    print("🏛️  ADR HOUSEKEEPING STARTED")
    print("=" * 40)

    # Find and validate ADRs
    adrs = find_all_adrs()
    print(f"Found {len(adrs)} ADR files")

    # Validate each ADR
    total_issues = 0
    for adr_path in adrs:
        issues = validate_adr_completeness(adr_path)
        if issues:
            print(f"❌ {adr_path.name}:")
            for issue in issues:
                print(f"   • {issue}")
            total_issues += len(issues)
        else:
            print(f"✅ {adr_path.name}: Valid")

    # Update ADR index
    print("\n📝 Updating ADR index...")
    update_adr_index()

    # Validate ADR linkage
    print("\n🔗 Validating ADR linkage...")
    linkage_issues = validate_adr_linkage()
    if linkage_issues:
        print("❌ ADR Linkage Issues:")
        for issue in linkage_issues:
            print(f"   • {issue}")
        total_issues += len(linkage_issues)
    else:
        print("✅ ADR linkage validation passed")

    if total_issues > 0:
        print(f"\n❌ ADR housekeeping completed with {total_issues} issues")
        exit(1)
    else:
        print("\n✅ ADR housekeeping completed successfully")


if __name__ == "__main__":
    main()
