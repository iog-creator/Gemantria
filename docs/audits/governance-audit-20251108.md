# Governance Audit Report — 2025-11-08

**Audit Scope:** AGENTS.md, RULES_INDEX.md, .cursor/rules triad (050/051/052), folder-scoped AGENTS.md files, and related documentation  
**Auditor:** Cursor (OPS v6.2.3)  
**Status:** ✅ PASSED with 3 MINOR findings requiring updates

---

## Executive Summary

The governance system is **operationally correct** with the Always-Apply triad properly locked to Rules 050/051/052. Three minor documentation discrepancies were found that require updates to maintain consistency:

1. **ADR-013** contains outdated `alwaysApply: true` reference (actual rule file is correct)
2. **docs/forest/overview.md** doesn't note status change for Rules 062/063
3. **Root AGENTS.md** rules inventory shows "---" placeholders instead of actual rule status

---

## ✅ Verified Correct

### 1. Always-Apply Triad (050/051/052)

**Status:** ✅ CORRECT

All three rules properly configured:

```yaml
# .cursor/rules/050-ops-contract.mdc
alwaysApply: true  ✅

# .cursor/rules/051-cursor-insight.mdc
alwaysApply: true  ✅

# .cursor/rules/052-tool-priority.mdc
alwaysApply: true  ✅
```

**References in root AGENTS.md:**
- Line 196: "automated review is advisory per AGENTS.md and RULE 051." ✅
- Line 349: "Always-Apply triad lives in `.cursor/rules/050...051...052.mdc`" ✅
- Lines 409-411: Rules inventory correctly shows triad as "AlwaysApply" ✅
- Line 836: "Authority chain: Rules 039 → 041 → 046 → 050 → 051 → 052" ✅
- Line 1085: "Always-Apply: 050 (OPS/SSOT), 051 (Required-checks), 052 (Tool-priority)" ✅

### 2. Former Always-Apply Rules (006, 010, 030, 062, 063)

**Status:** ✅ CORRECT

All five rules properly set to `alwaysApply: false`:

```yaml
# Verified correct in .cursor/rules/*.mdc files
006-agents-md-governance.mdc: alwaysApply: false  ✅
010-task-brief.mdc: alwaysApply: false  ✅
030-share-sync.mdc: alwaysApply: false  ✅
062-environment-validation.mdc: alwaysApply: false  ✅
063-git-safety.mdc: alwaysApply: false  ✅
```

### 3. Folder-Scoped AGENTS.md Files

**Status:** ✅ CORRECT

All folder-scoped AGENTS.md files properly created with appropriate headers:

```
✅ docs/adr/AGENTS.md
✅ docs/audits/AGENTS.md
✅ docs/consumers/AGENTS.md
✅ docs/forest/AGENTS.md
✅ docs/ingestion/AGENTS.md
✅ docs/phase9/AGENTS.md
✅ docs/phase10/AGENTS.md
✅ docs/runbooks/AGENTS.md
✅ docs/schema/AGENTS.md
✅ docs/tickets/AGENTS.md
✅ src/graph/AGENTS.md
✅ src/persist/AGENTS.md
✅ src/rerank/AGENTS.md
✅ src/services/AGENTS.md
✅ src/ssot/AGENTS.md
```

**Verification:**
- Root AGENTS.md does NOT contain folder-scoped headers ✅
- Folder files use proper "# AGENTS.md - {directory} Directory" format ✅
- `scripts/create_agents_md.py` now excludes `__pycache__` and `node_modules` ✅

### 4. Share Sync

**Status:** ✅ CORRECT

Share directory mirrors are current:
- `share/AGENTS.md` (46K, synced 2025-11-08 11:54) ✅
- `share/RULES_INDEX.md` (3.7K, synced 2025-11-08 11:49) ✅

### 5. Makefile Targets

**Status:** ✅ CORRECT

Governance targets properly wired:
- `agents.md.lint` target exists (line 772) ✅
- `ops.verify` depends on `agents.md.lint guards.all` (line 775) ✅
- `agents.md.index` optional DB index target exists (line 779) ✅

### 6. CI Workflow

**Status:** ✅ CORRECT

New CI workflow properly configured:
- `.github/workflows/agents-md-lint.yml` exists ✅
- HINT mode on PRs (non-fatal) ✅
- STRICT mode on tags (fatal) ✅

---

## ⚠️ Findings Requiring Updates

### Finding 1: ADR-013 Contains Outdated alwaysApply Reference

**Location:** `docs/ADRs/ADR-013-documentation-sync-enhancement.md:58`

**Issue:** Document shows `alwaysApply: true` in example/template, but the actual rule file (009-documentation-sync.mdc) has `alwaysApply: false`.

**Current State:**
```yaml
# docs/ADRs/ADR-013-documentation-sync-enhancement.md
alwaysApply: true  ❌ STALE
```

**Actual Rule File:**
```yaml
# .cursor/rules/009-documentation-sync.mdc
alwaysApply: false  ✅ CORRECT
```

**Recommendation:** Update ADR-013 to reflect that Rule 009 is now Default-Apply, not Always-Apply. Add a note that the triad (050/051/052) are the only Always-Apply rules.

**Impact:** LOW — Documentation drift only; actual rule behavior is correct.

---

### Finding 2: Forest Overview Shows "---" for Rules 062/063

**Location:** `docs/forest/overview.md:72-73`

**Issue:** Rules 062 and 063 show as "---" without noting they changed from alwaysApply: true to alwaysApply: false during triad enforcement.

**Current State:**
```
- Rule 062-environment-validation: ---
- Rule 063-git-safety: ---
```

**Recommendation:** Update forest overview to show actual status:
```
- Rule 062-environment-validation: (Default-Apply, formerly alwaysApply)
- Rule 063-git-safety: (Default-Apply, formerly alwaysApply)
```

**Impact:** LOW — Informational drift; rules are correctly configured.

---

### Finding 3: Root AGENTS.md Rules Inventory Shows "---" Placeholders

**Location:** `AGENTS.md:~409-411` (rules inventory table)

**Issue:** The rules inventory table in root AGENTS.md shows many rules as "---" instead of their actual status (e.g., Default-Apply, agent-requested, deprecated).

**Current State:**
```markdown
| 006 | # --- |
| 010 | # --- |
| 030 | # --- |
| 062 | # --- |
| 063 | # --- |
```

**Expected State:**
```markdown
| 006 | # 006-agents-md-governance (Default-Apply) |
| 010 | # 010-task-brief (Default-Apply) |
| 030 | # 030-share-sync (Default-Apply) |
| 062 | # 062-environment-validation (Default-Apply) |
| 063 | # 063-git-safety (Default-Apply) |
```

**Recommendation:** Run `make housekeeping` or regenerate the rules inventory to populate actual status for all rules.

**Impact:** MEDIUM — Makes it harder to understand which rules are active/deprecated without checking individual files.

---

## Summary of Recommendations

### Immediate (Before Next PR)

1. **Update ADR-013** to note Rule 009 is Default-Apply, not Always-Apply
2. **Regenerate forest overview** with proper status for Rules 062/063
3. **Update root AGENTS.md rules inventory** with actual rule status (not "---" placeholders)

### Commands to Execute

```bash
# 1) Update forest
make generate.forest

# 2) Update AGENTS.md rules inventory
python scripts/update_rules_inventory.py  # If this script exists
# OR manually update RULES_INVENTORY_START...END block in AGENTS.md

# 3) Update ADR-013
# (Manual edit required to note triad enforcement)

# 4) Sync share
make share.sync

# 5) Commit changes
git add docs/forest/overview.md docs/ADRs/ADR-013-*.md AGENTS.md share/
git commit -m "docs(audit): fix governance audit findings (ADR-013, forest, inventory)"
```

---

## Acceptance Criteria

- [ ] ADR-013 notes Rule 009 is Default-Apply
- [ ] Forest overview shows Rules 062/063 as Default-Apply (formerly alwaysApply)
- [ ] Root AGENTS.md rules inventory shows actual status (not "---")
- [ ] Share directory synced after changes
- [ ] No conflicting references to triad remain

---

## Audit Methodology

1. Read root `AGENTS.md`, `RULES_INDEX.md`
2. Verify all `.cursor/rules/*.mdc` alwaysApply flags
3. Grep for triad references across docs/forest, docs/ADRs, AGENTS.md
4. Check folder-scoped AGENTS.md headers and root bloat
5. Verify share/ mirrors current
6. Cross-reference forest overview with actual rule files

---

## Conclusion

The governance system is **operationally sound** with the triad properly enforced. The three findings are **documentation drift** issues that do not affect runtime behavior. Fixing them will restore full consistency across the documentation set.

**Overall Grade:** ✅ PASS with 3 MINOR updates required

