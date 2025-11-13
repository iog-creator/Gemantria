# AGENTS.md - Tickets Directory

## Directory Purpose

The `docs/tickets/` directory contains documentation for issue tracking, bug fixes, and feature implementation tickets. This directory documents specific technical issues, their resolutions, and implementation details for reference and knowledge sharing.

## Key Documents

### Ticket Documentation

- **ENRICH-JSON-REPAIR.md** - JSON Repair for Enrichment Outputs
  - Documents JSON repair procedures for LLM enrichment outputs
  - Specifies repair strategies for malformed JSON responses
  - Provides validation and acceptance criteria for repaired JSON
  - Links to related scripts and utilities

## Documentation Standards

### Ticket Documentation Format

All ticket documentation should include:

1. **Issue Description** - What problem is being addressed
2. **Root Cause** - Why the issue occurred
3. **Solution** - How the issue is resolved
4. **Implementation** - Code changes, scripts, or procedures
5. **Verification** - How to verify the fix works

### Ticket Naming Convention

- **Topic-based**: `ENRICH-JSON-REPAIR.md`, `[TOPIC]-[ACTION].md`
- **Issue-based**: `ISSUE-[NUMBER]-[DESCRIPTION].md`
- **Feature-based**: `FEATURE-[NAME]-[DESCRIPTION].md`

## Development Guidelines

### Creating Ticket Documentation

1. **Document issue**: Clearly describe the problem being addressed
2. **Root cause**: Explain why the issue occurred
3. **Solution**: Document the fix or implementation approach
4. **Code references**: Link to relevant scripts, functions, or files
5. **Verification**: Provide steps to verify the fix

### Ticket Resolution Standards

- **Code changes**: Document all code modifications
- **Script updates**: Note any script or Makefile target changes
- **Schema changes**: Document any data format or schema modifications
- **Testing**: Include test procedures and acceptance criteria

## Related Documentation

### Issue Tracking

- **GitHub Issues**: Link to GitHub issues when applicable
- **PR references**: Reference pull requests that implement fixes
- **ADR references**: Link to ADRs if architectural decisions are involved

### Related Scripts

- **src/utils/json_sanitize.py**: JSON sanitization utilities
- **scripts/eval/**: Evaluation and validation scripts
- **tests/**: Test files that verify fixes

## Integration with Governance

### Rule 040 - CI Triage Playbook

Ticket documentation supports incident triage:

- **Root cause analysis**: Documents why issues occurred
- **Fix procedures**: Provides step-by-step resolution steps
- **Prevention**: Notes how to prevent similar issues

### Rule 009 - Documentation Sync

Ticket documentation must be kept current:

- **Update on fix**: Document fixes when issues are resolved
- **Link to code**: Maintain links to relevant code changes
- **Archive resolved**: Move resolved tickets to archive if applicable

## Maintenance Notes

- **Keep current**: Update ticket docs when issues are resolved
- **Link to code**: Maintain links to relevant scripts and functions
- **Archive old**: Move resolved tickets to archive directory if applicable
- **Cross-reference**: Link to related issues, PRs, and ADRs
