# Codex CLI Integration Runbook

## Installation Instructions

1. Install Codex CLI globally (assuming Node.js or appropriate runtime):
   - `npm install -g codex-cli` (or equivalent based on Codex docs).

2. Copy `.codex/config.example.toml` to `~/.codex/config.toml` or project-local `.codex/config.toml`.

3. Add your API keys for profiles (openai, grok4).

4. Test: `codex --help`.

Note: Codex CLI is optional and not required for the repo. It's for local agent-assisted development.

## Safety Defaults Explanation

- `history.persistence = "none"`: Ensures fresh context per task, stateless runs.
- `sandbox_mode = "workspace-write"`: Limits operations to the current repo/workspace.
- `approval_policy = "on-request"`: Prompts for approval before any file edits.
- `file_opener = "cursor"`: Integrates with Cursor editor for file opening.
- Profiles: `openai` (default) and `grok4` (xAI-specific).

These defaults align with hermetic CI and no-share-writes policies.

## Helper Script Usage Examples

### Single Task
```bash
scripts/agents/codex-task.sh "Refactor the UI components for better modularity" PROFILE=grok4
```

### Parallel Tasks
```bash
echo "Task 1: Fix bug in filters.ts\nTask 2: Add tests for metrics.ts" | scripts/agents/codex-par.sh PROFILE=openai
```

Or with file:
```bash
scripts/agents/codex-par.sh -f tasks.txt
```

### Environment Variables
- `PROFILE`: openai (default) or grok4.
- `CWD`: Override current working directory.

## pmagent Integration

Codex is now a first-class planning provider inside pmagent:

- Enable it by setting in `.env.local`:
  ```dotenv
  PLANNING_PROVIDER=codex
  PLANNING_MODEL=gpt-5-codex
  CODEX_ENABLED=true
  CODEX_CLI_PATH=codex  # override if the binary lives elsewhere
  ```
- Run governed prompts via `pmagent tools.plan "Describe task"` (uses default provider) or `pmagent tools.codex "Describe task"` to force Codex regardless of the global provider.
- Provide richer context with `--prompt-file path/to/context.txt` and role-specific `--system "Implementer role"`.
- Every invocation creates an `agent_run` row, emits JSON summaries, and stores stdout/stderr hints for auditing.

Recommended system template (mirrors Prompting Guide):

```
You are an implementation-focused coding assistant for Gemantria.v2.
Obey Rules 050/051/052. Never change theology/gematria outputs.
Return JSON {analysis, proposed_diffs[], tests}.
```

- Ask Codex for Ruff-compliant diffs and explicit `tests` block (e.g., `ruff format --check .`, `pytest ...`).
- Before executing any suggested edits, persist Codex output under `evidence/planning/` and get human approval.

## Multi-Agent Workflow Pattern

1. `pmagent tools.plan --system "Architect"` to outline phases.
2. `pmagent tools.codex --system "Implementer"` for diff + test plans.
3. Optional: run multiple Codex agents in parallel (e.g., API vs. docs) by supplying different prompt files.
4. Store each response and reference it in PR descriptions or AGENTS.md updates.

## Troubleshooting

- `codex_disabled`: `CODEX_ENABLED` is false (default). Set to `true` locally; never enable in CI.
- `cli_not_found:codex`: Update `CODEX_CLI_PATH` or ensure the binary is on `$PATH`.
- Empty stdout: Codex sometimes writes output to stderr. `_print_planning_result` surfaces both streams; capture logs in `evidence/planning/`.
- CI guard failure: `scripts/agents/codex-task.sh` and pmagent commands both honor `ALLOW_CODEX`. In CI keep the default (disabled) to retain hermetic behavior.

## CI Guardrails

- All scripts and Makefile targets check if `CI=true` and `ALLOW_CODEX != 1`, exiting with a HINT message.
- No network calls or writes in CI by default.
- To enable in CI (not recommended): Set `ALLOW_CODEX=1` in CI env.
- Complies with Rules 042 (ruff formatting), 044 (no share writes), 046 (hermetic fallbacks).