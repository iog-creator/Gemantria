# Gemantria

<div align="left">
  <img alt="xref coverage" src="share/eval/badges/xrefs_coverage.svg" />
  <img alt="xref rate" src="share/eval/badges/xrefs_rate.svg" />
  <img alt="RFC3339" src="share/eval/badges/rfc3339.svg" />

[![Tagproof](https://github.com/iog-creator/Gemantria/actions/workflows/tagproof.yml/badge.svg)](../../actions/workflows/tagproof.yml)
</div>

**AI-powered Hebrew gematria analysis and biblical text exploration.**

---

## ⚠️ Kernel-Governed Repository

**This is NOT a normal Python project.** Before doing any work:

1. Run `make ops.kernel.check` — must succeed
2. Run `make reality.green` — 18/18 checks must pass
3. Read [`START_HERE.md`](START_HERE.md) for the complete boot guide

If the kernel reports `mode = DEGRADED`, only perform PM-approved remediation work.

---

## Overview

Gemantria builds a deterministic LangGraph pipeline that produces verified gematria data and visualization-ready artifacts for biblical text analysis.

### Core Capabilities

- **Noun Extraction** — Extract Hebrew nouns from Bible database
- **AI Enrichment** — Generate theological insights using Granite/Qwen models
- **Network Building** — Create semantic embeddings and relationships
- **Graph Analysis** — Community detection and centrality measures
- **DSPy Reasoning** — 8 specialized reasoning programs for intelligent decisions

### Current Phase: 28B

- ✅ Phase 28B: 8 DSPy reasoning programs wired with 126 training examples
- ✅ Phase 27: DMS-exclusive governance, OA runtime, kernel interpreter
- ✅ Phase 26: Kernel enforcement and boot mandates
- ✅ Phase 24-25: Backup system, handoff protocol, share sync

---

## Quick Start

```bash
# 1. Activate virtual environment
python -m venv .venv && source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Verify system health
make ops.kernel.check
make reality.green
```

---

## Key Commands

### Governance
```bash
make ops.kernel.check      # Kernel health check (mandatory)
make reality.green         # Full system truth gate (18 checks)
make housekeeping          # DMS sync, embeddings, cleanup
make backup.surfaces       # Create backup before destructive ops
```

### Development
```bash
make lint                  # Ruff format + check
make test.unit             # Run unit tests
make book.smoke            # Book processing smoke test
```

### Pipeline
```bash
make orchestrator.full BOOK=Genesis    # Full integrated pipeline
make analyze.export                    # Generate analysis exports
make schema.validate                   # Validate JSON schemas
```

---

## Project Structure

```
├── pmagent/             # Control plane (kernel, DMS, OA)
│   ├── oa/              # Orchestrator Assistant (DSPy reasoning)
│   ├── hints/           # Hint registry
│   └── kernel/          # Kernel interpreter
├── src/                 # Core gematria and graph modules
├── scripts/             # Governance, guards, utilities
├── share/               # Materialized surfaces (SSOT exports)
├── docs/                # SSOT, ADRs, analysis
└── examples/dspy/       # DSPy training data (126 examples)
```

---

## DSPy Reasoning Programs

| Program | Purpose |
|---------|---------|
| SafeOPSDecision | Decide if proposed OPS work is safe |
| OPSBlockGenerator | Generate OPS blocks from PM goals |
| GuardFailureInterpreter | Interpret guard failures |
| PhaseTransitionValidator | Validate phase transitions |
| HandoffIntegrityValidator | Validate handoff integrity |
| OAToolUsagePrediction | Predict optimal tool usage |
| ShareDMSDriftDetector | Detect share/DMS drift |
| MultiTurnKernelReasoning | Multi-turn kernel reasoning |

Training data: `examples/dspy/*.jsonl` (126 examples total)

---

## Governance Rules

- **Rule 050** — OPS Contract (LOUD FAIL gates)
- **Rule 051** — CI gating posture
- **Rule 052** — Tool priority (local → codex → gemini)
- **Rule 070** — Gotchas Check (pre/post work)
- **Rule 071** — Artifact/walkthrough protocol

See [`RULES_INDEX.md`](RULES_INDEX.md) for full rules.

---

## DSN Centralization

All database connections via centralized loaders:

```python
from scripts.config.env import get_rw_dsn, get_ro_dsn, get_bible_db_dsn
```

Never use `os.getenv("GEMATRIA_DSN")` directly.

---

## Documentation

- [START_HERE.md](START_HERE.md) — Agent/human boot guide
- [AGENTS.md](AGENTS.md) — Agent framework index
- [RULES_INDEX.md](RULES_INDEX.md) — Governance rules
- [docs/SSOT/EXECUTION_CONTRACT.md](docs/SSOT/EXECUTION_CONTRACT.md) — Execution rules
- [docs/SSOT/MASTER_PLAN.md](docs/SSOT/MASTER_PLAN.md) — Project roadmap

---

## License

Private repository — IOG Creator

