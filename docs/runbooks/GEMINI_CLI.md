# Gemini CLI Integration Runbook

> **⚠️ DEPRECATED**: Gemini CLI has been deprecated in favor of local inference providers (LM Studio/Ollama) for performance and architectural alignment. The Planning Lane now defaults to the Granite `local_agent` slot. This runbook is retained for reference only. New integrations should use local providers.

Gemini CLI provides a governed planning/coding lane with very large context windows. It is optional, disabled in CI, and only used for backend planning/maths tasks (never theology).

## Install & Authenticate

1. Install the CLI (Node 18+ required):
   ```bash
   npm install -g @google/gemini-cli
   gemini --version   # expect ≥ 0.17.x
   ```
2. Run `gemini login` (or set `GEMINI_API_KEY`) to authorize the CLI.
3. The CLI stores state in `~/.gemini/`. Key files:
   - `settings.json` – global configuration (model, MCP servers, IDE hints)
   - `google_accounts.json` – login cache

## Recommended `settings.json`

```json
{
  "ide": { "hasSeenNudge": true },
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"]
    }
  },
  "model": { "name": "gemini-2.5-pro" },
  "general": { "checkpointing": { "enabled": true } },
  "security": { "auth": { "selectedType": "gemini-api-key" } }
}
```

Notes:
- `model.name` **must** be a string (not nested) or the CLI throws `model.startsWith is not a function`.
- Configure MCP servers only if you need the GitHub tool; otherwise omit the section.

## pmagent Integration

Set the planning lane via `.env.local`:

```dotenv
PLANNING_PROVIDER=gemini
PLANNING_MODEL=gemini-2.5-pro
GEMINI_ENABLED=true          # DEPRECATED: Now defaults to false. Set explicitly to enable.
GEMINI_CLI_PATH=gemini       # override if installed elsewhere
```

Usage patterns:

- `pmagent tools.plan "Outline backend refactor"` – uses whichever provider is configured (Gemini if `PLANNING_PROVIDER=gemini`).
- `pmagent tools.gemini "Draft math proof" --system "Math planner"` – forces Gemini even if the global provider differs.
- Provide deterministic context via `--prompt-file ./evidence/context.txt`.
- Every run creates an `agent_run` row plus JSON summary (stdout) and optional natural-language transcript (`=== Response ===`).

## Multi-Agent & Evidence Workflow

1. Kick off an architect plan: `pmagent tools.gemini --system "Architect"` → produce `ordered_plan`.
2. Fork sub-agents by reusing the same prompt file with different `--system` roles (Implementer, Math Verifier).
3. Save each JSON summary to `evidence/planning/gemini-<timestamp>.json` before executing steps.
4. Reference the saved plan when updating `AGENTS.md`, SSOT docs, or PR descriptions.

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| `gemini command not found` | Ensure CLI is on `PATH` or set `GEMINI_CLI_PATH` to full path. |
| `model.startsWith is not a function` | `model.name` in `settings.json` is nested incorrectly; ensure it's `"model": { "name": "gemini-2.5-pro" }`. |
| `gemini_disabled` error from pmagent | **DEPRECATED**: Gemini CLI is now disabled by default. Set `GEMINI_ENABLED=true` explicitly to enable (not recommended). |
| CLI hangs | Use `pmagent tools.gemini --json-only` for non-interactive runs or pass `--cli-path "$(npm bin -g)/gemini"`. |

## Governance Reminders

- The planning lane is **non-theology**. Use it for backend planning, math, or coding decomposition only.
- Always store outputs before acting, and run `make housekeeping` after applying approved plans.
- Disable Gemini (unset env vars) before running CI pipelines or committing automation that should stay hermetic.

## Governance Reminders (PM / Planning Lane)

When Gemini CLI is acting as a PM / planning agent for this repo, it must follow the same governance rules as pmagent:

1. **Working directory and visibility**
   - Always start Gemini CLI in the **repo root**.
   - Ensure Gemini can read:
     - `AGENTS.md`
     - `RULES_INDEX.md`
     - `.cursor/rules/*.mdc` (especially `050-ops-contract.mdc`, `051-cursor-insight.mdc`, `052-tool-priority.mdc`, `062-environment-validation.mdc`)
     - `docs/SSOT/PM_CONTRACT.md`
     - `docs/SSOT/MASTER_PLAN.md`
     - `NEXT_STEPS.md`
     - Any relevant directory `AGENTS.md` files (for example, `agentpm/plan/AGENTS.md`, `agentpm/reality/AGENTS.md`)
   - If Gemini cannot see `.cursor/rules` or these SSOT docs, it must **stop and report an environment error**, not continue with “best effort”.

2. **Planning scope (non-theology, file-first)**
   - Use Gemini only for backend planning, math, and coding decomposition – **never** for theology or gematria scoring.
   - Treat SSOT docs and `evidence/pmagent/*.json` envelopes as the source of truth for planning and status.
   - Do not invent new commands; use `pmagent` and `make` targets that already exist (for example, `pmagent plan next`, `pmagent plan open`, `pmagent plan reality-loop`, `pmagent plan history`, `pmagent reality validate-capability-envelope`).

3. **Output shape when acting as PM**
   - When you ask Gemini to choose or describe the **next work item**, its response must follow the 4‑block OPS format:
     1. **Goal**
     2. **Commands**
     3. **Evidence to return**
     4. **Next gate**
   - The Commands block should be runnable as‑is in a local shell, and evidence expectations must match the repo’s guards (ruff, smokes, `make reality.green`, pmagent commands).

4. **Fail-closed behavior**
   - If Gemini detects that it is missing any of the required SSOT files, or if it cannot verify the repo root, it must:
     - Emit a clear message like:
       > "Environment error: missing `.cursor/rules` / `PM_CONTRACT.md` / `MASTER_PLAN.md`. Please mount the full repo and retry."
     - Refrain from proposing new commands or edits until the environment is fixed.
   - This matches the PM contract’s rule that governance drift is a **bug to be fixed**, not a hint to proceed with partial information.
