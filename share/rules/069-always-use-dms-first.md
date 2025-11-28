# Rule-069: Always Use DMS First (Planning Queries)

**Last Updated:** 2025-11-22  
**Status:** Active (Governance)

## Summary

Enforces that all planning queries ("what's next?", "what should I work on?") MUST use `pmagent plan kb list` BEFORE manually searching documentation files. Prevents the exact mistake that occurred in this session where the agent manually searched MASTER_PLAN.md, NEXT_STEPS.md, and task.md instead of using the DMS system.

## Rule Location

- Primary: `.cursor/rules/069-always-use-dms-first.mdc`
- Referenced in: `docs/SSOT/PM_CONTRACT.md` (section 2.4.3)

## Required Workflow

1. Run `pmagent plan kb list` FIRST
2. Check worklist for actionable items
3. ONLY search manual docs if DMS returns no guidance
4. Document why manual search was needed

## Integration

- **PM Contract**: Added CRITICAL callout before file search section
- **Rule File**: Created `.cursor/rules/069-always-use-dms-first.mdc`
- **AlwaysApply**: Marked with sentinel for governance enforcement

## Why This Matters

The incident that triggered this rule:
- User asked "what's next after Phase 10?"
- Agent manually searched 4+ documents
- Found conflicting information
- User pointed out this is exactly what DMS is supposed to fix
- Created Rule-069 to prevent recurrence

## Enforcement

- Hermetic CI will validate DMS query before planning decisions
- PM review flags conversations that skip DMS
- Loud failure if DMS skipped without justification

---

**Related:**
- Rule-053 (PM↔DMS Integration) - defines the DMS ecosystem
- Rule-069 - enforces agents actually USE the DMS
