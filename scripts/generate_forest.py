# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
"""Generate forest overview from rules, workflows, and ADRs per ADR-019."""

import os
import datetime
import glob
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

RULES_DIR = ".cursor/rules/*.mdc"
WORKFLOWS_DIR = ".github/workflows/*.yml"
ADRS_DIR = "docs/ADRs/*.md"
OUTPUT_MD = "docs/forest/overview.md"


def _read_rule_file(rule_path: str) -> str:
    """Read a single rule file and extract title (for parallel processing)."""
    try:
        with open(rule_path) as f:
            first_line = f.readline().strip()
            title = first_line.lstrip("#").strip() if first_line.startswith("#") else first_line
            rule_num = os.path.basename(rule_path).split(".")[0]
            return f"- Rule {rule_num}: {title}"
    except Exception:
        return None


def _read_adr_file(adr_path: str) -> str:
    """Read a single ADR file and extract title (for parallel processing)."""
    try:
        with open(adr_path) as f:
            content = f.read()
            lines = content.split("\n")
            title = "Unknown Title"
            for line in lines[:5]:
                if line.startswith("# "):
                    title = line[2:].strip()
                    break
            adr_num = os.path.basename(adr_path).split(".")[0]
            return f"- {adr_num}: {title}"
    except Exception as e:
        return f"- {os.path.basename(adr_path)}: Error reading ({e})"


def generate_overview():
    """Generate forest overview document (parallelized file reading)."""
    overview = "# Forest Overview\n\n"
    overview += f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    # Rules (parallelized)
    overview += "## Active Rules\n\n"
    rule_files = sorted(glob.glob(RULES_DIR))
    rules = []
    if rule_files:
        with ProcessPoolExecutor(max_workers=min(8, len(rule_files))) as executor:
            futures = {executor.submit(_read_rule_file, rule): rule for rule in rule_files}
            for future in as_completed(futures):
                result = future.result()
                if result:
                    rules.append(result)
        rules.sort()  # Sort by rule number

    if rules:
        overview += "\n".join(rules) + "\n\n"
    else:
        overview += "No rules found.\n\n"

    # Workflows (simple - no parallelization needed)
    overview += "## CI Workflows\n\n"
    workflows = []
    for wf in sorted(glob.glob(WORKFLOWS_DIR)):
        wf_name = os.path.basename(wf)
        workflows.append(f"- {wf_name}")

    if workflows:
        overview += "\n".join(workflows) + "\n\n"
    else:
        overview += "No workflows found.\n\n"

    # ADRs (parallelized)
    overview += "## ADRs\n\n"
    adr_files = sorted(glob.glob(ADRS_DIR))
    adrs = []
    if adr_files:
        with ProcessPoolExecutor(max_workers=min(8, len(adr_files))) as executor:
            futures = {executor.submit(_read_adr_file, adr): adr for adr in adr_files}
            for future in as_completed(futures):
                adrs.append(future.result())
        adrs.sort()  # Sort by ADR number

    if adrs:
        overview += "\n".join(adrs) + "\n\n"
    else:
        overview += "No ADRs found.\n\n"

    # Phase gate status
    overview += "## Phase Gate Status\n\n"
    overview += "- Forest regeneration: ✅ Required before new PRs (Rule 025)\n"
    overview += "- SSOT sync: ✅ Docs/ADRs/rules must sync (Rule 027)\n"
    overview += "- ADR coverage: ✅ New changes require ADR delta (Rule 029)\n\n"

    # Write output
    output_path = Path(OUTPUT_MD)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        f.write(overview)

    print(f"Forest overview generated at {OUTPUT_MD}")


if __name__ == "__main__":
    generate_overview()
