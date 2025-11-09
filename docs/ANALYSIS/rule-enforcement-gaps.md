# Rule Enforcement Gaps Analysis

**Date:** 2025-11-09  
**Context:** User had to explicitly request multiple steps that should have been automatic per rules  
**Scope:** Rule 058 (Auto-Housekeeping), Rule 026 (Hints Envelope), Rule 065 (GPT Docs Sync)

## Executive Summary

Despite having comprehensive rules defining mandatory post-change workflows, Cursor is not automatically executing them. The user had to explicitly request:
1. Running `make housekeeping` after changes
2. Building hints system for rule/docs changes
3. Following proper change workflows

**Root Cause:** Disconnect between rule definitions (`alwaysApply: false`, "MANDATORY" language) and Cursor's actual enforcement mechanisms.

---

## Problem 1: Rule 058 Not Auto-Applied

### Issue
- **Rule 058** states: "Mandatory run `make housekeeping` after every change/PR"
- **Reality:** Rule has `alwaysApply: false` in frontmatter
- **Impact:** Cursor doesn't automatically run housekeeping after file edits

### Evidence
```yaml
# .cursor/rules/058-auto-housekeeping.mdc
alwaysApply: false  # ❌ Should be true for automatic enforcement
```

### Root Cause
- Rule description says "AlwaysApply" but frontmatter contradicts
- No Cursor mechanism to automatically execute Makefile targets after edits
- Rule relies on developer memory rather than system enforcement

### Solution
1. **Change frontmatter** to `alwaysApply: true` (if Cursor supports this)
2. **Add explicit reminder** in rule: "Cursor MUST run `make housekeeping` after ANY file edit"
3. **Create pre-commit hook** as fallback enforcement (Rule 026 mentions this)
4. **Add CI check** that validates housekeeping was run (check for evidence files)

---

## Problem 2: Hints System Not Automatic

### Issue
- **Rule 026** (Hints Envelope) exists but hints weren't considered for rule/docs changes
- **Rule 065** was created without thinking about hints integration
- **Impact:** Hints system had to be built reactively instead of proactively

### Evidence
- User asked: "did you build the hints in for this?"
- Hints system was added AFTER Rule 065 was created
- No automatic connection between rule creation and hints emission

### Root Cause
- Rule 026 says `alwaysApply: false`
- No systematic check: "When creating/modifying rules, check if hints are needed"
- Hints are mentioned in rules but not integrated into change workflows

### Solution
1. **Update Rule 026** to explicitly state: "When creating/modifying rules or docs, automatically consider hints"
2. **Add checklist** to Rule 065: "Before finalizing rule/docs changes, verify hints are emitted"
3. **Wire hints into housekeeping** (✅ DONE - `governance.docs.hints` target)
4. **Add reminder pattern**: When editing `.cursor/rules/*.mdc` or `docs/SSOT/*.md`, automatically check for hints

---

## Problem 3: Change Workflow Not Followed

### Issue
- **Rule 058** defines mandatory steps after changes
- **Rule 030** requires share sync after docs/rules changes
- **Reality:** User had to ask: "did you properly follow rules on how to make changes?"

### Evidence
- Multiple commits without running housekeeping
- Share sync happened but wasn't automatic
- No systematic verification of rule compliance

### Root Cause
- Rules define "MANDATORY" but Cursor doesn't enforce automatically
- No checklist or workflow reminder system
- Relies on agent memory rather than systematic checks

### Solution
1. **Create change workflow checklist** that Cursor must follow:
   ```
   After ANY file edit:
   - [ ] Run `make housekeeping`
   - [ ] Check if hints needed (Rule 026)
   - [ ] Verify share sync (Rule 030)
   - [ ] Check related rules for updates (Rule 065, etc.)
   ```
2. **Add to Rule 050** (OPS Contract): Explicit checklist in "Evidence-First Protocol"
3. **Create reminder script**: `scripts/verify_post_change.sh` that checks all requirements

---

## Problem 4: Rule Interdependencies Not Checked

### Issue
- Created Rule 065 without checking Rule 026 (Hints Envelope)
- Modified `governance_tracker.py` without checking Rule 046 (Hermetic Fallbacks)
- **Impact:** Related rules not considered, leading to incomplete implementations

### Root Cause
- No systematic rule dependency checking
- Rules exist in isolation rather than as a system
- No "related rules" validation when creating/modifying rules

### Solution
1. **Add rule dependency graph** to `RULES_INDEX.md`
2. **Create rule checker**: When modifying a rule, check all rules in "Related Rules" section
3. **Add to Rule 008** (Cursor Rule Authoring): "Before finalizing, check all Related Rules sections"

---

## Problem 5: `alwaysApply: false` Contradicts "AlwaysApply" Language

### Issue
- Multiple rules say "AlwaysApply" in title but have `alwaysApply: false` in frontmatter
- Creates confusion about when rules are actually applied
- **Impact:** Rules that should be automatic aren't

### Evidence
```yaml
# Rule 058
alwaysApply: false  # But title says "AlwaysApply"

# Rule 026  
alwaysApply: false  # But should apply when creating rules/docs
```

### Root Cause
- Frontmatter `alwaysApply` may not work as expected in Cursor
- Rules use "AlwaysApply" as emphasis rather than technical directive
- No clear documentation on what `alwaysApply: true` actually does

### Solution
1. **Audit all rules** for `alwaysApply` vs. "AlwaysApply" language mismatch
2. **Document Cursor behavior**: What does `alwaysApply: true` actually do?
3. **Standardize**: Either use `alwaysApply: true` for automatic rules OR remove the frontmatter and rely on explicit reminders
4. **Add enforcement layer**: If Cursor doesn't auto-apply, add explicit checklists

---

## Comprehensive Solutions

### Solution 1: Fix Rule 058 Frontmatter and Add Explicit Reminder

```yaml
# .cursor/rules/058-auto-housekeeping.mdc
alwaysApply: true  # Change to true
description: Mandatory run `make housekeeping` after every change/PR...
```

Add to rule body:
```markdown
## Cursor Enforcement

**CRITICAL**: After ANY file edit in this repository, Cursor MUST:
1. Run `make housekeeping` automatically
2. Verify housekeeping completed successfully
3. Commit any generated files (share/, evidence/, etc.)
4. If housekeeping fails, stop and report error

This is non-negotiable. Do not proceed without running housekeeping.
```

### Solution 2: Create Post-Change Verification Script

```bash
#!/bin/bash
# scripts/verify_post_change.sh

echo "🔍 Verifying post-change requirements..."

# Check if housekeeping was run (look for evidence files)
if [ ! -f "evidence/governance_docs_hints.json" ] && git diff --name-only | grep -qE "(\.cursor/rules|docs/SSOT|AGENTS\.md)"; then
    echo "❌ Housekeeping not run after rule/docs changes"
    exit 1
fi

# Check share sync
if git diff --name-only | grep -qE "(docs/|scripts/|\.cursor/rules)" && ! git diff --name-only | grep -q "share/"; then
    echo "⚠️  WARNING: Share sync may be needed (Rule 030)"
fi

echo "✅ Post-change verification complete"
```

### Solution 3: Add Explicit Checklist to Rule 050

Update Rule 050 "Evidence-First Protocol" section:

```markdown
## 5 · Evidence-First Protocol

Before proposing changes:

```bash
# ... existing commands ...
```

**After making changes, Cursor MUST:**

1. **Run housekeeping**: `make housekeeping` (Rule 058)
2. **Check hints**: Verify hints emitted if rule/docs changed (Rule 026)
3. **Verify share sync**: Check `share/` updated (Rule 030)
4. **Check related rules**: Review "Related Rules" sections for updates needed
5. **Commit generated files**: Share sync, evidence, forest updates, etc.

**DO NOT** commit changes without completing this checklist.
```

### Solution 4: Create Rule Dependency Checker

```python
# scripts/check_rule_dependencies.py
"""
When modifying a rule, check all rules in its "Related Rules" section
to ensure interdependencies are maintained.
"""

def check_rule_dependencies(rule_file: Path):
    # Parse rule file
    # Extract "Related Rules" section
    # Check each related rule for consistency
    # Emit hints if inconsistencies found
    pass
```

### Solution 5: Update Rule 008 (Rule Authoring) with Checklist

Add to Rule 008:

```markdown
## Pre-Finalization Checklist

Before finalizing any rule change:

- [ ] Check all "Related Rules" sections for updates needed
- [ ] Verify `alwaysApply` frontmatter matches rule intent
- [ ] Add hints emission if rule affects operational behavior (Rule 026)
- [ ] Update `RULES_INDEX.md` if rule number/name changes
- [ ] Run `make housekeeping` after rule changes (Rule 058)
- [ ] Verify share sync updated (Rule 030)
```

---

## Implementation Priority

1. **P0 (Immediate)**: Fix Rule 058 frontmatter + add explicit reminder
2. **P0 (Immediate)**: Add checklist to Rule 050 "Evidence-First Protocol"
3. **P1 (This Week)**: Create `verify_post_change.sh` script
4. **P1 (This Week)**: Update Rule 008 with pre-finalization checklist
5. **P2 (Next Sprint)**: Create rule dependency checker
6. **P2 (Next Sprint)**: Audit all rules for `alwaysApply` consistency

---

## Testing

After implementing solutions:

1. **Test 1**: Create a new rule file → Verify housekeeping runs automatically
2. **Test 2**: Modify `AGENTS.md` → Verify share sync happens
3. **Test 3**: Update a rule → Verify hints are emitted
4. **Test 4**: Make code change → Verify checklist is followed

---

## Related Rules

- **Rule 050**: OPS Contract (evidence-first protocol)
- **Rule 058**: Auto-Housekeeping (mandatory execution)
- **Rule 026**: System Enforcement Bridge (hints envelope)
- **Rule 030**: Share Sync (mandatory after changes)
- **Rule 008**: Cursor Rule Authoring (rule creation guidelines)
- **Rule 065**: GPT Documentation Sync (hints integration)

---

## Notes

- Cursor's `alwaysApply` frontmatter may not work as expected - need to verify actual behavior
- Consider adding explicit reminders in rule bodies rather than relying on frontmatter
- Pre-commit hooks and CI checks provide fallback enforcement if Cursor doesn't auto-apply
- This analysis should be reviewed and updated as Cursor's rule enforcement capabilities evolve

