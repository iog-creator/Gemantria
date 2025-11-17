# Branch Fragmentation Issue — Quick Reference for GPT Agents

**Status:** 🔴 **CRITICAL**  
**Last Updated:** 2025-11-16

---

## The Problem

The repository has **514 total branches** with **199 branches NOT merged into main** (83% of remote branches). This creates:

- Merge conflicts that accumulate over time
- Technical debt from unmerged work
- Confusion about which branches are active
- CI/CD overhead from testing stale branches

---

## Key Statistics

- **514 total branches** (local + remote)
- **239 remote branches**
- **199 branches NOT merged** (83%)
- **40 branches merged** (17%)
- **20+ open PRs** (many likely stale)

---

## What GPT Agents Should Know

### When Creating New Branches

1. **Check if similar work exists**: Search for existing branches/PRs before creating new ones
2. **Use descriptive names**: Follow naming conventions (`feat/`, `fix/`, `docs/`)
3. **Keep branches small**: Prefer smaller PRs that merge quickly
4. **Rebase frequently**: Keep branch up-to-date with main to avoid conflicts

### When Working with Existing Branches

1. **Check branch age**: If >30 days old, verify it's still needed
2. **Check PR status**: If PR exists, check if it's stale or abandoned
3. **Avoid creating duplicates**: Don't create new branches for work already in progress
4. **Close abandoned work**: If branch is abandoned, close the PR (preserve branch)

### When Merging PRs

1. **Merge quickly**: Don't let PRs sit open for weeks
2. **Use batch scripts**: For multiple PRs, use `scripts/ops/batch_merge_burndown.sh`
3. **Resolve conflicts promptly**: Don't let conflicts accumulate
4. **Delete merged branches**: Enable auto-delete after merge (GitHub setting)

---

## Root Causes

1. **Rapid feature development**: Multiple parallel tracks (Phase 6, Phase 7, governance)
2. **Governance blockers**: Phase-1/6D/7 blockers cause branches to accumulate
3. **Merge conflict accumulation**: Branches diverge from main over time
4. **No cleanup policy**: No automated cleanup of merged/stale branches

---

## Immediate Actions Needed

1. **Audit open PRs**: Categorize as ready/needs-update/stale/blocked
2. **Close stale PRs**: PRs with no activity >30 days
3. **Batch merge ready PRs**: Use existing batch merge scripts
4. **Resolve blockers**: Phase-1 Control Plane, Phase-6D wiring, Phase-7 SSOT migration

---

## Full Documentation

See `docs/analysis/BRANCH_FRAGMENTATION_ISSUE.md` for complete analysis, solutions, and implementation plan.

---

## Related Scripts

- `scripts/ops/batch_merge_burndown.sh` — Batch merge multiple PRs
- `scripts/ops/fast_merge_burndown.sh` — Fast batch merge with auto-conflict resolution
- `scripts/ops/update_and_merge_pr.sh` — Update and merge single PR using worktree

---

## Health Thresholds

- **🟢 Healthy**: <50 unmerged branches, <10 open PRs
- **🟡 Warning**: 50-100 unmerged branches, 10-20 open PRs
- **🔴 Critical**: >100 unmerged branches, >20 open PRs (**CURRENT STATE**)

---

**Rule-063 (Git Safety)**: Never force-push to main, never delete branches without confirmation, always verify branch state before operations.

