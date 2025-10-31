# Codex CLI — Optional Local Agents (Fresh Context per Task)

**Purpose.** Run terminal-native agents with a fresh context window per task, side-by-side with Cursor. **Not used in CI** unless `ALLOW_CODEX=1`.

## Install

```bash
# Option 1: Global install (requires sudo)
sudo npm i -g @openai/codex

# Option 2: Local install (no sudo)
npm i -g @openai/codex --prefix ~/.local
export PATH="$HOME/.local/bin:$PATH"

# Then login
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
export CODEX_API_KEY=...       # Codex.io (for MCP server)
```

## MCP Server (Model Context Protocol)

### Codex CLI as MCP Server

Codex CLI itself can act as an MCP server, allowing Cursor to use Codex directly. **No API key needed** - Codex CLI uses your ChatGPT subscription via OAuth login.

### Cursor MCP Integration

**Configure Codex CLI in Cursor's global MCP config:**

1. **Login to Codex CLI** (uses your ChatGPT subscription, no API key):
   ```bash
   codex login        # OAuth/device auth flow
   codex login status # Verify login status
   ```

2. **Add Codex to Cursor's global MCP config** (`~/.cursor/mcp.json`):
   ```json
   {
     "mcpServers": {
       "codex": {
         "command": "codex",
         "args": ["mcp-server"]
       }
     }
   }
   ```
   **Note:** This is configured in your **global** `~/.cursor/mcp.json` file (not the project `.cursor/mcp.json`).

3. **Restart Cursor** to load the MCP server.

4. **Verify in Cursor:** Settings → MCP → "codex" should show as Connected.

### Using Codex via Cursor MCP

Once configured, you can use Codex through Cursor's AI features:
- "Use the 'codex' MCP to read the workspace Makefile and propose a minimal fix."
- Codex will run with your ChatGPT subscription, no separate API key needed.

### Quick Setup & Verification Steps

**1. Login to Codex CLI:**
```bash
codex login        # OAuth/device auth (no API key needed)
codex status       # Verify login status
```

**2. Configure Cursor MCP:**
```bash
make codex.mcp.edit      # Edit global MCP config
make codex.mcp.validate  # Validate MCP config JSON
```

**3. Restart Cursor completely**

**4. Verify MCP connection:**
- Cursor Settings → MCP → Look for "codex" server (should show "Connected")

**5. Smoke test in Cursor:**
- "Use the 'codex' MCP to list the last 3 git commits with one-line messages."

**6. Terminal smoke test:**
```bash
codex exec -C . "List the last 3 git commits with one-line messages."
```

### Note on External MCP Servers

Codex CLI can also connect to external MCP servers (see `.codex/config.example.toml`), but the primary integration is Codex CLI itself acting as an MCP server for Cursor.

**Important:** The `@codex-data/codex-mcp` package is **not** OpenAI's Codex CLI - it's a separate blockchain data service that requires a different API key. For Cursor integration, use **Codex CLI itself** (`codex mcp-server`).

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
