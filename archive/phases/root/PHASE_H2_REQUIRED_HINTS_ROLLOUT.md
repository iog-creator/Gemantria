# Phase H2 – Required Hints Rollout Plan

## Status
Draft - Awaiting PM Review

## Overview

Small, targeted rollout to migrate a high-value subset of hardcoded hints into the DMS hint registry as REQUIRED hints. Focus on critical behaviors that must be enforced contractually (DMS-only, local gates primary, no silent fallbacks).

## Goals

1. **Migrate 3-5 critical REQUIRED hints** from hardcoded strings to DMS
2. **Remove hardcoded copies** once DMS hints are verified working
3. **Keep changes tightly scoped** - no global refactor
4. **Verify guard enforcement** - ensure `guard.hints.required` passes for all affected flows

## Prerequisites

- [x] DMS hint registry infrastructure complete (Phase H1)
- [x] Migration 054 applied
- [x] Initial 3 hints seeded
- [ ] Discovery catalog generated (`share/governance/hints_catalog.json`)
- [ ] Baseline verification complete (local gates passing)

## Target Hints (High-Value, Small Set)

### 1. DMS-Only Behavior (Already Seeded)
- **Logical Name**: `docs.dms_only`
- **Scope**: `handoff`
- **Flow**: `handoff.generate`
- **Status**: ✅ Already in registry
- **Hardcoded Location**: `scripts/prepare_handoff.py` (handoff structure)
- **Action**: Verify present, remove hardcoded copy

### 2. Local Gates Primary
- **Logical Name**: `status.local_gates_first`
- **Scope**: `status_api`
- **Flow**: `status_snapshot`
- **Status**: ✅ Already in registry
- **Hardcoded Location**: `pmagent/reality/check.py`, `pmagent/status/snapshot.py`
- **Action**: Verify present, remove hardcoded copy

### 3. Share Sync DMS-Only
- **Logical Name**: `share.dms_only`
- **Scope**: `handoff`
- **Flow**: `handoff.generate`
- **Status**: ✅ Already in registry
- **Hardcoded Location**: `scripts/prepare_handoff.py`, `scripts/sync_share.py` (docstrings)
- **Action**: Verify present, remove hardcoded copy

### 4. No Silent Fallbacks (New - To Be Added)
- **Logical Name**: `governance.fail_closed`
- **Scope**: `handoff`
- **Flow**: `handoff.generate`
- **Status**: ⏳ To be added
- **Hardcoded Location**: `scripts/sync_share.py`, `scripts/governance/*.py`
- **Action**: Add to registry, remove hardcoded copy

### 5. Reality Green Requirements (New - To Be Added)
- **Logical Name**: `reality.green.required_checks`
- **Scope**: `status_api`
- **Flow**: `reality_check`
- **Status**: ⏳ To be added
- **Hardcoded Location**: `pmagent/reality/check.py`, `scripts/guards/guard_reality_green.py`
- **Action**: Add to registry, remove hardcoded copy

## Implementation Steps

### Step 1: Baseline Verification
**Status**: Not Started

Run local gates to ensure system is stable:
```bash
ruff format --check . && ruff check .
make book.smoke
make ci.exports.smoke
make reality.green STRICT
```

**Acceptance**: All gates pass

### Step 2: Discovery Catalog Generation
**Status**: Not Started

Run discovery script in report-only mode:
```bash
python scripts/governance/discover_hints.py --output share/governance/hints_catalog.json
```

**Acceptance**: 
- Catalog file exists at `share/governance/hints_catalog.json`
- Catalog contains list of all hardcoded hints with source locations

### Step 3: DB State Check
**Status**: Not Started

Query current hint registry state:
```python
# Check total hints, by kind, by scope
SELECT count(*) FROM control.hint_registry;
SELECT kind, count(*) FROM control.hint_registry GROUP BY kind;
SELECT scope, count(*) FROM control.hint_registry GROUP BY scope;
```

**Acceptance**: 
- Current state documented
- Baseline established for comparison

### Step 4: Add Missing REQUIRED Hints
**Status**: Not Started

Add hints #4 and #5 to registry:
```python
# Hint 4: governance.fail_closed
{
    "logical_name": "governance.fail_closed",
    "scope": "handoff",
    "applies_to": {"flow": "handoff.generate"},
    "kind": "REQUIRED",
    "injection_mode": "PRE_PROMPT",
    "payload": {
        "text": "Governance scripts must fail-closed on errors. No silent fallbacks.",
        "commands": [],
        "constraints": {"rule_ref": "039", "fail_closed": True},
        "metadata": {"source": "Rule-039", "agent_file": "AGENTS.md"}
    },
    "priority": 5
}

# Hint 5: reality.green.required_checks
{
    "logical_name": "reality.green.required_checks",
    "scope": "status_api",
    "applies_to": {"flow": "reality_check"},
    "kind": "REQUIRED",
    "injection_mode": "PRE_PROMPT",
    "payload": {
        "text": "reality.green STRICT must pass all required checks before declaring system ready.",
        "commands": ["make reality.green STRICT"],
        "constraints": {"rule_ref": "050", "required_before": "PR"},
        "metadata": {"source": "Rule-050", "section": "5"}
    },
    "priority": 10
}
```

**Acceptance**: 
- Both hints added to registry
- Verified via DB query

### Step 5: Verify Hints in Envelopes
**Status**: Not Started

Test that hints appear in generated envelopes:
```bash
# Test handoff envelope
python scripts/prepare_handoff.py > /tmp/handoff_test.md
grep -i "DMS-only\|local gates\|fail-closed" /tmp/handoff_test.md

# Test capability_session envelope
pmagent plan next --with-status > /tmp/capability_test.json
jq '.required_hints' /tmp/capability_test.json

# Test reality_check envelope
pmagent reality-check check --mode STRICT > /tmp/reality_test.json
jq '.required_hints' /tmp/reality_test.json
```

**Acceptance**: 
- All REQUIRED hints appear in their respective envelopes
- Hints are properly formatted and embedded

### Step 6: Verify Guard Enforcement
**Status**: Not Started

Test guard with actual envelope files:
```bash
# Test handoff guard
python scripts/guards/hints_required.py \
    --flow handoff.generate \
    --envelope share/handoff_latest.md \
    --mode STRICT

# Test reality_check guard
python scripts/guards/hints_required.py \
    --flow reality_check \
    --envelope evidence/pmagent/reality_check_latest.json \
    --mode STRICT
```

**Acceptance**: 
- Guard passes for all flows in STRICT mode
- Missing hints are detected and reported

### Step 7: Remove Hardcoded Copies
**Status**: Not Started

Remove hardcoded hint strings from:
- `scripts/prepare_handoff.py` - Remove DMS-only and share.dms_only strings
- `pmagent/reality/check.py` - Remove local gates primary strings
- `pmagent/status/snapshot.py` - Remove local gates primary strings
- `scripts/sync_share.py` - Remove DMS-only docstring references (keep technical docs)
- `scripts/governance/*.py` - Remove fail-closed hint strings

**Acceptance**: 
- No hardcoded hint strings remain in target files
- All hints loaded from DMS via `load_hints_for_flow()`
- Envelopes still contain hints (verified via guard)

### Step 8: Final Verification
**Status**: Not Started

Run full verification suite:
```bash
# Local gates
ruff format --check . && ruff check .
make book.smoke
make ci.exports.smoke

# Reality green with hints check
make reality.green STRICT

# Guard tests
python scripts/guards/hints_required.py --flow handoff.generate --envelope share/handoff_latest.md --mode STRICT
python scripts/guards/hints_required.py --flow reality_check --envelope evidence/pmagent/reality_check_latest.json --mode STRICT
```

**Acceptance**: 
- All gates pass
- All guards pass
- System behavior unchanged (hints still present, now from DMS)

## Files to Modify

### New Files
- `docs/PHASE_H2_REQUIRED_HINTS_ROLLOUT.md` (this file)

### Modified Files
- `scripts/governance/discover_hints.py` - Add `--output` flag
- `scripts/prepare_handoff.py` - Remove hardcoded DMS-only hints
- `pmagent/reality/check.py` - Remove hardcoded local gates hints
- `pmagent/status/snapshot.py` - Remove hardcoded local gates hints
- `scripts/sync_share.py` - Clean up docstring references (keep technical docs)

### Registry Updates
- Add `governance.fail_closed` hint
- Add `reality.green.required_checks` hint

## Acceptance Criteria

1. ✅ Discovery catalog generated and reviewed
2. ✅ 5 REQUIRED hints in registry (3 existing + 2 new)
3. ✅ All hints appear in their respective envelopes
4. ✅ Guard passes for all flows in STRICT mode
5. ✅ Hardcoded copies removed from target files
6. ✅ All local gates pass
7. ✅ System behavior unchanged (hints still work, now from DMS)

## Risks & Mitigation

### Risk: Removing hardcoded hints breaks envelope generation
**Mitigation**: 
- Verify hints in envelopes before removing hardcoded copies
- Keep parallel behavior during transition
- Test guard enforcement before removal

### Risk: Guard fails due to missing hints
**Mitigation**: 
- Test guard with actual envelope files before final verification
- Ensure all REQUIRED hints are seeded before guard enforcement
- Use HINT mode during transition, STRICT mode only after verification

### Risk: Discovery catalog incomplete
**Mitigation**: 
- Review discovery catalog manually
- Add any missing hints to catalog before seeding
- Verify catalog completeness against known hardcoded hints

## Next Steps After Phase H2

1. **Phase H3**: Migrate remaining SUGGESTED hints (lower priority)
2. **Phase H4**: Update rules/docs to reference DMS hint registry
3. **Phase H5**: Expand hint catalog based on operational learnings

## Notes

- **Small scope**: Only 5 hints in this phase (3 already seeded, 2 new)
- **High value**: Focus on critical behaviors that must be enforced
- **Low risk**: Changes are additive (add hints) then subtractive (remove hardcoded), with verification at each step
- **Incremental**: Can stop after any step if issues arise
