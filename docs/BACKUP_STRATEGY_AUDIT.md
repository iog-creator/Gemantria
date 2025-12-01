# Backup and Versioning Strategy Audit

## Current State Analysis

### 1. Tag-Based Versioning (PRIMARY STRATEGY) ✅

**Location**: `RELEASES.md` (lines 130-148)

**Workflow**:
```bash
# Phase completion workflow
git checkout main
git pull --ff-only
git tag -a v{major}.{minor}.{patch} -m "Release v{version}: {description}"
git push origin v{major}.{minor}.{patch}
```

**Evidence**: 93 tags exist, including:
- `v0.0.1-phase0-complete`
- `v0.0.3-phase2-pr008-complete`
- `v0.0.4-phase3-pr009-complete`
- `v0.0.5-phase3-pr010-complete`
- `backup/main-before-recovery-2025-12-01` (emergency backup)

**Purpose**: Mark stable checkpoints, phase completions, releases

---

### 2. PM Snapshots (OPERATIONAL MONITORING) ✅

**Locations**:
- `Makefile` lines 187-189 (`pm.snapshot` target)
- `scripts/pm_snapshot.py`
- Output: `evidence/pm_snapshot/run.txt`

**Workflow**:
```bash
make pm.snapshot  # Generate PM health snapshot
```

**Purpose**: 
- System health monitoring
- DB/LM status tracking
- NOT for version control or backup
- Part of housekeeping (`make housekeeping`)

---

### 3. LangGraph Checkpointers (RUNTIME STATE) ✅

**Locations**:
- `Makefile` line 523 (checkpointer_state cleanup)
- `genai-toolbox/docs/.../quickstart.py` line 45 (MemorySaver)
- `scripts/mcp_agent_bindings_chip.py` (postgres/memory checkpointer)

**Purpose**:
- Runtime agent state persistence
- NOT for version control
- Ephemeral data for agent workflows

---

### 4. Branch Preservation (CONFLICTIMG STRATEGY) ❌

**Current Reality**: 179+ remote branches still exist

**Conflict with Tag Strategy**:
- Tags mark completion → branches should be deleted
- Branches accumulate → defeats tag-based workflow
- Creates confusion: "Is code in tag or branch?"

**Root Cause**: No automated branch cleanup after tagging

---

### 5. Schema Snapshots (DOCUMENTATION) ✅

**Locations**:
- `Makefile` lines 996-999 (`control.schema.snapshot`)
- `scripts/db/control_schema_snapshot.py`

**Purpose**:
- Document DB schema state
- Export for evidence/documentation
- NOT for versioning

---

## Problems Identified

### ❌ Problem 1: Branch Accumulation
**Issue**: 179 branches remain after 105 deleted  
**Cause**: No post-tag branch cleanup  
**Impact**: Confuses "what's in the release"


### ❌ Problem 2: Multiple "Backup" Concepts
**Issue**: Tags, snapshots, checkpointers all have different purposes but user thinks "backup"  
**Cause**: Terminology overlap  
**Impact**: User uncertainty about recovery strategy

### ❌ Problem 3: No Automated Workflow Integration
**Issue**: RELEASES.md documents manual workflow, but no automation  
**Cause**: Tag creation not integrated with branch cleanup  
**Impact**: Manual overhead, forgotten steps

---

## Recommended Single Coherent Strategy

### PRIMARY: Tag-Based Releases

**For version control and recovery**:
1. Complete phase/feature
2. Merge to main
3. Create tag: `v{version}-phase{N}-complete`
4. **Delete feature branch** (automated)
5. Push tag to GitHub

**Tags are the source of truth for:**
- Phase completions
- Releases
- Recovery points
- Reproducible builds

### SECONDARY: Operational Monitoring (NOT backup)

**PM Snapshots** (`pm.snapshot`):
- System health tracking
- Run during housekeeping
- Evidence for debugging
- **NOT for version recovery**

**Checkpointers**:
- Runtime agent state
- Ephemeral data
- **NOT for version recovery**

**Schema Snapshots**:
- Documentation
- Schema evolution tracking
- **NOT for version recovery**

---

## Implementation Plan

### 1. Automate Post-Tag Branch Cleanup

Create workflow: After creating tag, automatically:
```bash
# In RELEASES.md workflow
git tag -a v{version} -m "..."
git push origin v{version}

# NEW: Auto-cleanup merged branches
pmagent repo branch-cleanup --execute

# Or more aggressively, delete branches older than 14 days
/tmp/aggressive_delete.sh
```

### 2. Update RELEASES.md 

Add step 3.4 to tagging flow:
```markdown
#### 3.4. Cleanup Feature Branches

After tagging, clean up merged branches:
\`\`\`bash
# Delete merged branches
pmagent repo branch-cleanup --execute

# Verify
git branch -r | wc -l  # Should be ~25 or fewer
\`\`\`
```

### 3. Clarify "Backup" vs "Snapshot"

**Update documentation** to disambiguate:
- **Tag** = Version checkpoint (for recovery)
- **Snapshot** = Health report (for monitoring)
- **Checkpoint** = Runtime state (for agents)

### 4. Set Branch Retention Policy

**New policy**:
- Branches without tags: Delete after 14 days
- Branches with associated tag: Delete immediately after tag creation
- Only keep: main + current active branches (<7 days old)

### 5. GitHub Branch Protection

Add to main:
- Require branches be up-to-date before merge
- Auto-delete head branches after PR merge
- Require tags for production deployments

---

## Migration Steps

### Step 1: Document Current State ✅
- Audit complete
- 93 tags documented
- 179 branches identified

### Step 2: Aggressive Cleanup (NOW)
```bash
# Delete all branches >14 days old
/tmp/aggressive_delete.sh
# Result: 179 → ~23 branches
```

### Step 3: Update RELEASES.md (NEXT)
- Add branch cleanup step
- Clarify tag-based strategy
- Remove ambiguous "backup" language

### Step 4: Automate (FUTURE)
- GitHub Action: Auto-delete branches after tag creation
- Weekly cron: Delete stale branches
- Tag creation helper script

---

## Bottom Line

**One Strategy**: **Tags are the backup/recovery mechanism**

Everything else (snapshots, checkpointers) serves operational needs, NOT version control.

**Action Required**:
1. ✅ Complete aggressive branch cleanup (179 → ~23)
2. ✅ Update RELEASES.md with cleanup step
3. ✅ Document single coherent strategy
4. Set up GitHub branch auto-deletion
5. Create tag workflow automation
