# ADR-055: Auto-Docs Sync CI Enforcement

## Status
Proposed

## Decision
Add CI check for docs sync post-change (Rule 055)

## Context
Documentation synchronization gaps have occurred when manual docs passes are skipped. This leads to outdated AGENTS.md files, missing rule references, and forest overview inconsistencies.

## Decision
Implement Rule 055 (Auto-Docs Sync Pass) requiring comprehensive docs pass after every change/PR. CI will enforce via rules_guard.py validation.

## Related Rules
027, 055

## Consequences
- Mandatory docs synchronization prevents governance gaps
- CI enforcement ensures no bypass of documentation requirements
- Comprehensive validation covers AGENTS.md variants, rule cross-references, and forest regeneration
