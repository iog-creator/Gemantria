#!/usr/bin/env python3
"""Bridge rules and ADRs enforcement per ADR-022."""

import glob
import re
import os

RULES_DIR = ".cursor/rules/*.mdc"
ADRS_DIR = "docs/ADRs/*.md"


def load_rules():
    """Load active rules from .mdc files."""
    rules = []
    for file_path in glob.glob(RULES_DIR):
        try:
            with open(file_path) as f:
                content = f.read()
                # Extract rule title from content
                match = re.search(r"Rule \d+: (.*)", content)
                if match:
                    rules.append(match.group(1).strip())
                else:
                    # Fallback to filename
                    rule_name = os.path.basename(file_path).replace(".mdc", "")
                    rules.append(f"Rule {rule_name}")
        except Exception as e:
            print(f"Warning: Could not read rule file {file_path}: {e}")
    return set(rules)


def load_adrs():
    """Load ADR references to rules."""
    adr_rules = set()
    for file_path in glob.glob(ADRS_DIR):
        try:
            with open(file_path) as f:
                content = f.read()
                # Extract related rules from ADR content
                matches = re.findall(r"Related Rules?: ([^\n]+)", content, re.IGNORECASE)
                for match in matches:
                    # Split on commas and clean up
                    rules = [r.strip() for r in match.split(",")]
                    adr_rules.update(rules)
        except Exception as e:
            print(f"Warning: Could not read ADR file {file_path}: {e}")
    return adr_rules


def check_bridge():
    """Check that all active rules are referenced in ADRs."""
    rules = load_rules()
    adr_rules = load_adrs()

    # Find rules that are not referenced in ADRs
    missing_references = rules - adr_rules

    if missing_references:
        raise ValueError(f"Rules not referenced in ADRs: {sorted(missing_references)}")

    print("System enforcement bridge validated ✓")


if __name__ == "__main__":
    try:
        check_bridge()
    except Exception as e:
        print(f"Enforcement bridge check failed: {e}")
        exit(1)
