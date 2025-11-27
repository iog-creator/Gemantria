# AGENTS.md - Runbooks Directory

## Directory Purpose

The `docs/runbooks/` directory contains operational runbooks that provide step-by-step procedures for common tasks, troubleshooting guides, and operational workflows. These runbooks enable consistent execution of operational tasks and serve as reference documentation for operators and developers.

## Key Documents

### Operational Runbooks

- **ATLAS_VISUAL_VERIFICATION.md** - Browser-based visual verification procedures for Atlas UI components
- **CODEX_CLI.md** - Codex CLI integration guide (installation, usage, examples)
- **CONTROL_SCHEMA.md** - Control-plane schema introspection procedures (Phase-3B Feature #8)
- **CONTROL_STATUS.md** - Control-plane status check procedures (Phase-3B Feature #6)
- **CONTROL_TABLES.md** - Control-plane tables listing procedures (Phase-3B Feature #7)
- **CURSOR_BROWSER_QA.md** - Browser QA procedures for Cursor agent interactions
- **DSN_SECRETS.md** - Database connection string management and security practices
- **HANDOFF_WORKFLOW.md** - Agent handoff procedures and evidence requirements
- **MCP_KNOWLEDGE_DB.md** - MCP Knowledge Database setup and usage (Postgres catalog-as-a-service)
- **MCP_SSE_AUTO_START.md** - LM Studio MCP SSE server auto-start configuration
- **VECTOR_DMS_WALKTHROUGH.md** - Vector DMS semantic search system walkthrough and usage guide
- **BIBLESCHOLAR_API_VERIFICATION.md** - BibleScholar API endpoints verification and usage

### Runbook Categories

1. **Control Plane**: Control-plane database introspection and status checks (Phase-3B)
2. **Visual Verification**: Browser-based UI testing and verification procedures
3. **Tool Integration**: External tool setup and usage guides
4. **Security**: Secrets management and secure configuration practices
5. **Workflow**: Agent handoff and operational workflow procedures
6. **Infrastructure**: Service setup and configuration guides

## Documentation Standards

### Runbook Structure

All runbooks should include:

1. **Purpose** - What the runbook accomplishes
2. **Prerequisites** - Required tools, access, or configuration
3. **Step-by-step procedures** - Detailed execution steps
4. **Verification** - How to confirm successful completion
5. **Troubleshooting** - Common issues and solutions
6. **Related documentation** - Links to relevant ADRs, rules, or other docs

### Runbook Format

- **Markdown format**: All runbooks use Markdown for consistency
- **Code blocks**: Use appropriate language tags for code examples
- **Command examples**: Include exact commands with expected outputs
- **Screenshots**: Include visual references when helpful (stored in `docs/atlas/webproof/`)

### Runbook Maintenance

- **Keep current**: Update runbooks when procedures change
- **Test procedures**: Verify runbook steps work as documented
- **Add troubleshooting**: Document common issues and solutions
- **Cross-reference**: Link to related ADRs, rules, or other runbooks

## Development Guidelines

### Creating New Runbooks

1. **Identify need**: Document operational procedures that are repeated or complex
2. **Follow structure**: Use standard runbook format (Purpose, Prerequisites, Steps, Verification)
3. **Test procedures**: Verify all steps work as documented
4. **Add to index**: Update this AGENTS.md with new runbook entry
5. **Cross-reference**: Link to related ADRs, rules, or documentation

### Updating Existing Runbooks

1. **Verify accuracy**: Test updated procedures before committing
2. **Update version**: Note changes in runbook header or changelog
3. **Notify team**: Alert relevant team members to procedure changes
4. **Archive old versions**: Keep historical versions if significant changes

### Runbook Quality Standards

- **Clarity**: Steps should be unambiguous and easy to follow
- **Completeness**: Include all necessary context and prerequisites
- **Accuracy**: Verify all commands and procedures work as documented
- **Maintainability**: Keep runbooks current with system changes

## Related Documentation

### Visual Verification

- **ATLAS_VISUAL_VERIFICATION.md**: Browser-based UI verification procedures
- **CURSOR_BROWSER_QA.md**: Cursor agent browser interaction QA
- **Rule 067**: Atlas Webproof (browser-verified UI) requirements

### Control Plane Operations

- **CONTROL_STATUS.md**: Control-plane status check and table row counts
- **CONTROL_TABLES.md**: Control-plane tables listing with row counts
- **CONTROL_SCHEMA.md**: Control-plane schema introspection (DDL)
- **Phase-3B**: Control-plane CLI commands via `pmagent control` subcommands

### Tool Integration

- **CODEX_CLI.md**: Codex CLI setup and usage
- **MCP_KNOWLEDGE_DB.md**: MCP Knowledge Database integration
- **MCP_SSE_AUTO_START.md**: LM Studio MCP SSE server configuration

### Security & Configuration

- **DSN_SECRETS.md**: Database connection string security practices
- **Rule 062**: Environment validation requirements
- **Rule 046**: Hermetic CI fallbacks (DB-off tolerance)

### Workflow Procedures

- **HANDOFF_WORKFLOW.md**: Agent handoff and evidence requirements
- **Rule 051**: Cursor Insight & Handoff (evidence-first protocol)
- **Rule 050**: OPS Contract (4-block output format)

## Integration with Governance

### Rule 051 - Cursor Insight & Handoff

Runbooks support the handoff workflow by providing:

- **Evidence requirements**: What evidence must be collected
- **Verification steps**: How to validate handoff readiness
- **Next gate procedures**: What happens after handoff

### Rule 067 - Atlas Webproof

Visual verification runbooks support browser-verified UI requirements:

- **Browser tool usage**: Procedures for using browser verification tools
- **Screenshot procedures**: How to capture and verify visual evidence
- **Backlink validation**: Procedures for verifying webproof backlinks

### Rule 062 - Environment Validation

DSN and configuration runbooks support environment validation:

- **Venv activation**: Procedures for activating virtual environment
- **DSN verification**: How to verify database connection strings
- **Configuration checks**: Procedures for validating environment setup

## Maintenance Notes

- **Regular review**: Audit runbooks quarterly for accuracy and relevance
- **Update on changes**: Modify runbooks when procedures or tools change
- **Test procedures**: Verify runbook steps work before committing updates
- **Archive evidence**: Store runbook execution evidence in `share/evidence/` when applicable
- **Cross-reference**: Maintain links between runbooks and related governance rules
