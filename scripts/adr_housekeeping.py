#!/usr/bin/env python3
"""
adr_housekeeping.py - Automated ADR Creation and Updates for Housekeeping

Integrates with the 4 critical information sources:
1. Hints envelopes (runtime intelligence)
2. AGENTS.md files (plural, governance docs)
3. .mdc rules (Cursor workspace rules)
4. ADRs (architectural decisions)

Automatically creates/updates ADRs when architectural changes are detected.
Part of Rule-058 housekeeping automation.
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

ROOT = Path(__file__).resolve().parent.parent

# ADR template
ADR_TEMPLATE = """# ADR-{number:03d}: {title}

## Status
Proposed | Accepted | Deprecated | Superseded by ADR-{superseded_by}

## Context
{context}

## Decision
{decision}

## Consequences
{consequences}

## Verification
{verification}

## Related Rules
{related_rules}

## Implementation Notes
{implementation_notes}

## Metadata
- **Date**: {date}
- **Status**: {status}
- **Superseded By**: ADR-{superseded_by}
- **Related ADRs**: {related_adrs}
- **Source**: {source}
- **Rule References**: {rule_references}
"""


class ADRManager:
    """Manages automated ADR creation and updates."""

    def __init__(self):
        self.adrs_dir = ROOT / "docs" / "ADRs"
        self.sources = {
            "hints_envelopes": self._check_hints_envelopes,
            "agents_md": self._check_agents_md_files,
            "mdc_rules": self._check_mdc_rules,
            "existing_adrs": self._check_existing_adrs,
        }
        self.detected_changes: Dict[str, List[Dict[str, Any]]] = {}
        self.next_adr_number = self._get_next_adr_number()

    def _get_next_adr_number(self) -> int:
        """Get the next available ADR number."""
        if not self.adrs_dir.exists():
            return 1

        existing = []
        for f in self.adrs_dir.glob("ADR-*.md"):
            match = re.match(r"ADR-(\d{3})-", f.name)
            if match:
                existing.append(int(match.group(1)))

        return max(existing) + 1 if existing else 1

    def run_housekeeping(self) -> bool:
        """Run complete ADR housekeeping."""
        print("🔍 ADR HOUSEKEEPING - Scanning 4 information sources...")

        changes_detected = False

        for source_name, checker in self.sources.items():
            print(f"📋 Checking {source_name.replace('_', ' ')}...")
            changes = checker()
            if changes:
                self.detected_changes[source_name] = changes
                changes_detected = True
                print(f"  ✅ Found {len(changes)} potential ADR updates")
            else:
                print("  ✅ No changes detected")
        if changes_detected:
            print("\n🏗️  Processing detected changes...")
            self._process_changes()
            print("✅ ADR housekeeping complete")
            return True
        else:
            print("✅ No ADR changes needed")
            return False

    def _check_hints_envelopes(self) -> List[Dict[str, Any]]:
        """Check hints envelopes for architectural decisions."""
        changes = []
        exports_dir = ROOT / "exports"

        if not exports_dir.exists():
            return changes

        for envelope_file in exports_dir.glob("*hints_envelope*.json"):
            try:
                with open(envelope_file, encoding="utf-8") as f:
                    envelope = json.load(f)

                if envelope.get("type") != "hints_envelope":
                    continue

                # Check for imperative commands indicating architectural changes
                imperative_commands = envelope.get("imperative_commands", [])
                if any(
                    cmd in ["ENFORCE_PROJECT_GOVERNANCE", "VALIDATE_ENVELOPE_CONTENTS"] for cmd in imperative_commands
                ):
                    changes.append(
                        {
                            "type": "hints_envelope_architecture",
                            "source": "hints_envelope",
                            "file": str(envelope_file.relative_to(ROOT)),
                            "title": "Hints Envelope Architecture Enhancement",
                            "context": "Hints envelopes now contain imperative commands for critical system enforcement",
                            "decision": "Enhanced hints envelopes with imperative command protocol for automated governance",
                            "consequences": "Improved system reliability and automated enforcement of critical operations",
                        }
                    )

                # Check for envelope error system
                if "envelope_error_system" in envelope.get("enforcement_level", ""):
                    changes.append(
                        {
                            "type": "envelope_error_system",
                            "source": "hints_envelope",
                            "file": str(envelope_file.relative_to(ROOT)),
                            "title": "Envelope Error System Implementation",
                            "context": "Runtime hints now include critical error system with imperative commands",
                            "decision": "Implemented envelope error system for automated critical issue handling",
                            "consequences": "Enhanced system robustness with automated error recovery and governance enforcement",
                        }
                    )

            except Exception as e:
                print(f"  ⚠️  Error reading {envelope_file}: {e}")

        return changes

    def _check_agents_md_files(self) -> List[Dict[str, Any]]:
        """Check AGENTS.md files for new architectural content."""
        changes = []
        agents_files = [ROOT / "AGENTS.md", ROOT / "docs" / "AGENTS.md", ROOT / "src" / "AGENTS.md"]

        for agents_file in agents_files:
            if not agents_file.exists():
                continue

            try:
                content = agents_file.read_text(encoding="utf-8")

                # Check for new agent frameworks
                if "Agentic Pipeline Framework" in content and not self._adr_exists("agentic_pipeline"):
                    changes.append(
                        {
                            "type": "agentic_pipeline",
                            "source": "agents_md",
                            "file": str(agents_file.relative_to(ROOT)),
                            "title": "Agentic Pipeline Framework Implementation",
                            "context": "Complex pipeline operations require specialized AI agents for different phases",
                            "decision": "Implemented comprehensive agent framework with ingestion, enrichment, graph building, and analytics agents",
                            "consequences": "Improved pipeline automation and specialized handling of complex tasks",
                        }
                    )

                # Check for PMS system
                if "Project Management System" in content and not self._adr_exists("pms_system"):
                    changes.append(
                        {
                            "type": "pms_system",
                            "source": "agents_md",
                            "file": str(agents_file.relative_to(ROOT)),
                            "title": "Project Management System Implementation",
                            "context": "Need systematic approach to manage governance across large codebases",
                            "decision": "Implemented PMS with 4 information sources: hints envelopes, AGENTS.md files, .mdc rules, and ADRs",
                            "consequences": "Improved project governance and automated compliance management",
                        }
                    )

            except Exception as e:
                print(f"  ⚠️  Error reading {agents_file}: {e}")

        return changes

    def _check_mdc_rules(self) -> List[Dict[str, Any]]:
        """Check .mdc rules for new architectural rules."""
        changes = []
        rules_dir = ROOT / ".cursor" / "rules"

        if not rules_dir.exists():
            return changes

        for rule_file in rules_dir.glob("*.mdc"):
            try:
                content = rule_file.read_text(encoding="utf-8")

                # Extract rule number and title
                match = re.search(r"# Rule (\d+) — (.+)", content)
                if not match:
                    continue

                rule_num = int(match.group(1))
                rule_title = match.group(2)

                # Check if this rule needs an ADR
                if rule_num >= 58 and not self._adr_exists(f"rule_{rule_num}"):
                    changes.append(
                        {
                            "type": f"rule_{rule_num}",
                            "source": "mdc_rules",
                            "file": str(rule_file.relative_to(ROOT)),
                            "title": f"Rule {rule_num}: {rule_title}",
                            "context": f"New governance rule {rule_num} introduced for project management",
                            "decision": f"Implemented Rule {rule_num} - {rule_title}",
                            "consequences": "Enhanced project governance and compliance management",
                        }
                    )

            except Exception as e:
                print(f"  ⚠️  Error reading {rule_file}: {e}")

        return changes

    def _check_existing_adrs(self) -> List[Dict[str, Any]]:
        """Check existing ADRs for updates needed."""
        changes = []

        if not self.adrs_dir.exists():
            return changes

        for adr_file in self.adrs_dir.glob("ADR-*.md"):
            try:
                content = adr_file.read_text(encoding="utf-8")

                # Check for ADRs that reference rules that may have been updated
                if "## Related Rules" in content:
                    # Could check if referenced rules still exist or have been updated
                    # For now, just note that ADRs exist
                    pass

            except Exception as e:
                print(f"  ⚠️  Error reading {adr_file}: {e}")

        return changes

    def _adr_exists(self, adr_type: str) -> bool:
        """Check if an ADR of the given type already exists."""
        if not self.adrs_dir.exists():
            return False

        for adr_file in self.adrs_dir.glob("ADR-*.md"):
            try:
                content = adr_file.read_text(encoding="utf-8")
                if adr_type in content:
                    return True
            except Exception:
                continue

        return False

    def _process_changes(self):
        """Process detected changes and create/update ADRs."""
        for source, changes in self.detected_changes.items():
            for change in changes:
                if not self._adr_exists(change["type"]):
                    self._create_adr(change)
                else:
                    print(f"  ⏭️  ADR for {change['type']} already exists")

    def _create_adr(self, change: Dict[str, Any]):
        """Create a new ADR from detected change."""
        adr_number = self.next_adr_number
        self.next_adr_number += 1

        title = change["title"]
        date = datetime.now().strftime("%Y-%m-%d")

        # Extract rule references from change data
        rule_references = change.get("rule_references", [])
        if isinstance(rule_references, list):
            rule_refs_str = ", ".join(f"Rule-{r}" for r in rule_references)
        else:
            rule_refs_str = str(rule_references)

        adr_content = ADR_TEMPLATE.format(
            number=adr_number,
            title=title,
            context=change.get("context", "Context to be determined"),
            decision=change.get("decision", "Decision to be determined"),
            consequences=change.get("consequences", "Consequences to be determined"),
            verification=change.get(
                "verification",
                "- [ ] ADR implementation verified\n- [ ] Related rules updated\n- [ ] Documentation synchronized",
            ),
            related_rules=rule_refs_str,
            implementation_notes=change.get("implementation_notes", "Implementation details to be added"),
            date=date,
            status=change.get("status", "Proposed"),
            superseded_by=change.get("superseded_by", "000"),
            related_adrs=change.get("related_adrs", "None"),
            source=change.get("source", "Unknown"),
            rule_references=rule_refs_str,
        )

        # Ensure ADRs directory exists
        self.adrs_dir.mkdir(parents=True, exist_ok=True)

        # Write ADR file
        adr_filename = f"ADR-{adr_number:03d}-{self._slugify(title)}.md"
        adr_path = self.adrs_dir / adr_filename

        with open(adr_path, "w", encoding="utf-8") as f:
            f.write(adr_content)

        print(f"  📝 Created ADR-{adr_number:03d}: {title}")

    def _slugify(self, text: str) -> str:
        """Convert text to URL-friendly slug."""
        return re.sub(r"[^\w\-]", "-", text.lower()).strip("-")


def main():
    """Main entry point."""
    manager = ADRManager()
    success = manager.run_housekeeping()

    if success:
        print("\n✅ ADR housekeeping completed successfully")
    else:
        print("\nℹ️  ADR housekeeping found no changes")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
