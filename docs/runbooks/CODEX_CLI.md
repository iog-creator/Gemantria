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

## CI Guardrails

- All scripts and Makefile targets check if `CI=true` and `ALLOW_CODEX != 1`, exiting with a HINT message.
- No network calls or writes in CI by default.
- To enable in CI (not recommended): Set `ALLOW_CODEX=1` in CI env.
- Complies with Rules 042 (ruff formatting), 044 (no share writes), 046 (hermetic fallbacks).