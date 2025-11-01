# ADR-027: AI Agent Tooling Integration

## Status
Accepted

## Context
The Gemantria project requires sophisticated AI tooling for code analysis, documentation, and workflow automation. Previous integrations were limited to LM Studio for metadata generation. The project needs comprehensive AI agent support for development, testing, and operational workflows.

## Decision
Implement dual AI agent architecture with Gemini CLI for long-context sessions and Codex CLI for terminal/MCP operations:

### Gemini CLI Integration
- **Purpose**: Long-context sessions (1M+ tokens) with checkpointing for complex analysis
- **Configuration**: `~/.gemini/settings.json` with Gemini 2.5 Pro model
- **Environment**: Isolated API key management in `~/.config/gemantria/secrets.env`
- **Integration**: Makefile targets (`make gemini.task`, `make gemini.session`)

### Codex CLI Integration
- **Purpose**: Terminal operations and MCP server mode for Cursor integration
- **Configuration**: MCP server mode for Cursor orchestration
- **Integration**: Makefile targets (`make codex.task`) with CI guards

### MCP Server Architecture
- **Cursor Integration**: 3 MCP servers (GitHub: 46 tools, Gemantria-ops: 13 tools, Codex: 2 tools)
- **Configuration**: Settings-based configuration in `~/.config/Cursor/User/settings.json`
- **Security**: Hermetic CI operation (agents disabled in CI unless explicitly enabled)

## Consequences

### Positive
- **Long-context analysis**: Gemini enables complex multi-file, multi-concept analysis
- **Integrated workflow**: Cursor MCP integration provides seamless AI assistance
- **Operational safety**: CI guards prevent unintended AI operations in automated environments
- **Flexible usage**: Both direct terminal commands and integrated Cursor tools available

### Negative
- **Authentication complexity**: Multiple API key management (Gemini, OpenAI for Codex)
- **Resource usage**: Long-context sessions consume significant API resources
- **Learning curve**: Multiple tools and invocation methods to master

### Neutral
- **No breaking changes**: Existing workflows remain functional
- **Incremental adoption**: Tools can be used independently or together
- **Documentation overhead**: Additional runbooks and operational procedures required

## Implementation
- Gemini CLI: `npm install -g @google/gemini-cli`
- Codex CLI: Pre-installed, requires OpenAI API configuration
- MCP Configuration: Automated via Cursor settings.json
- Environment Setup: `.env` and user-level secrets management
- Makefile Integration: CI-guarded targets for safe operation

## Alternatives Considered
- **Single agent approach**: Would limit flexibility between long-context and integrated workflows
- **VS Code extensions**: Would reduce terminal flexibility and long-context capabilities
- **API-only integration**: Would lose conversational and interactive benefits

## References
- [Gemini CLI Documentation](https://github.com/google-gemini/gemini-cli)
- [OpenAI Codex CLI](https://developers.openai.com/codex/cli/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
