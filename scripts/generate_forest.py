#!/usr/bin/env python3
"""Generate forest overview from rules, workflows, and ADRs per ADR-019."""

import os
import datetime
import glob
from pathlib import Path

RULES_DIR = '.cursor/rules/*.mdc'
WORKFLOWS_DIR = '.github/workflows/*.yml'
ADRS_DIR = 'docs/ADRs/*.md'
OUTPUT_MD = 'docs/forest/overview.md'


def generate_overview():
    """Generate forest overview document."""
    overview = "# Forest Overview\n\n"
    overview += f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    # Rules
    overview += "## Active Rules\n\n"
    rules = []
    for rule in sorted(glob.glob(RULES_DIR)):
        with open(rule, 'r') as f:
            first_line = f.readline().strip()
            title = first_line.lstrip('#').strip() if first_line.startswith('#') else first_line
            rule_num = os.path.basename(rule).split('.')[0]
            rules.append(f"- Rule {rule_num}: {title}")

    if rules:
        overview += '\n'.join(rules) + '\n\n'
    else:
        overview += "No rules found.\n\n"

    # Workflows
    overview += "## CI Workflows\n\n"
    workflows = []
    for wf in sorted(glob.glob(WORKFLOWS_DIR)):
        wf_name = os.path.basename(wf)
        workflows.append(f"- {wf_name}")

    if workflows:
        overview += '\n'.join(workflows) + '\n\n'
    else:
        overview += "No workflows found.\n\n"

    # ADRs
    overview += "## ADRs\n\n"
    adrs = []
    for adr in sorted(glob.glob(ADRS_DIR)):
        try:
            with open(adr, 'r') as f:
                content = f.read()
                # Extract title from first header
                lines = content.split('\n')
                title = "Unknown Title"
                for line in lines[:5]:  # Check first 5 lines
                    if line.startswith('# '):
                        title = line[2:].strip()
                        break
                adr_num = os.path.basename(adr).split('.')[0]
                adrs.append(f"- {adr_num}: {title}")
        except Exception as e:
            adrs.append(f"- {os.path.basename(adr)}: Error reading ({e})")

    if adrs:
        overview += '\n'.join(adrs) + '\n\n'
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

    with open(output_path, 'w') as f:
        f.write(overview)

    print(f"Forest overview generated at {OUTPUT_MD}")


if __name__ == "__main__":
    generate_overview()