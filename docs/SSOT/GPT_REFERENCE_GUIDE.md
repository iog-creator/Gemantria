# GPT Reference Guide - Gemantria Project Files

This guide explains the 20 essential files available for GPT analysis of the Gemantria project.

## Core Project Documentation

**AGENTS.md** - Agent framework and operational contracts. Defines how automated agents work, their responsibilities, and governance rules.

**GEMATRIA_MASTER_REFERENCE.md** - Complete project master reference (1,183 lines). Contains all project details, architecture, agent contracts, rules, schemas, and operational procedures.

**MASTER_PLAN.md** - High-level project roadmap and goals. Strategic vision and phase planning.

**RULES_INDEX.md** - Complete index of all project rules. Governance framework with 60+ numbered rules for compliance.

## Configuration & Setup

**env_example.txt** - Environment variable template. Shows all required configuration variables.

**pyproject.toml** - Python project configuration. Dependencies, build settings, and tool configurations.

**pytest.ini** - Test configuration. How tests are run and configured.

**Makefile** - Build and automation targets. All available `make` commands for development, testing, and deployment.

## Schemas & Data Structures

**ai-nouns.schema.json** - Schema for AI-generated noun data. Defines structure of enriched concept data.

**graph.schema.json** - Schema for semantic network data. Defines node/edge structure for concept graphs.

**graph-patterns.schema.json** - Schema for graph pattern analysis. Community detection and centrality metrics.

**graph-stats.schema.json** - Schema for graph statistics. Network health and performance metrics.

**graph_stats.head.json** - Sample graph statistics data. Real example of graph analysis output.

## Documentation

**README.md** - Project overview and quick start. Basic introduction and setup instructions.

**README_FULL.md** - Comprehensive project documentation. Detailed guides and references.

**CHANGELOG.md** - Version history and changes. What changed in each release.

**RELEASES.md** - Release notes and deployment info. Version-specific release information.

## Development Workflow

**pull_request_template.md** - PR template requirements. What must be included in pull requests.

**pre-commit-config.yaml** - Code quality hooks. Automated checks that run before commits.

**SHARE_MANIFEST.json** - File sharing configuration. Defines which files are shared and how.

## Usage Guidelines for GPT

1. **Start with GEMATRIA_MASTER_REFERENCE.md** for complete project understanding
2. **Reference AGENTS.md** for operational procedures and agent contracts
3. **Check RULES_INDEX.md** for governance compliance requirements
4. **Use schemas** to understand data structures and validation rules
5. **Review Makefile** for available automation commands
6. **Check env_example.txt** for configuration requirements

## File Limits

This curated set of 20 files stays within GPT's 22-file upload limit while providing comprehensive project understanding.
