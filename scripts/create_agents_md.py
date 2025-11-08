# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
"""
create_agents_md.py — Automatically create missing AGENTS.md files in required directories.

This script ensures AGENTS.md files exist in all directories that require them according to
Rule 009 - Documentation Sync. It creates missing files with appropriate templates based
on directory type and purpose.

Rule 009 Requirements:
- Source Code Directories (src/*/) - AGENTS.md: Required
- Tool Directories (scripts/, migrations/, tests/) - AGENTS.md: Required
- Documentation Directories (docs/*/) - AGENTS.md: Required
- Generated/Output Directories (reports/, exports/, data/) - AGENTS.md: Not required
- Configuration Directories (.cursor/*/) - AGENTS.md: Not required

Usage:
    python scripts/create_agents_md.py  # Create missing AGENTS.md files
    python scripts/create_agents_md.py --dry-run  # Show what would be created
"""

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def get_required_directories() -> dict[str, list[str]]:
    """Get directories that require AGENTS.md files, grouped by type."""
    # Directories to exclude from AGENTS.md requirement
    EXCLUDED_DIRS = {
        "__pycache__",  # Python bytecode cache
        ".git",  # Git metadata
        "node_modules",  # Node.js dependencies
        ".venv",  # Python virtual environment
        "venv",  # Python virtual environment (alternate)
        ".pytest_cache",  # Pytest cache
        ".mypy_cache",  # Mypy cache
        ".ruff_cache",  # Ruff cache
        "__pypackages__",  # PDM packages
    }

    required = {
        "source": [],  # src/*/
        "tools": ["scripts", "migrations", "tests"],  # Tool directories
        "docs": [],  # docs/*/
    }

    # Add all src subdirectories (excluding cache/generated dirs)
    src_dir = ROOT / "src"
    if src_dir.exists():
        for subdir in src_dir.iterdir():
            if subdir.is_dir() and not subdir.name.startswith(".") and subdir.name not in EXCLUDED_DIRS:
                required["source"].append(f"src/{subdir.name}")

    # Add all docs subdirectories (excluding cache/generated dirs)
    docs_dir = ROOT / "docs"
    if docs_dir.exists():
        for subdir in docs_dir.iterdir():
            if subdir.is_dir() and not subdir.name.startswith(".") and subdir.name not in EXCLUDED_DIRS:
                required["docs"].append(f"docs/{subdir.name}")

    return required


def get_existing_agents_files() -> set[str]:
    """Get all existing AGENTS.md file paths relative to root."""
    existing = set()
    for agents_file in ROOT.glob("**/AGENTS.md"):
        rel_path = agents_file.relative_to(ROOT)
        existing.add(str(rel_path.parent / "AGENTS.md"))
    return existing


def get_missing_agents_files() -> dict[str, list[str]]:
    """Get AGENTS.md files that need to be created, grouped by directory type."""
    required = get_required_directories()
    existing = get_existing_agents_files()

    missing: dict[str, list[str]] = {"source": [], "tools": [], "docs": []}

    # Check source directories
    for src_subdir in required["source"]:
        agents_path = f"{src_subdir}/AGENTS.md"
        if agents_path not in existing:
            missing["source"].append(src_subdir)

    # Check tool directories
    for tool_dir in required["tools"]:
        agents_path = f"{tool_dir}/AGENTS.md"
        if agents_path not in existing:
            missing["tools"].append(tool_dir)

    # Check docs directories
    for docs_subdir in required["docs"]:
        agents_path = f"{docs_subdir}/AGENTS.md"
        if agents_path not in existing:
            missing["docs"].append(docs_subdir)

    return missing


def create_source_agents_md(dir_path: str) -> str:
    """Create AGENTS.md content for source code directories."""
    dir_name = Path(dir_path).name

    template = f"""# AGENTS.md - {dir_path} Directory

## Directory Purpose

The `{dir_path}/` directory contains {dir_name} components for the Gematria analysis pipeline.

## Key Components

<!-- Add key components and their purposes here -->

## API Contracts

<!-- Add function/class signatures and contracts here -->

## Testing Strategy

<!-- Add testing approach and coverage requirements here -->

## Development Guidelines

<!-- Add coding standards and patterns specific to this directory here -->

## Related ADRs

| Component/Function | Related ADRs |
|-------------------|--------------|
<!-- Add ADR references here -->
"""
    return template


def create_tools_agents_md(dir_path: str) -> str:
    """Create AGENTS.md content for tool directories."""
    dir_name = Path(dir_path).name

    # Special handling for different tool directories
    if dir_name == "scripts":
        return """# AGENTS.md - Scripts Directory

## Directory Purpose

The `scripts/` directory contains executable scripts for pipeline operations, reporting, testing, and maintenance tasks.
These scripts provide command-line interfaces for common development and operational workflows.

## Key Scripts

<!-- Add script descriptions here following the pattern in scripts/AGENTS.md -->

## Script Categories

### Pipeline Operations
<!-- Scripts for running and monitoring the pipeline -->

### Development Tools
<!-- Scripts for development workflow (linting, testing, etc.) -->

### Deployment Scripts
<!-- Scripts for deployment and operations -->

## Script Standards

### Environment Loading (CRITICAL - Always Apply)
All scripts must load environment variables consistently to prevent database connectivity issues.

```python
# REQUIRED: Add this to ALL scripts that use environment variables
from src.infra.env_loader import ensure_env_loaded  # noqa: E402

# Load environment variables from .env file (REQUIRED)
ensure_env_loaded()
```

### Command-Line Interface
- Help: `--help` for all scripts
- Arguments: Clear parameter naming and validation
- Output: Consistent formatting and error codes
- Logging: Structured logging with appropriate verbosity

### Error Handling
- Graceful Failures: Clear error messages and exit codes
- Recovery: Where possible, suggest remediation steps
- Logging: Detailed error information for debugging

### Configuration
- Environment: Use environment variables for configuration
- Defaults: Sensible defaults with override capability
- Validation: Input validation with helpful error messages
- Loading: MANDATORY `ensure_env_loaded()` call for all database scripts

## Development Guidelines

### Adding New Scripts
1. Purpose: Clear, single responsibility
2. Interface: Command-line arguments and help
3. Error Handling: Robust error handling and logging
4. Testing: Unit tests for script logic
5. Documentation: Inline help and README updates

### Script Maintenance
1. Updates: Keep scripts current with API changes
2. Testing: Automated testing of script execution
3. Documentation: Update usage examples and parameters
4. Deprecation: Clear migration path for replaced scripts

## Execution Environment

### Dependencies
- Python: Required version and virtual environment
- System Tools: bash, make, git for CI/CD integration
- External Services: Database, LM Studio for full functionality

### Security Considerations
- Input Validation: Sanitize all user inputs
- Credentials: Secure handling of API keys and passwords
- Permissions: Appropriate file and database permissions
- Audit Trail: Logging of script execution and changes

## Testing Strategy

### Script Testing
- Unit Tests: Test script logic in isolation
- Integration Tests: Test with real dependencies
- End-to-End: Full workflow validation

### CI/CD Integration
- Automated Execution: Scripts run in CI pipelines
- Artifact Generation: Reports and logs as CI artifacts
- Quality Gates: Script success as merge requirements

## Maintenance & Operations

### Monitoring
- Execution Logs: Track script runs and performance
- Failure Alerts: Notification for script failures
- Performance Metrics: Execution time and resource usage

### Troubleshooting
- Debug Mode: Verbose logging for issue diagnosis
- Dry Run: Preview changes without execution
- Rollback: Safe reversal of script actions

### Documentation
- README: Script catalog with usage examples
- Inline Help: `--help` for all scripts
- Runbooks: Operational procedures using scripts
"""

    elif dir_name == "migrations":
        return """# AGENTS.md - Migrations Directory

## Directory Purpose

The `migrations/` directory contains database schema migration scripts for the Gematria analysis system.
These migrations ensure consistent database schema evolution across development and production environments.

## Migration Scripts

<!-- Document migration files and their purposes here -->

## Migration Standards

### File Naming
- Format: `NNN_description.sql` where NNN is sequential number
- Examples: `001_initial_schema.sql`, `002_create_checkpointer.sql`

### Content Standards
- **Transactional**: Each migration should be wrapped in a transaction
- **Idempotent**: Safe to run multiple times
- **Rollback**: Include rollback instructions in comments
- **Tested**: Verified against clean database state

### Execution Order
- Migrations run in numerical order
- No gaps in numbering allowed
- Each migration depends on the previous state

## Development Guidelines

### Creating New Migrations
1. **Check Current State**: Review existing migrations
2. **Sequential Numbering**: Use next available number
3. **Clear Description**: Descriptive name for the change
4. **Test Locally**: Apply and rollback on development database
5. **Document Changes**: Update this AGENTS.md file

### Migration Testing
1. **Clean Apply**: Test on empty database
2. **Incremental Apply**: Test on database with previous migrations
3. **Rollback Test**: Verify rollback works correctly
4. **Data Preservation**: Ensure no data loss during migration

## Related ADRs

| Migration | Related ADRs | Description |
|-----------|--------------|-------------|
<!-- Add migration to ADR mappings here -->
"""

    elif dir_name == "tests":
        return """# AGENTS.md - Tests Directory

## Directory Purpose

The `tests/` directory contains comprehensive test suites for the Gematria analysis system,
ensuring code quality, correctness, and reliability through automated validation.

## Test Organization

### test_*.py Structure
```
tests/
├── unit/          # Unit tests (isolated functions/classes)
├── integration/   # Integration tests (component interaction)
├── e2e/          # End-to-end tests (full pipeline)
└── smoke/        # Smoke tests (basic functionality)
```

## Test Categories

### Unit Tests (`tests/unit/`)
- **Scope**: Individual functions, classes, and modules
- **Dependencies**: Minimal mocking, focus on isolated logic
- **Coverage**: ≥98% line coverage required
- **Execution**: `make test.unit`

### Integration Tests (`tests/integration/`)
- **Scope**: Component interactions and data flow
- **Dependencies**: Real database connections, external services
- **Coverage**: Critical integration paths
- **Execution**: `make test.integration`

### End-to-End Tests (`tests/e2e/`)
- **Scope**: Complete pipeline execution
- **Dependencies**: Full environment setup
- **Coverage**: User-facing workflows
- **Execution**: `make test.e2e`

### Smoke Tests (`tests/smoke/`)
- **Scope**: Basic functionality verification
- **Dependencies**: Minimal setup, fast execution
- **Coverage**: Critical failure points
- **Execution**: `make test.smoke`

## Testing Standards

### Code Coverage
- **Unit Tests**: ≥98% coverage required (CI gate)
- **Integration Tests**: Key interaction points
- **Overall**: Combined coverage ≥95%

### Test Naming
- **Files**: `test_*.py`
- **Functions**: `test_*()`
- **Classes**: `Test*`

### Test Isolation
- **Database**: Use test databases or transactions
- **External Services**: Mock when possible, skip when unavailable
- **State**: Clean up after each test

## Test Data Management

### Test Datasets
- **Source**: Code-verified or DB-derived only (Rule 001)
- **No Mocks**: Production code never uses mock datasets (Rule 011)
- **Deterministic**: Fixed seeds and reproducible data

### Database Testing
- **Transactions**: Rollback after each test
- **Isolation**: Separate test database/schema
- **Cleanup**: Automatic cleanup on test completion

## CI/CD Integration

### Automated Execution
- **Pre-commit**: Fast smoke tests
- **PR Validation**: Full test suite
- **Merge Gates**: Coverage and test pass requirements

### Test Environments
- **Local**: Full test execution
- **CI**: Parallel test execution
- **Production**: Smoke tests only

## Development Guidelines

### Writing Tests
1. **ARRANGE-ACT-ASSERT**: Clear test structure
2. **Descriptive Names**: Explain what and why
3. **Minimal Setup**: Only required test data
4. **Fast Execution**: Optimize for quick feedback

### Test Maintenance
1. **Update on Changes**: Modify tests when code changes
2. **Remove Obsolete**: Delete tests for removed features
3. **Add New Coverage**: Tests for new functionality
4. **Refactor**: Improve test readability and maintainability

## Debugging Tests

### Common Issues
- **Flaky Tests**: Identify and fix non-deterministic behavior
- **Slow Tests**: Optimize execution time
- **False Positives**: Ensure tests fail only on real issues

### Debugging Tools
- **Verbose Output**: Use `-v` flag for detailed test output
- **PDB**: Interactive debugging with `import pdb; pdb.set_trace()`
- **Logging**: Enable debug logging for test execution

## Related ADRs

| Test Category | Related ADRs | Description |
|---------------|--------------|-------------|
<!-- Add test category to ADR mappings here -->
"""

    # Fallback for unrecognized tool directories
    template = f"""# AGENTS.md - {dir_path} Directory

## Directory Purpose

The `{dir_path}/` directory contains {dir_name} tools for the Gematria analysis pipeline.

## Key Tools

<!-- Add key tools and their purposes here -->

## Tool Categories

<!-- Add tool categories and their purposes here -->

## Tool Standards

<!-- Add tool standards and conventions here -->

## Related ADRs

| Tool/Component | Related ADRs |
|----------------|--------------|
<!-- Add ADR references here -->
"""
    return template


def create_docs_agents_md(dir_path: str) -> str:
    """Create AGENTS.md content for documentation directories."""
    dir_name = Path(dir_path).name

    if dir_name == "ADRs":
        return """# AGENTS.md - ADRs Directory

## Directory Purpose

The `docs/ADRs/` directory contains Architecture Decision Records that document significant architectural decisions
made during the development of the Gematria analysis system.

## ADR Categories

### Schema Decisions
<!-- Database schema, data model, and structural decisions -->

### Algorithm Decisions
<!-- Core algorithms, processing logic, and computational approaches -->

### Infrastructure Decisions
<!-- Deployment, scaling, and operational architecture -->

### Process Decisions
<!-- Development workflow, quality gates, and organizational processes -->

## ADR Standards

### File Naming
- Format: `ADR-NNN-title.md` where NNN is sequential number
- Examples: `ADR-001-initial-architecture.md`, `ADR-013-report-generation.md`

### Content Structure
- **Context**: Problem statement and background
- **Decision**: What was decided and why
- **Rationale**: Benefits and trade-offs
- **Alternatives**: Other options considered
- **Consequences**: Implementation requirements and impacts

### Status Tracking
- **Proposed**: Initial decision pending implementation
- **Accepted**: Decision approved and implementation in progress
- **Rejected**: Decision not pursued
- **Deprecated**: Decision no longer relevant
- **Superseded**: Decision replaced by newer ADR

## ADR Lifecycle

### Creation Process
1. **Identify Decision**: Recognize need for architectural decision
2. **Draft ADR**: Document context, options, and recommendation
3. **Review**: Technical review and stakeholder feedback
4. **Approval**: Decision acceptance and implementation planning
5. **Implementation**: Code changes and documentation updates

### Maintenance
1. **Updates**: Modify ADRs when decisions change
2. **Cross-references**: Link related ADRs and implementation
3. **Archival**: Mark deprecated ADRs clearly
4. **Indexing**: Keep ADR index current

## Implementation Tracking

### ADR Status Matrix

| ADR | Title | Status | Implementation |
|-----|-------|--------|----------------|
<!-- Add ADR status tracking table here -->

## Related Documentation

- **MASTER_PLAN.md**: High-level project roadmap and phase planning
- **AGENTS.md**: AI assistant development guidance
- **README.md**: User-facing documentation and quick start guide
"""

    elif dir_name == "SSOT":
        return """# AGENTS.md - SSOT Directory

## Directory Purpose

The `docs/SSOT/` directory contains Single Source of Truth documents that define canonical schemas, contracts,
and specifications for the Gematria analysis system.

## SSOT Documents

### Schema Files
- **graph-patterns.schema.json**: Validation schema for graph pattern analysis exports
- **temporal-patterns.schema.json**: Schema for time-series pattern analysis
- **pattern-forecast.schema.json**: Schema for forecasting model outputs
- **graph-stats.schema.json**: Schema for graph statistics and metrics
- **graph-correlations.schema.json**: Schema for concept correlation data

### Contract Documents
- **graph-metrics-api.md**: API contract for graph metrics endpoints
- **graph-stats-api.md**: API contract for statistics endpoints
- **visualization-config.md**: Configuration contract for visualization components
- **webui-contract.md**: Contract between backend and frontend visualization

### Reference Documents
- **data_flow.md**: Data flow diagrams and pipeline architecture
- **data_flow_visual.md**: Visual representations of data flows
- **jsonld-schema.md**: JSON-LD and semantic web standards
- **rdf-ontology.md**: RDF ontology definitions and namespaces

## SSOT Standards

### Schema Validation
- **JSON Schema**: All schemas follow JSON Schema Draft 2020-12
- **Versioning**: Schema versions tracked in filenames and content
- **Backwards Compatibility**: Schema changes maintain backwards compatibility
- **Documentation**: All schemas include inline documentation

### Contract Compliance
- **Interface Definition**: Clear input/output specifications
- **Error Handling**: Defined error responses and codes
- **Versioning**: API version compatibility guarantees
- **Testing**: Contract tests validate compliance

### Document Maintenance
- **Single Source**: Each specification has one authoritative location
- **Cross-references**: Links between related specifications
- **Update Process**: Controlled process for specification changes
- **Validation**: Automated validation of specification compliance

## Development Integration

### Code Generation
- **Type Hints**: Generate Python type hints from schemas
- **Validation Code**: Auto-generate input validation from contracts
- **Test Data**: Generate test fixtures from schema examples

### Quality Gates
- **Schema Validation**: All exports validated against schemas
- **Contract Testing**: API compliance verified against contracts
- **Cross-reference Checks**: Specification links verified and current

## Usage Guidelines

### For Developers
1. **Reference SSOT**: Always reference these documents for specifications
2. **Validate Changes**: Ensure changes don't break existing contracts
3. **Update Documents**: Modify specifications when interfaces change
4. **Test Compliance**: Verify implementations meet specification requirements

### For Reviewers
1. **Check References**: Ensure code references correct SSOT documents
2. **Validate Contracts**: Verify API changes update contracts
3. **Schema Compliance**: Confirm data structures match schemas
4. **Documentation Sync**: Ensure docs reflect current implementation

## Related ADRs

| Document | Related ADRs | Description |
|----------|--------------|-------------|
| graph-patterns.schema.json | ADR-016 | Graph pattern analysis specification |
| temporal-patterns.schema.json | ADR-034 | Temporal pattern analysis framework |
| pattern-forecast.schema.json | ADR-035 | Forecasting model specifications |
| webui-contract.md | ADR-022 | Backend-frontend visualization contract |
"""

    else:
        # Generic docs template
        return f"""# AGENTS.md - {dir_path} Directory

## Directory Purpose

The `{dir_path}/` directory contains documentation for the {dir_name} aspects of the Gematria analysis system.

## Key Documents

<!-- Add key documents and their purposes here -->

## Documentation Standards

<!-- Add documentation standards and guidelines here -->

## Development Guidelines

<!-- Add guidelines for maintaining this documentation here -->

## Related ADRs

| Document | Related ADRs |
|----------|--------------|
<!-- Add document to ADR mappings here -->
"""


def create_agents_md_file(dir_path: str, dry_run: bool = False) -> bool:
    """Create AGENTS.md file for the given directory path."""
    full_path = ROOT / dir_path
    agents_file = full_path / "AGENTS.md"

    if agents_file.exists():
        print(f"SKIP: {agents_file} already exists")
        return False

    # Determine directory type and create appropriate content
    if dir_path.startswith("src/"):
        content = create_source_agents_md(dir_path)
    elif dir_path in ["scripts", "migrations", "tests"]:
        content = create_tools_agents_md(dir_path)
    elif dir_path.startswith("docs/"):
        content = create_docs_agents_md(dir_path)
    else:
        print(f"SKIP: {dir_path} not recognized as requiring AGENTS.md")
        return False

    if dry_run:
        print(f"WOULD CREATE: {agents_file}")
        return True

    # Create the directory if it doesn't exist (though it should)
    full_path.mkdir(parents=True, exist_ok=True)

    # Write the AGENTS.md file
    agents_file.write_text(content)
    print(f"CREATED: {agents_file}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Create missing AGENTS.md files")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be created without actually creating files",
    )
    args = parser.parse_args()

    missing = get_missing_agents_files()

    total_missing = sum(len(dirs) for dirs in missing.values())
    if total_missing == 0:
        print("✅ All required AGENTS.md files exist")
        return

    print(f"Found {total_missing} missing AGENTS.md files:")

    created = 0
    for category, dirs in missing.items():
        if not dirs:
            continue
        print(f"\n{category.upper()} DIRECTORIES:")
        for dir_path in dirs:
            if create_agents_md_file(dir_path, args.dry_run):
                created += 1

    if not args.dry_run:
        print(f"\n✅ Created {created} AGENTS.md files")
        print("Run 'make rules.audit docs.audit' to verify compliance")
    else:
        print(f"\n📋 Would create {created} AGENTS.md files (use without --dry-run to create)")


if __name__ == "__main__":
    main()
