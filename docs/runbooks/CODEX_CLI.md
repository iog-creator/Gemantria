# Codex CLI — Optional Local Agents (Fresh Context per Task)

**Purpose.** Run terminal-native agents with a fresh context window per task, side-by-side with Cursor. **Not used in CI** unless `ALLOW_CODEX=1`.

## Install

```bash
npm i -g @openai/codex
codex login
```

Copy repo example to your user config:

```bash
mkdir -p ~/.codex
cp .codex/config.example.toml ~/.codex/config.toml
```

Export keys when needed:

```bash
export OPENAI_API_KEY=...      # OpenAI
export XAI_API_KEY=...         # xAI (Grok)
```

## Safety Defaults

- `history.persistence = "none"` ⇒ **fresh context** each run
- `sandbox_mode = "workspace-write"` ⇒ edits limited to repo
- `approval_policy = "on-request"` ⇒ asks before edits
- `file_opener = "cursor"` ⇒ open file refs in Cursor
- Profiles: `openai` (default), `grok4` (fast/code)

## Helper scripts

```bash
# single task
scripts/agents/codex-task.sh "Audit Makefile; propose minimal patch for 'make ci'."

# grok profile
PROFILE=grok4 scripts/agents/codex-task.sh "Summarize pytest failures and propose 2-line fix."

# parallel tasks (pipe one-per-line)
printf "%s\n" \
  "Run ruff check; print exact fix commands." \
  "Run pytest -q; summarize failures." \
| scripts/agents/codex-par.sh
```

## Make targets (optional)

Gated by `ALLOW_CODEX=1` and **no-op in CI** by default. See Makefile additions in this PR.

```bash
# Single task
make codex.task TASK="List last 5 commits; propose 2-line release note."

# Grok profile
make codex.grok TASK="Scan pytest failures; produce minimal patches."

# Parallel tasks (preserve newlines/spaces)
make codex.parallel TASKS=$'Task one\nTask two with spaces\nTask three'
```

## CI Guardrails (aligned with AGENTS.md & Rules 042/044/046)

- **No outbound network in CI by default.**
- **No `share/**` writes in CI.**
- **Ruff-only formatter.**

All scripts detect CI environments (`CI`, `GITHUB_ACTIONS`, `GITLAB_CI`, `BUILDKITE`) and exit early with a HINT message unless `ALLOW_CODEX=1` is explicitly set.
