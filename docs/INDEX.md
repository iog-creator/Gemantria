# Gemantria Repository Index

**Quick navigation for all repository documentation and configuration.**

## 📋 Core Documentation

- **[AGENTS.md](../AGENTS.md)** - Agent framework, development workflow, priorities, and production safety
- **[README.md](../README.md)** - Project overview, setup, and quick start guide
- **[MASTER_PLAN.md](MASTER_PLAN.md)** - Project roadmap and current status
- **[DATA_FLOW_DIAGRAM.md](../DATA_FLOW_DIAGRAM.md)** - System architecture and data flow

## 🎯 Governance & Rules

- **[SSOT/RULES_INDEX.md](SSOT/RULES_INDEX.md)** - Complete index of all active Cursor rules
- **[SSOT/MASTER_PLAN.md](SSOT/MASTER_PLAN.md)** - Single source of truth for project planning
- **[.cursor/rules/](https://github.com/iog-creator/Gemantria/tree/main/.cursor/rules)** - All Cursor rule definitions
- **[AGENTS.md](../AGENTS.md#rules-summary)** - Rules summary and enforcement policies

## 🔧 Configuration & CI/CD

- **[.github/workflows/system-enforcement.yml](https://github.com/iog-creator/Gemantria/blob/main/.github/workflows/system-enforcement.yml)** - CI pipeline with policy gates
- **[.github/CODEOWNERS](https://github.com/iog-creator/Gemantria/blob/main/.github/CODEOWNERS)** - Code ownership for governance-critical paths
- **[.github/BRANCH_PROTECTION.md](https://github.com/iog-creator/Gemantria/blob/main/.github/BRANCH_PROTECTION.md)** - Branch protection configuration
- **[Makefile](../Makefile)** - Build targets and development commands

## 📊 Schemas & Data Models

- **[SSOT/graph-patterns.schema.json](SSOT/graph-patterns.schema.json)** - Graph patterns data schema
- **[SSOT/graph-stats.schema.json](SSOT/graph-stats.schema.json)** - Graph statistics data schema
- **[SSOT/pattern-forecast.schema.json](SSOT/pattern-forecast.schema.json)** - Pattern forecasting data schema
- **[SSOT/temporal-patterns.schema.json](SSOT/temporal-patterns.schema.json)** - Temporal patterns data schema

## 🗃️ Manifests & Sync

- **[SHARE_MANIFEST.json](../SHARE_MANIFEST.json)** - Defines what gets synced to share directory
- **[share/](https://github.com/iog-creator/Gemantria/tree/main/share)** - Mirrored artifacts for external access
- **[scripts/sync_share.py](../scripts/sync_share.py)** - Share directory synchronization script

## 📈 Latest Data & Reports

- **[exports/graph_latest.json](../exports/graph_latest.json)** - Latest concept network export
- **[exports/graph_stats.json](../exports/graph_stats.json)** - Current network statistics
- **[exports/pattern_forecast.json](../exports/pattern_forecast.json)** - Latest pattern forecasts
- **[reports/](https://github.com/iog-creator/Gemantria/tree/main/reports)** - Pipeline run reports and metrics

## 🧪 Testing & Quality

- **[tests/](https://github.com/iog-creator/Gemantria/tree/main/tests)** - Complete test suite (unit, integration, e2e)
- **[pyproject.toml](../pyproject.toml)** - Python dependencies and tool configuration
- **[requirements-dev.txt](../requirements-dev.txt)** - Development dependencies

## 🚀 Quick Commands

```bash
# Setup and verification
make doctor                    # Environment health check
make test                      # Run full test suite
make lint                      # Code quality checks

# Development workflow
make go                        # Full pipeline run with gates
make share.sync               # Sync documentation to share/
make rules.audit              # Validate rule system integrity

# Data operations
make data.verify              # Check data completeness (Rule 037)
make ci.exports.smoke         # Validate exports (Rule 038)

# Policy gates
make rules.numbering.check    # Verify rule numbering integrity
make share.check             # Ensure share mirror is clean
make ops.next                # Check NEXT_STEPS.md completion
```

## 🎯 Key Environment Variables

```bash
# Database connections
# IMPORTANT: All DSN access must go through centralized loaders:
# - Preferred: scripts.config.env (get_rw_dsn(), get_ro_dsn(), get_bible_db_dsn())
# - Legacy: src.gemantria.dsn (dsn_rw(), dsn_ro(), dsn_atlas())
# Never use os.getenv("GEMATRIA_DSN") directly - enforced by guard.dsn.centralized
GEMATRIA_DSN=postgresql://...    # Primary database
BIBLE_DB_DSN=postgresql://...    # Read-only reference database

# LM Studio configuration
LM_STUDIO_HOST=http://127.0.0.1:9991    # Answerer/Critic server
EMBED_URL=http://127.0.0.1:9994         # Embeddings server

# Pipeline configuration
CHECKPOINTER=postgres|memory    # State persistence (default: memory)
BATCH_SIZE=50                  # Processing batch size
ALLOW_PARTIAL=0|1             # Partial batch override

# Safety gates
ENFORCE_QWEN_LIVE=1           # Require live Qwen models
ALLOW_MOCKS_FOR_TESTS=0       # Production safety
```

## 📚 Architectural Decisions

- **[ADRs/](ADRs/)** - Architecture Decision Records
- **[ADR-000](../docs/ADRs/ADR-000-langgraph.md)** - LangGraph checkpointer architecture
- **[ADR-001](../docs/ADRs/ADR-001-two-db.md)** - Dual database design
- **[ADR-002](../docs/ADRs/ADR-002-batch-semantics.md)** - Batch processing semantics

## 🔍 Navigation Shortcuts

- **New to the project?** → Start with [AGENTS.md](../AGENTS.md) for development workflow
- **Need to understand the rules?** → Check [SSOT/RULES_INDEX.md](SSOT/RULES_INDEX.md)
- **Looking for schemas?** → See [SSOT/](SSOT/) directory
- **CI/CD issues?** → Review [.github/workflows/system-enforcement.yml](https://github.com/iog-creator/Gemantria/blob/main/.github/workflows/system-enforcement.yml)
- **Latest pipeline results?** → Check [reports/](https://github.com/iog-creator/Gemantria/tree/main/reports) and [exports/](../exports/)

---

**Last updated:** This index is automatically maintained. For questions, see [AGENTS.md](../AGENTS.md).
