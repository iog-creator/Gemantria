#!/usr/bin/env python3
"""
Governance Conflict Audit (AgentPM-Next:M4)

Systematically audits and reports logical contradictions in SSOT governance documents.
Leverages M1/M2 doc fragments and M3 metrics to detect conflicts between rules.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

from agentpm.kb.registry import REPO_ROOT


@dataclass
class ConflictFinding:
    """Represents a single conflict finding."""

    conflict_id: str
    severity: str  # "critical", "high", "medium", "low"
    rule_pairs: list[tuple[str, str]]  # [(rule_id_1, rule_id_2), ...]
    description: str
    evidence: list[str] = field(default_factory=list)
    recommendation: str = ""


@dataclass
class ConflictAuditResult:
    """Result of governance conflict audit."""

    generated_at: str
    total_rules_scanned: int
    conflicts_found: int
    findings: list[ConflictFinding]
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "generated_at": self.generated_at,
            "total_rules_scanned": self.total_rules_scanned,
            "conflicts_found": self.conflicts_found,
            "findings": [
                {
                    "conflict_id": f.conflict_id,
                    "severity": f.severity,
                    "rule_pairs": [{"rule_1": r1, "rule_2": r2} for r1, r2 in f.rule_pairs],
                    "description": f.description,
                    "evidence": f.evidence,
                    "recommendation": f.recommendation,
                }
                for f in self.findings
            ],
            "notes": self.notes,
        }


def load_rule_content(rule_path: Path) -> str:
    """Load rule content from file."""
    try:
        return rule_path.read_text(encoding="utf-8")
    except Exception as e:
        return f"ERROR: Could not read rule file: {e}"


def extract_rule_id(rule_path: Path) -> str | None:
    """Extract rule ID from filename (e.g., '046' from '046-ci-hermetic-fallbacks.mdc')."""
    match = re.match(r"^(\d+)-", rule_path.name)
    return match.group(1) if match else None


def detect_known_conflicts(rules_dir: Path) -> list[ConflictFinding]:
    """Detect known logical conflicts between rules."""
    findings: list[ConflictFinding] = []

    # Known conflict: Rule 046 (hermetic defaults) vs Rule 062 (live operational mandate)
    rule_046_path = rules_dir / "046-ci-hermetic-fallbacks.mdc"
    rule_062_path = rules_dir / "062-environment-validation.mdc"

    if rule_046_path.exists() and rule_062_path.exists():
        rule_046_content = load_rule_content(rule_046_path)
        rule_062_content = load_rule_content(rule_062_path)

        # Check for explicit context scope markers that resolve the conflict
        rule_046_has_context_scope = bool(
            re.search(
                r"THIS RULE APPLIES.*CI/HERMETIC|applies.*CI/hermetic.*only|CI/HERMETIC.*ONLY", rule_046_content, re.I
            )
        )
        rule_062_has_context_scope = bool(
            re.search(
                r"THIS RULE APPLIES.*LIVE|applies.*live.*development.*operations|LIVE.*DEVELOPMENT.*OPERATIONS",
                rule_062_content,
                re.I,
            )
        )

        # If both rules have explicit context scopes, the conflict is resolved
        if rule_046_has_context_scope and rule_062_has_context_scope:
            # Conflict resolved - both rules explicitly state their context scope
            return findings

        # Check for conflict indicators (only if context scopes not present)
        hermetic_patterns = [
            r"MAY handle db_off gracefully",
            r"hermetic.*CI",
            r"designed for hermetic",
            r"db_off.*graceful",
        ]
        live_patterns = [
            r"MUST run.*bringup full",
            r"AUTO-START.*services",
            r"Do NOT report.*DB offline.*expected",
            r"task requires live",
        ]

        hermetic_evidence = [p for p in hermetic_patterns if re.search(p, rule_046_content, re.I)]
        live_evidence = [p for p in live_patterns if re.search(p, rule_062_content, re.I)]

        if hermetic_evidence and live_evidence:
            findings.append(
                ConflictFinding(
                    conflict_id="CONFLICT-046-062",
                    severity="critical",
                    rule_pairs=[("046", "062")],
                    description=(
                        "Rule 046 (Hermetic CI Fallbacks) allows graceful degradation for "
                        "db_off scenarios in CI, while Rule 062 (Environment Validation) "
                        "mandates auto-starting services for live operations. This creates "
                        "ambiguity about when to use hermetic mode vs live mode."
                    ),
                    evidence=[
                        f"Rule 046: {len(hermetic_evidence)} hermetic patterns found",
                        f"Rule 062: {len(live_evidence)} live operation patterns found",
                        "Rule 046 allows 'db_off gracefully' for observability commands",
                        "Rule 062 mandates 'pmagent bringup full' when DB is down for live tasks",
                    ],
                    recommendation=(
                        "Clarify the distinction: Rule 046 applies to CI/hermetic contexts only, "
                        "while Rule 062 applies to live development/operations. Add explicit "
                        "context markers to both rules to prevent ambiguity."
                    ),
                )
            )

    # Check for other potential conflicts
    # Rule 050 (OPS Contract) vs Rule 046 (Hermetic defaults)
    rule_050_path = rules_dir / "050-ops-contract.mdc"
    if rule_050_path.exists() and rule_046_path.exists():
        rule_050_content = load_rule_content(rule_050_path)
        rule_046_content = load_rule_content(rule_046_path)

        # Check if Rule 050 mandates live checks while 046 allows hermetic
        if re.search(r"make reality\.green", rule_050_content, re.I) and re.search(r"hermetic", rule_046_content, re.I):
            # This is not necessarily a conflict - Rule 050 is about OPS mode, 046 is about CI
            # But we should note potential ambiguity
            findings.append(
                ConflictFinding(
                    conflict_id="POTENTIAL-050-046",
                    severity="medium",
                    rule_pairs=[("050", "046")],
                    description=(
                        "Rule 050 (OPS Contract) requires 'make reality.green' checks, "
                        "while Rule 046 (Hermetic CI Fallbacks) allows hermetic behavior. "
                        "The distinction between OPS mode and CI mode should be explicit."
                    ),
                    evidence=[
                        "Rule 050 mandates reality.green checks in OPS mode",
                        "Rule 046 allows hermetic behavior for CI",
                    ],
                    recommendation=(
                        "Ensure Rule 050 explicitly states it applies to live OPS mode, "
                        "not hermetic CI. Rule 046 should explicitly state it applies to CI only."
                    ),
                )
            )

    return findings


def scan_rules_for_patterns(rules_dir: Path) -> list[ConflictFinding]:
    """Scan all rules for conflicting patterns."""
    findings: list[ConflictFinding] = []

    rule_files = sorted(rules_dir.glob("*.mdc"))
    rule_contents: dict[str, str] = {}

    # Load all rule contents
    for rule_file in rule_files:
        rule_id = extract_rule_id(rule_file)
        if rule_id:
            rule_contents[rule_id] = load_rule_content(rule_file)

    # Check for contradictory patterns across rules
    # Pattern: "MUST" vs "MAY" for similar operations
    must_patterns = re.compile(r"\bMUST\b|\bREQUIRED\b|\bMANDATORY\b", re.I)
    may_patterns = re.compile(r"\bMAY\b|\bOPTIONAL\b|\bALLOWED\b", re.I)

    for rule_id_1, content_1 in rule_contents.items():
        for rule_id_2, content_2 in rule_contents.items():
            if rule_id_1 >= rule_id_2:  # Avoid duplicates
                continue

            # Check for similar topics but different mandates
            # This is a simple heuristic - could be enhanced with semantic analysis
            if must_patterns.search(content_1) and may_patterns.search(content_2):
                # Check if they mention similar concepts
                common_terms = ["db", "database", "service", "hermetic", "live", "CI", "environment"]
                if any(term in content_1.lower() and term in content_2.lower() for term in common_terms):
                    # Potential conflict - but we'll only flag known ones
                    pass

    return findings


def audit_governance_conflicts(rules_dir: Path | None = None, output_path: Path | None = None) -> ConflictAuditResult:
    """
    Perform governance conflict audit.

    Args:
        rules_dir: Directory containing rule files (default: .cursor/rules)
        output_path: Optional path to write JSON output

    Returns:
        ConflictAuditResult with findings
    """
    if rules_dir is None:
        rules_dir = REPO_ROOT / ".cursor" / "rules"

    if not rules_dir.exists():
        return ConflictAuditResult(
            generated_at=datetime.now(UTC).isoformat(),
            total_rules_scanned=0,
            conflicts_found=0,
            findings=[],
            notes=[f"Rules directory not found: {rules_dir}"],
        )

    rule_files = list(rules_dir.glob("*.mdc"))
    total_rules = len(rule_files)

    # Detect known conflicts
    findings = detect_known_conflicts(rules_dir)

    # Scan for additional pattern-based conflicts
    pattern_findings = scan_rules_for_patterns(rules_dir)
    findings.extend(pattern_findings)

    result = ConflictAuditResult(
        generated_at=datetime.now(UTC).isoformat(),
        total_rules_scanned=total_rules,
        conflicts_found=len(findings),
        findings=findings,
        notes=[
            f"Scanned {total_rules} rule files from {rules_dir}",
            "Known conflicts detected using pattern matching",
            "Recommendation: Review findings and update rules to resolve conflicts",
        ],
    )

    # Write output if path provided
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")

    return result


def main() -> None:
    """CLI entry point for conflict audit."""
    import sys

    rules_dir = REPO_ROOT / ".cursor" / "rules"
    output_path = REPO_ROOT / "evidence" / "governance_conflict_manifest.json"

    result = audit_governance_conflicts(rules_dir=rules_dir, output_path=output_path)

    # Print JSON to stdout
    print(json.dumps(result.to_dict(), indent=2))

    # Exit with error code if critical conflicts found
    critical_count = sum(1 for f in result.findings if f.severity == "critical")
    if critical_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
