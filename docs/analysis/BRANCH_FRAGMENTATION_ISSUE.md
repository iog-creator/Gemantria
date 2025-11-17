# Branch Fragmentation Issue — Critical Repository Health Problem

**Date:** 2025-11-16  
**Status:** 🔴 **CRITICAL** — Requires immediate attention  
**Impact:** High — Blocks efficient development, increases merge conflicts, creates technical debt

---

## Executive Summary

The Gemantria repository has accumulated **significant branch fragmentation**:

- **514 total branches** (local + remote)
- **239 remote branches**
- **199 branches NOT merged into main** (83% of remote branches)
- **Only 40 branches merged into main** (17% of remote branches)
- **20+ open PRs** (many likely stale or abandoned)

This fragmentation creates:
1. **Merge conflict accumulation** as branches diverge from main
2. **Technical debt** from unmerged work
3. **Confusion** about which branches are active vs abandoned
4. **CI/CD overhead** from testing many stale branches
5. **Difficulty** in tracking what work is complete vs in-progress

---

## Current State (2025-11-16)

### Branch Statistics

```bash
# Total branches (local + remote)
git branch -a | wc -l
# 514 branches

# Remote branches
git branch -r | wc -l
# 239 remote branches

# Merged into main
git branch -r --merged main | wc -l
# 40 branches (17%)

# NOT merged into main
git branch -r --no-merged main | wc -l
# 199 branches (83%)
```

### Sample Open PRs (Truncated List)

- PR #565: feat(phase6): unified bring-up system
- PR #563: fix(e2e): runnable entrypoints for docs→DB→LM pipeline
- PR #561: docs: mark Phase-6P complete & add Phase-7 plan stub
- PR #552: feat(phase6j): BibleScholar read-only Gematria adapter
- PR #551: feat(phase6i): expand Gematria numerics coverage
- PR #550: feat(phase6g): AgentPM Gematria module skeleton
- PR #549: feat(phase6d): BibleScholar Knowledge Slice integration
- PR #548: feat(phase6d): StoryMaker Knowledge Slice integration
- PR #547: feat(phase6d): knowledge adapter for kb_docs export
- PR #541: phase5: StoryMaker & BibleScholar LM integration planning
- PR #504-502: Multiple E87-E90 implementation PRs
- PR #479, #477, #475, #473, #471, #469: Multiple PLAN-073/074 TV staging PRs

**Pattern:** Many branches follow naming conventions like:
- `feat/phase6*` (Phase 6 feature branches)
- `impl/078-*` (Implementation branches)
- `tvs/073-*` (Test verification staging branches)
- `plan-074/*` (Planning branches)

---

## Root Causes

### 1. Rapid Feature Development

- Multiple parallel feature tracks (Phase 6, Phase 7, governance rebuild)
- Small PRs created for each sub-feature
- Branches created but not always merged promptly

### 2. Governance Drift

From `PHASE_1_7_GOVERNANCE_DRIFT_MAP.md`:
- **Blocker 1**: Phase-1 Control Plane pending items (STRICT/HINT CI lanes)
- **Blocker 2**: Phase-6D downstream app wiring incomplete
- **Blocker 3**: Phase-7 Governance SSOT migration not implemented

These blockers cause branches to accumulate while waiting for foundational work.

### 3. Merge Conflict Accumulation

- Branches diverge from main over time
- Conflicts become harder to resolve as branches age
- Scripts exist to batch-merge PRs (`scripts/ops/batch_merge_burndown.sh`, `scripts/ops/fast_merge_burndown.sh`) indicating this is a known problem

### 4. Lack of Branch Cleanup Policy

- No automated cleanup of merged branches
- No policy for closing stale PRs
- No clear criteria for when to abandon vs merge branches

---

## Impact Analysis

### Development Velocity

- **Slower PR reviews**: Harder to find relevant PRs among 20+ open
- **Merge conflicts**: 199 unmerged branches increase conflict probability
- **Context switching**: Developers must track many branches

### Technical Debt

- **Unmerged work**: Features implemented but not integrated
- **Duplicate effort**: Multiple branches may implement similar features
- **Testing overhead**: CI runs on many stale branches

### Repository Health

- **Git performance**: Large number of branches slows git operations
- **Confusion**: Hard to determine which branches are active
- **Maintenance burden**: Keeping branches up-to-date becomes impractical

---

## Existing Mitigation Attempts

### Batch Merge Scripts

The repository has scripts to batch-merge PRs:

1. **`scripts/ops/batch_merge_burndown.sh`**
   - Merges main into each PR branch
   - Resolves common conflicts automatically
   - Attempts to merge PRs

2. **`scripts/ops/fast_merge_burndown.sh`**
   - Fast batch merge for DSN burndown PRs
   - Auto-resolves common conflicts
   - Uses worktrees to avoid conflicts

3. **`scripts/ops/update_and_merge_pr.sh`**
   - Updates and merges single PR using worktree
   - Handles conflicts by taking main's version for known files

**Issue**: These scripts help but don't address the root cause of branch accumulation.

---

## Recommended Solutions

### Immediate Actions (Week 1)

1. **Audit Open PRs**
   ```bash
   # List all open PRs with metadata
   gh pr list --state open --json number,title,headRefName,createdAt,author,state \
     --limit 100 > evidence/open_prs_audit.json
   
   # Categorize:
   # - Ready to merge (passing checks, approved)
   # - Needs rebase/update
   # - Stale/abandoned (no activity >30 days)
   # - Blocked (waiting on other work)
   ```

2. **Close Stale PRs**
   - Identify PRs with no activity >30 days
   - Comment on PRs asking for status
   - Close PRs that are abandoned (preserve branch for reference)

3. **Batch Merge Ready PRs**
   - Use existing batch merge scripts for PRs that are ready
   - Focus on PRs that pass checks and have approvals

### Short-Term Actions (Month 1)

4. **Establish Branch Cleanup Policy**
   - Auto-delete branches after PR merge (GitHub setting)
   - Monthly cleanup of branches older than 90 days
   - Document branch naming conventions

5. **Implement Branch Health Monitoring**
   - Script to report branch statistics weekly
   - Alert when unmerged branch count exceeds threshold
   - Track branch age and divergence from main

6. **Prioritize Blocker Resolution**
   - Address Phase-1 Control Plane pending items
   - Complete Phase-6D downstream app wiring
   - Implement Phase-7 Governance SSOT migration
   - This will unblock many dependent branches

### Long-Term Actions (Quarter 1)

7. **Smaller, Faster PRs**
   - Encourage smaller PRs that merge quickly
   - Set PR size limits (e.g., max 500 lines changed)
   - Faster review cycles reduce branch accumulation

8. **Feature Flags Instead of Branches**
   - Use feature flags for incomplete features
   - Merge to main behind flags
   - Reduces long-lived feature branches

9. **Automated Branch Management**
   - GitHub Actions to auto-close stale PRs
   - Automated rebase/update of PRs before merge
   - Branch protection rules to prevent divergence

---

## Branch Classification Framework

Classify branches into categories:

### 1. **Active Development**
- Recent commits (<7 days)
- Open PR with recent activity
- **Action**: Keep, ensure up-to-date with main

### 2. **Ready to Merge**
- PR passes all checks
- Has approvals
- No conflicts
- **Action**: Merge immediately

### 3. **Needs Update**
- PR has conflicts or failing checks
- Branch diverged from main
- **Action**: Rebase/update, then merge or close

### 4. **Stale/Abandoned**
- No activity >30 days
- No response to status inquiries
- **Action**: Close PR, archive branch (don't delete)

### 5. **Blocked**
- Waiting on other work (governance rebuild, etc.)
- Documented blocker
- **Action**: Keep but track blocker resolution

---

## Metrics to Track

### Weekly Reports

1. **Branch Count**
   - Total branches
   - Unmerged branches
   - Branches older than 30/60/90 days

2. **PR Status**
   - Open PRs by category (ready/needs-update/stale/blocked)
   - Average PR age
   - Merge rate (PRs merged per week)

3. **Merge Conflicts**
   - Number of PRs with conflicts
   - Average conflict resolution time
   - Common conflict files

### Health Thresholds

- **🟢 Healthy**: <50 unmerged branches, <10 open PRs
- **🟡 Warning**: 50-100 unmerged branches, 10-20 open PRs
- **🔴 Critical**: >100 unmerged branches, >20 open PRs (current state)

---

## Implementation Plan

### Phase 1: Assessment (Week 1)
- [ ] Audit all open PRs (categorize)
- [ ] Identify stale/abandoned PRs
- [ ] Document blockers for blocked PRs
- [ ] Create branch health dashboard

### Phase 2: Cleanup (Week 2-3)
- [ ] Close stale PRs (with notifications)
- [ ] Batch merge ready PRs
- [ ] Update/rebase PRs that need it
- [ ] Archive abandoned branches

### Phase 3: Policy (Week 4)
- [ ] Document branch cleanup policy
- [ ] Set up automated branch deletion (post-merge)
- [ ] Create branch health monitoring script
- [ ] Update AGENTS.md with branch management guidelines

### Phase 4: Blocker Resolution (Month 2-3)
- [ ] Resolve Phase-1 Control Plane blockers
- [ ] Complete Phase-6D downstream app wiring
- [ ] Implement Phase-7 Governance SSOT migration
- [ ] Unblock dependent branches

### Phase 5: Automation (Month 3-4)
- [ ] GitHub Actions for stale PR detection
- [ ] Automated rebase/update workflows
- [ ] Branch health reporting (weekly)
- [ ] PR size/quality checks

---

## Related Documents

- `docs/analysis/phase7_governance/PHASE_1_7_GOVERNANCE_DRIFT_MAP.md` — Governance blockers
- `scripts/ops/batch_merge_burndown.sh` — Batch merge script
- `scripts/ops/fast_merge_burndown.sh` — Fast merge script
- `scripts/ops/update_and_merge_pr.sh` — Single PR update script
- `scripts/branch_health_report.py` — Branch health reporting (if exists)

---

## Next Steps

1. **Immediate**: Review this document with team
2. **This Week**: Run PR audit and categorize all open PRs
3. **Next Week**: Begin cleanup (close stale, merge ready)
4. **This Month**: Establish branch cleanup policy
5. **Next Month**: Resolve governance blockers

---

## Notes for GPT Agents

When working with branches:

1. **Check branch age**: If branch is >30 days old, verify it's still needed
2. **Rebase before PR**: Always rebase on latest main before creating PR
3. **Small PRs**: Prefer smaller, focused PRs that merge quickly
4. **Close when done**: Close PRs that are abandoned or superseded
5. **Document blockers**: If PR is blocked, document the blocker clearly

**Rule-063 (Git Safety)**: Never force-push to main, never delete branches without confirmation, always verify branch state before operations.

