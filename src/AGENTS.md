# AGENTS.md — Core Pipeline Agents

## Purpose

Defines the operational agents and nodes in the Gematria LangGraph pipeline. This document serves as the single source of truth for pipeline component responsibilities and architectural relationships.

## Core Nodes

| Node                  | Purpose                                        | Related ADRs              |
| --------------------- | ---------------------------------------------- | ------------------------- |
| extraction.py         | Hebrew noun extraction + triple verification   | ADR-002, ADR-009          |
| validation.py         | Schema and duplication checks                  | ADR-003                   |
| enrichment.py         | AI theological insight generation              | ADR-007, ADR-008          |
| network_aggregator.py | Embedding + relations build (bi-encoder proxy) | ADR-010, ADR-014, ADR-026 |
| integration.py        | DB persistence layer                           | ADR-001, ADR-004          |
| retrieval.py          | Query interface                                | ADR-006                   |

## Infrastructure Agents

| Service            | Description                | Related ADRs     |
| ------------------ | -------------------------- | ---------------- |
| checkpointer.py    | Postgres state persistence | ADR-004          |
| metrics_queries.py | Observability & metrics    | ADR-005, ADR-006 |

## Directory Structure

```
src/
├── core/          # Core pipeline logic (extraction, validation)
├── graph/         # Graph processing and network aggregation
├── infra/         # Infrastructure (DB, checkpointer, logging)
├── nodes/         # LangGraph node implementations
└── services/      # External service integrations
```

## Related Documentation

- **Parent**: [AGENTS.md](../AGENTS.md) - Repository overview
- **Rules**: [.cursor/rules/003-graph-and-batch.mdc](../../.cursor/rules/003-graph-and-batch.mdc)
- **SSOT**: [docs/SSOT/](../../docs/SSOT/) - Canonical schemas
