# GITHUB_WORKFLOW_CONTRACT.md

# Gemantria — GitHub Reality & Branch Governance (Phase 26.5+)

## 1. Reality Has Three Layers

When any agent (Cursor, OA, pmagent, PM) decides what work is allowed, it MUST
treat reality as a 3-layer stack:

1. **GitHub Reality (outer shell)**
   - Remote branches in `origin/*`
   - Open PRs and their titles/descriptions
   - CI status on GitHub (required checks)

2. **DMS + Kernel (control plane)**
   - Postgres `control.*` tables
   - `PM_KERNEL.json` and `PM_BOOTSTRAP_STATE.json`
   - `reality.green` and `ops.kernel.check`

3. **Local Surfaces**
   - Working tree & uncommitted changes
   - `docs/SSOT/*`, `share/*`, new code edits

**Rule:** For any feature or phase work:
- All three layers must be checked.
- If they disagree in a material way, agents MUST fail closed and escalate.

---

## 2. Phase ↔ Branch Mapping

Each phase must have a dedicated branch (and usually a PR):

- Phase 26 regen: e.g. `feat/phase26-kernel-enforcement`
- Phase 27 kernel consumers: e.g. `feat/phase27-kernel-consumers`

Kernel state (`PM_KERNEL.json.current_phase`) MUST match the intended phase of
the current working branch. If:

- `kernel.current_phase = 26`, but branch starts with `feat/phase27-...`, or
- `kernel.current_phase = 27`, but branch starts with `feat/phase26-...`,

then the system is in an invalid phase/branch alignment and agents MUST
STOP and escalate to the PM before doing feature work.

---

## 3. GitHub Preflight for OPS Sessions

Before any OPS session that may change code, `share/`, or SSOT docs:

### 1. Kernel preflight:
- **Run**: `make ops.kernel.check`
- **If it fails**: NO feature work, remediation only.

### 2. Git preflight:
- **Run**:
  - `git status -sb`
  - `git rev-parse --abbrev-ref HEAD`
  - `git branch -vv`
- **Confirm**:
  - Working tree is clean (or only intentional edits).
  - Branch name matches the current phase.
  - Branch tracks a remote (`origin/branch-name`).

### 3. (Optional but recommended) GitHub preflight:
- **If `gh` CLI is available**:
  - `gh pr status` to see open PR(s) for this branch.
- **Otherwise**:
  - `git ls-remote --heads origin` to confirm branch exists remotely.

Agents MUST include this evidence in their OPS responses when planning feature work.

---

## 4. CI Quality Gates and Ruff Scope

The ruff CI job is scoped to **governed paths** (`pmagent/`, `src/`, `docs/SSOT/`, `scripts/guards/`, `tests/`) as defined in `ruff.toml`. Ruff is zero-tolerance on these paths; all errors must be fixed before merging.

**Legacy directories** (`archive/`, `oa/`, and other explicitly excluded paths in `ruff.toml`) are excluded from linting to avoid blocking new PRs. These directories are treated as technical debt and must be cleaned up in dedicated PRs, not as part of feature work.

**Docs-only PRs** (PRs that only modify documentation/markdown files, such as PM contract updates) must not be blocked by lint failures in excluded legacy code. The ruff CI job respects `ruff.toml` exclusions and only checks governed paths.

---

## 5. Phase Mixing is Forbidden

On any branch whose purpose is documented as "Phase 26":

- Phase 27 implementations (`pmagent/kernel` interpreter, OA runtime, DSPy programs,
  Console kernel panel wiring) MUST remain:
  - design-only (`docs/SSOT/*`), or
  - code skeletons that are not wired into runtime paths.

If Phase 27 code is accidentally wired into Phase 26 behavior, agents MUST:

1. Stop implementation.
2. Explain the drift to the PM.
3. Either:
   - Unwire the 27.* behavior, or
   - Move the work to a dedicated Phase 27 branch.

---

## 6. Integration Points

- **`EXECUTION_CONTRACT.md`**:
  - Section 5 (Kernel-Aware Preflight) MUST reference this contract as the
    GitHub-awareness layer.
    
- **`START_HERE.md`**:
  - MUST mention GitHub preflight (`git status`/branch/remote checks) as part of
    the standard boot sequence.
    
- **`AGENTS.md` / `GEMINI.md`**:
  - MUST treat GitHub as part of SSOT: branches, PR titles, and CI are not
    optional context.

---

## 7. Future Guard: `reality.github`

A future guard `make reality.github` SHOULD:

- Check branch ↔ phase alignment using `PM_KERNEL.json` and git branch name.
- Check that required PRs exist for active phases.
- Surface GitHub CI results for the current branch/PR.

For now, see `scripts/guards/guard_github_state.py` as the initial hook point.

---

## Success Criteria

This contract is effective when:

- ✅ All OPS blocks include Git preflight evidence (branch, status, tracking)
- ✅ Agents cannot mix Phase N implementation into Phase M branches without explicit detection
- ✅ GitHub state (branch, PR, CI) is treated as equally important as kernel state
- ✅ `make github.state.check` runs successfully and surfaces branch/phase alignment

---

**Last Updated**: 2025-12-06 (Phase 26.5 — GitHub Awareness Enforcement)
