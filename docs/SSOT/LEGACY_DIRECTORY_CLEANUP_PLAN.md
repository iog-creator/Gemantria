# Legacy Directory Cleanup Plan — Phase 27.H Extension

**Status:** PLANNING  
**Owner:** PM + Cursor (OPS Mode)  
**Governance:** Gemantria OPS v6.2.3 (Rules 050, 051, 052 active)  
**Date:** 2025-12-07

---

## 1. Executive Summary

This plan systematically removes unused, stale, and legacy directories identified through DMS introspection and semantic inventory analysis. The cleanup is organized into **4 phases** with safety checks at each step.

**Total Impact:**
- **~25,000 files** across legacy directories
- **~1.5GB** of disk space
- **Improved repository hygiene** and reduced cognitive overhead

---

## 2. Directory Classification

### 2.1 Phase 1: Safe Delete (No Dependencies)

These directories are **clearly legacy** with no active references:

| Directory | Files | Size | Rationale | Action |
|-----------|-------|------|-----------|--------|
| `archive/` | 22,040 | 604M | Phase 16 legacy purge artifacts, already quarantined | **DELETE** |
| `backups/` | 1 | 298M | Single large legacy backup file | **DELETE** |
| `.pg/` | 1,936 | 55M | Postgres data dumps (should never be in repo) | **DELETE** |
| `tagproof/` | 8 | 476K | Tag proof artifacts (generated, not source) | **DELETE** |

**Total Phase 1:** ~24,000 files, ~957MB

### 2.2 Phase 2: Selective Cleanup (Check for Valuable Files)

These directories may contain some valuable files but are mostly legacy:

| Directory | Files | Size | Rationale | Action |
|-----------|-------|------|-----------|--------|
| `backup/` | 76 | 4.3M | Timestamped backups (legitimate but can be rotated) | **ROTATE** (keep last 10, delete older) |
| `examples/` | 3 | 28K | May contain legacy examples | **INVESTIGATE** → delete if legacy |
| `reports/` | 5 | 36K | May contain legacy reports | **INVESTIGATE** → delete if legacy |
| `agents/` | 1 | 8K | Unknown purpose | **INVESTIGATE** → delete if legacy |
| `build/` | 2 | 16K | Build artifacts | **DELETE** (should be gitignored) |
| `test-results/` | 1 | 8K | Test artifacts | **DELETE** (should be gitignored) |
| `var/` | 3 | 20K | Variable/temporary files | **DELETE** (should be gitignored) |

**Total Phase 2:** ~90 files, ~4.4MB

### 2.3 Phase 3: External Dependencies (Gitignore, Not Delete)

These are external dependencies that should be **gitignored** but not deleted (may be needed locally):

| Directory | Files | Size | Rationale | Action |
|-----------|-------|------|-----------|--------|
| `genai-toolbox/` | 1,073 | 595M | External dependency (should not be in git) | **GITIGNORE** (keep locally if needed) |

**Total Phase 3:** 1,073 files, 595MB (gitignored, not deleted)

### 2.4 Phase 4: Keep (Active or Minimal)

These directories are **active** or **minimal** and should be preserved:

| Directory | Files | Size | Rationale | Action |
|-----------|-------|------|-----------|--------|
| `oa/` | 3 | 12K | Phase 27.B scaffolding (minimal, active) | **KEEP** |

---

## 3. Execution Plan

### Phase 1: Safe Delete (No Dependencies)

**Pre-flight:**
1. Verify no references in:
   - `Makefile` targets
   - `scripts/` imports
   - `docs/SSOT/` documentation
   - DMS registry

**Execution:**
```bash
# Delete clearly legacy directories
rm -rf archive/
rm -rf backups/
rm -rf .pg/
rm -rf tagproof/
```

**Verification:**
- `git status` shows deletions
- `make ops.kernel.check` still passes
- `make reality.green` shows improvement (fewer root violations)

---

### Phase 2: Selective Cleanup

**Pre-flight:**
1. Inspect each directory for valuable files
2. Check if any files are referenced in code/docs
3. Backup rotation for `backup/` (keep last 10, delete older)

**Execution:**
```bash
# Rotate backups (keep last 10)
python3 scripts/ops/backup_rotate.py --keep 10

# Investigate and delete if legacy
# (After manual inspection)
rm -rf examples/  # if legacy
rm -rf reports/   # if legacy
rm -rf agents/    # if legacy
rm -rf build/     # build artifacts
rm -rf test-results/  # test artifacts
rm -rf var/       # temporary files
```

**Verification:**
- Manual review of each directory before deletion
- Confirm no active references

---

### Phase 3: Gitignore Updates

**Pre-flight:**
1. Check current `.gitignore` for these patterns
2. Ensure patterns are comprehensive

**Execution:**
```bash
# Add to .gitignore if not present
cat >> .gitignore << 'EOF'
# External dependencies
genai-toolbox/

# Build artifacts
build/
test-results/
var/

# Postgres dumps (should never be committed)
.pg/
EOF
```

**Verification:**
- `.gitignore` updated
- `git status` shows these directories as ignored

---

### Phase 4: Verification & Documentation

**Post-cleanup:**
1. Run full guard suite
2. Update SSOT documentation
3. Update DMS registry (if needed)
4. Commit with clear message

**Execution:**
```bash
# Full verification
make ops.kernel.check
make reality.green || true  # may have known non-blockers
make guard.root.surface

# Update documentation
# (Update this plan with actual results)
```

---

## 4. Safety Checks

### 4.1 Pre-Delete Verification

Before deleting any directory:
1. **Search for references:**
   ```bash
   grep -r "archive/" Makefile scripts/ docs/SSOT/ || true
   grep -r "backups/" Makefile scripts/ docs/SSOT/ || true
   grep -r "\.pg/" Makefile scripts/ docs/SSOT/ || true
   grep -r "tagproof/" Makefile scripts/ docs/SSOT/ || true
   ```

2. **Check DMS registry:**
   ```bash
   pmagent kb registry list --json-only | jq '.[] | select(.path | contains("archive"))'
   ```

3. **Verify git tracking:**
   ```bash
   git ls-files archive/ backups/ .pg/ tagproof/ | head -20
   ```

### 4.2 Post-Delete Verification

After deletions:
1. **Kernel checks:**
   ```bash
   make ops.kernel.check
   ```

2. **Reality green:**
   ```bash
   make reality.green || true
   ```

3. **Root surface:**
   ```bash
   make guard.root.surface
   ```

---

## 5. Expected Outcomes

### 5.1 Immediate Benefits

- **Reduced repository size:** ~1.5GB freed
- **Cleaner root:** No legacy artifacts
- **Faster operations:** Fewer files to scan
- **Clearer structure:** Only active code/docs remain

### 5.2 Guard Improvements

- `guard.root.surface` should pass cleanly
- `reality.green` should show fewer violations
- DMS alignment should improve (fewer "extra in share" items)

### 5.3 Documentation Updates

- Update `docs/SSOT/SHARE_FOLDER_ANALYSIS.md` to reflect cleanup
- Update `docs/SSOT/PHASE27_INDEX.md` with cleanup results
- Update `.gitignore` to prevent future accumulation

---

## 6. Rollback Plan

If cleanup causes issues:

1. **Git restore:**
   ```bash
   git restore archive/ backups/ .pg/ tagproof/
   ```

2. **Selective restore:**
   ```bash
   git restore <specific-file>
   ```

3. **Backup restore:**
   ```bash
   # Use most recent backup in backup/
   cp -r backup/<latest>/share/* share/
   ```

---

## 7. Acceptance Criteria

- [ ] All Phase 1 directories deleted
- [ ] All Phase 2 directories investigated and cleaned
- [ ] `.gitignore` updated for Phase 3
- [ ] `make ops.kernel.check` passes
- [ ] `make guard.root.surface` passes
- [ ] `make reality.green` shows improvement
- [ ] Documentation updated
- [ ] Git commit with clear message

---

## 8. Next Steps

1. **Execute Phase 1** (safe deletes)
2. **Execute Phase 2** (selective cleanup)
3. **Execute Phase 3** (gitignore updates)
4. **Execute Phase 4** (verification)
5. **Update SSOT docs** with results
6. **Create PR** for review

---

**End of Plan**
