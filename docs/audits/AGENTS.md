# AGENTS.md - Audits Directory

## Directory Purpose

The `docs/audits/` directory contains audit reports and documentation for system audits, compliance checks, and governance validation. These audits verify system integrity, rule compliance, and documentation quality.

## Key Documents

### Audit Reports

- **AGENTS_MD_AUDIT_20251112.md** - Comprehensive audit of all AGENTS.md files across the repository
  - Documents audit findings, compliance status, and recommendations
  - Tracks documentation quality metrics and completion status
  - Provides implementation plan for remaining stub files

- **AUDIT_DB_ORIGINALS.md** - Pipeline Integration Acceptance Audit (2025-11-04)
  - Verifies schema separation (bible_db read-only, gematria write-side)
  - Confirms governance compliance (OPS v6.2.3)
  - Documents integration verification (7 tasks verified)

- **governance-audit-20251108.md** - Governance System Audit Report
  - Verifies Always-Apply triad (Rules 050/051/052) configuration
  - Checks AGENTS.md, RULES_INDEX.md, and folder-scoped AGENTS.md files
  - Documents minor findings requiring documentation updates

## Documentation Standards

### Audit Report Format

All audit reports should include:

1. **Executive Summary** - High-level findings and status
2. **Scope** - What was audited and verification criteria
3. **Findings** - Detailed results organized by category
4. **Recommendations** - Action items and improvement suggestions
5. **Evidence** - Links to supporting documentation and artifacts

### Audit Naming Convention

- **Date-based**: `AGENTS_MD_AUDIT_YYYYMMDD.md`, `governance-audit-YYYYMMDD.md`
- **Topic-based**: `AUDIT_DB_ORIGINALS.md`, `AUDIT_[TOPIC].md`
- **Status tracking**: Include status (PASSED, FAILED, IN_PROGRESS) in report header

## Development Guidelines

### Conducting Audits

1. **Define scope**: Clearly specify what is being audited
2. **Establish criteria**: Define pass/fail conditions and quality metrics
3. **Collect evidence**: Gather supporting documentation and artifacts
4. **Document findings**: Record all findings with severity and recommendations
5. **Archive evidence**: Store audit artifacts in `share/evidence/` or evidence branches

### Audit Types

- **Documentation audits**: Verify AGENTS.md completeness, rule compliance, SSOT accuracy
- **Governance audits**: Verify rule configuration, Always-Apply triad, documentation sync
- **Integration audits**: Verify system integration, schema compliance, DSN usage
- **Quality audits**: Verify code quality, test coverage, lint compliance

### Audit Frequency

- **Documentation audits**: Quarterly or after major documentation changes
- **Governance audits**: After rule changes or governance framework updates
- **Integration audits**: After major system changes or schema migrations
- **Quality audits**: Continuous (CI/CD) and periodic comprehensive reviews

## Related ADRs

| Document | Related ADRs | Status |
|----------|--------------|--------|
| AGENTS_MD_AUDIT_20251112.md | Rule 017 (Agent Docs Presence), Rule 006 (AGENTS.md Governance) | Complete |
| AUDIT_DB_ORIGINALS.md | ADR-001 (Two-DB Safety), Rule 001 (DB Safety) | Accepted |
| governance-audit-20251108.md | Rule 050 (OPS Contract), Rule 051 (Cursor Insight), Rule 052 (Tool Priority) | Passed |

## Integration with Governance

### Rule 017 - Agent Docs Presence

Audits verify compliance with Rule 017 requirements:

- **Required files**: Verify all required AGENTS.md files are present
- **Content quality**: Check documentation completeness and accuracy
- **Structure validation**: Verify AGENTS.md files follow standard format

### Rule 006 - AGENTS.md Governance

Audits ensure AGENTS.md files comply with governance standards:

- **Format compliance**: Verify standard structure and sections
- **Cross-references**: Check ADR linkages and related documentation
- **Maintenance**: Verify documentation is kept current with code changes

### Rule 050/051/052 - Always-Apply Triad

Governance audits verify Always-Apply triad configuration:

- **Rule configuration**: Verify alwaysApply: true in rule files
- **Documentation references**: Check AGENTS.md references to triad
- **Consistency**: Ensure triad is consistently referenced across documentation

## Maintenance Notes

- **Archive old audits**: Keep historical audit reports for reference
- **Update audit templates**: Refine audit procedures based on findings
- **Track recommendations**: Monitor implementation of audit recommendations
- **Schedule regular audits**: Establish audit cadence for continuous compliance
