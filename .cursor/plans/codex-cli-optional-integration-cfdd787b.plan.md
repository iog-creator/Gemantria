<!-- cfdd787b-c7d2-4559-a969-187f79fbdeb7 c8b9fc6c-ea4c-4557-abb3-b3b6e0c1249e -->
# Codex CLI Optional Integration (Local-Only, CI-Gated)

## Goal

Add optional Codex CLI integration for running fresh-context terminal agents alongside Cursor. Integration is:

- **Local-only by default** (CI remains hermetic unless `ALLOW_CODEX=1`)
- **No share/ writes** (respects Rule 044)
- **Ruff-only formatting preserved** (respects Rule 042)
- **Stateless runs** (fresh context per task)

## Compliance Checkpoints

- Rule 042: Formatter SSOT — only shell/markdown/toml files added; ruff remains formatter
- Rule 044: Share Manifest Contract — no new share artifacts
- Rule 046: Hermetic CI Fallbacks — CI exits early with HINT unless `ALLOW_CODEX=1`
- AGENTS.md: Guardrails — no outbound network in CI, no share writes in CI

## Implementation Steps

### Step 1: Verify SSOT State

- Capture current git status and branch
- Verify guardrails in AGENTS.md (lines 182-188)
- Confirm system-enforcement.yml CI gates
- Document evidence for compliance verification

### Step 2: Create Directory Structure

- `mkdir -p scripts/agents docs/runbooks .codex`
- Ensure proper permissions for shell scripts

### Step 3: Add Configuration Files

- **`.codex/config.example.toml`**: Example config with safe defaults
  - `history.persistence = "none"` (fresh context)
  - `sandbox_mode = "workspace-write"` (repo-scoped)
  - `approval_policy = "on-request"` (asks before edits)
  - `file_opener = "cursor"` (opens files in Cursor)
  - Profiles: `openai` (default), `grok4` (xAI)

### Step 4: Create Helper Scripts

- **`scripts/agents/codex-task.sh`**: Single-task wrapper
  - CI guard: exit 0 with HINT if `CI=true` and `ALLOW_CODEX≠1`
  - Checks for `codex` command availability
  - Supports `PROFILE` and `CWD` env vars
  - Usage help included

- **`scripts/agents/codex-par.sh`**: Parallel task runner
  - Reads tasks from stdin or `-f` file argument
  - Same CI guard as codex-task.sh
  - Runs tasks in background and waits for all

### Step 5: Create Documentation

- **`docs/runbooks/CODEX_CLI.md`**: Complete runbook
  - Installation instructions
  - Safety defaults explanation
  - Helper script usage examples
  - CI guardrails section

### Step 6: Update Makefile

- Add three new targets (append to end):
  - `codex.task`: Single task via `codex-task.sh`
  - `codex.grok`: Grok profile task
  - `codex.parallel`: Parallel tasks via `codex-par.sh`
- All targets include CI guard: exit 0 with HINT if CI and `ALLOW_CODEX≠1`
- Usage: `make codex.task TASK="instruction"`

### Step 7: Update AGENTS.md

- Add minimal section under "Guardrails we keep"
- Pointer to `docs/runbooks/CODEX_CLI.md`
- Note: optional, local-only, CI-gated
- Installation and usage quick reference

### Step 8: Local Verification (No Network)

- Run `ruff format --check .` and `ruff check .` (Rule 042 compliance)
- Test Makefile targets without Codex installed (expect HINT, exit 0)
- Verify no share/ drift (`git diff --quiet -- share`)
- Confirm all new scripts are executable

### Step 9: Format and Commit

- Run `ruff format .` to format new files
- Stage all changes: `git add -A`
- Commit: `docs(agents): optional Codex CLI integration (local-only); gated Make targets; runbook & scripts`

### Step 10: Create PR

- Push branch: `tools/codex-cli-optional-setup-001`
- Create PR with title and body explaining:
  - Summary of changes
  - CI hermiticity guarantees
  - Alignment with Rules 042/044/046
  - Acceptance criteria checklist

## Files to Create

1. `.codex/config.example.toml` — Configuration template
2. `scripts/agents/codex-task.sh` — Single task wrapper
3. `scripts/agents/codex-par.sh` — Parallel task runner
4. `docs/runbooks/CODEX_CLI.md` — Runbook documentation

## Files to Modify

1. `Makefile` — Add three new targets (append-only)
2. `AGENTS.md` — Add pointer section under guardrails

## Verification Commands

```bash
# Format/lint check
ruff format --check . && ruff check .

# Test CI guard (should exit 0 with HINT)
CI=true make codex.task TASK="test" || true

# Verify no share drift
git diff --quiet -- share
```

## Risk Mitigation

- **Easy rollback**: Delete three files + Makefile additions + AGENTS.md section
- **CI safety**: All targets exit early in CI by default
- **No share writes**: Integration doesn't touch share/
- **Formatter preserved**: Only adds non-Python files

### To-dos

- [ ] Verify SSOT state: capture git status, verify AGENTS.md guardrails, confirm CI enforcement gates
- [ ] Create directory structure: scripts/agents, docs/runbooks, .codex
- [ ] Create .codex/config.example.toml with safe defaults (stateless, repo-scoped, cursor opener)
- [ ] Create scripts/agents/codex-task.sh with CI guard and usage help
- [ ] Create scripts/agents/codex-par.sh for parallel task execution with CI guard
- [ ] Create docs/runbooks/CODEX_CLI.md with installation, usage, and CI guardrails
- [ ] Add codex.task, codex.grok, codex.parallel targets to Makefile with CI guards
- [ ] Add Codex CLI pointer section to AGENTS.md under guardrails
- [ ] Run ruff format, verify no share drift, test Makefile targets (CI guard works)
- [ ] Commit changes and create PR with compliance summary and acceptance criteria
