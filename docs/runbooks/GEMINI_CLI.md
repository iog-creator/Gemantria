# Gemini CLI — Optional Local Agents (Fresh Context per Task)

**Purpose.** Run Google Gemini models in your terminal with a fresh context window per task, side-by-side with Cursor. **Not used in CI** unless `ALLOW_GEMINI=1`.

## Install

```bash
# Option 1: Official NPM package
npm i -g @google/gemini-cli

# Option 2: macOS/Linux Homebrew
brew install gemini-cli

# Launch and authenticate
gemini

# (Optional) API key authentication instead of OAuth
export GEMINI_API_KEY=your_api_key_here
gemini
```

## Authentication Options

### OAuth (Recommended)
- Uses your Google account via browser OAuth flow
- No API key management required
- Automatic token refresh

### API Key
- Set `GEMINI_API_KEY` environment variable
- Or use Vertex AI: `export GOOGLE_API_KEY=... && export GOOGLE_GENAI_USE_VERTEXAI=true`

### Vertex AI (Enterprise)
- Set `GOOGLE_API_KEY` and `GOOGLE_GENAI_USE_VERTEXAI=true`
- Supports enterprise features and higher rate limits
- Requires GCP project setup

## Settings Configuration

Gemini CLI uses `~/.gemini/settings.json` for configuration:

```json
{
  "auth": {
    "method": "api-key"
  },
  "model": "gemini-2.0-flash-exp",
  "telemetry": {
    "enabled": false
  }
}
```

**Note:** Model selection and other settings are configured here, not via command-line profiles.

## MCP Server Integration (Optional)

Gemini CLI can consume MCP servers via settings configuration, allowing integration with external tools and services.

Add to `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"]
    }
  }
}
```

## Safety Defaults

- **Context scope**: Limited to current working directory
- **File operations**: Can read/modify files in workspace
- **Network access**: Available for tool integrations
- **Model selection**: Configurable via settings.json

## Command Line Usage

### Single Task Execution
```bash
# Basic task
gemini -p "Analyze the Makefile and suggest improvements"

# With working directory
gemini -p "Review recent git commits" --include-directories ./src

# Non-interactive mode (for scripting)
echo "List directory contents" | gemini -p "Execute this command"
```

### Interactive Mode
```bash
# Start interactive session
gemini

# Within session:
> Analyze this codebase structure
> Help me debug this Python function
> Generate documentation for this module
```

## Make Targets (Optional)

Gated by `ALLOW_GEMINI=1` and **no-op in CI** by default.

```bash
# Single task
make gemini.task TASK="Analyze recent commits and suggest improvements"

# Parallel tasks (up to 4 concurrent)
make gemini.parallel TASKS=$'Task one\nTask two with spaces\nTask three'

# Interactive session
make gemini.session NAME="code-review-session"
```

## Key Features

### 1M Token Context Window
- Gemini 2.5 Pro supports up to 1M tokens
- Ideal for large codebases and comprehensive analysis
- Maintains context across long conversations

### Built-in Tools
- **Google Search**: Ground responses in current web data
- **Shell execution**: Run commands and analyze output
- **Web fetching**: Access external APIs and resources
- **File operations**: Read, modify, and create files

### Checkpointing (Interactive Sessions)
- Save/restore conversation state
- Resume long-running analysis sessions
- Persistent context across terminal sessions

## Comparison with Codex CLI

| Feature | Gemini CLI | Codex CLI |
|---------|------------|-----------|
| **Provider** | Google Gemini | OpenAI Codex |
| **Context Window** | 1M tokens (Gemini 2.5 Pro) | 128K tokens |
| **Authentication** | OAuth or API key | OAuth (ChatGPT subscription) |
| **Tools** | Built-in (search, shell, web) | MCP server integration |
| **Checkpointing** | Yes | No |
| **Parallel Execution** | Via make targets | Via make targets |
| **CI Integration** | Optional (ALLOW_GEMINI=1) | Optional (ALLOW_CODEX=1) |

## CI Guardrails (Aligned with AGENTS.md & Rules)

- **No outbound network in CI by default**
- **No `share/**` writes in CI**
- **Hermetic execution**: Requires explicit `ALLOW_GEMINI=1` override

All targets detect CI environments (`CI`, `GITHUB_ACTIONS`, `GITLAB_CI`, `BUILDKITE`) and exit early with a HINT message unless `ALLOW_GEMINI=1` is explicitly set.

## Troubleshooting

### Authentication Issues
```bash
# Clear authentication state
rm -rf ~/.gemini

# Re-authenticate
gemini
```

### Rate Limiting
- Free tier: 10 requests/minute
- Upgrade to paid tier for higher limits
- Use Vertex AI for enterprise quotas

### Context Window Limits
- Monitor token usage in responses
- Break large tasks into smaller sessions
- Use interactive mode for incremental work

## Best Practices

1. **Use appropriate models**: Gemini 2.0 Flash for speed, Gemini 2.5 Pro for complex analysis
2. **Leverage tools**: Enable search and web access for up-to-date information
3. **Session management**: Use named sessions for ongoing work
4. **CI safety**: Keep local-only unless explicitly enabled
5. **Context files**: Use GEMINI.md for consistent project context

## Integration with Development Workflow

- **Code review**: Analyze pull requests and suggest improvements
- **Debugging**: Interactive troubleshooting with full context access
- **Documentation**: Generate and validate documentation
- **Architecture**: Analyze codebase structure and patterns
- **Testing**: Review test coverage and suggest additional tests
