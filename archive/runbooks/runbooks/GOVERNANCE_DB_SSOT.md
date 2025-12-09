# Governance DB SSOT Runbook — Cursor Rules

## Purpose

This runbook documents how Cursor rules (`.cursor/rules/*.mdc`) are ingested

into the control-plane database and how to validate that the database is the

single source of truth (SSOT) for governance.

This implements the Phase-7 Governance plan described in:

- docs/analysis/phase7_governance/GEMANTRIA_SYSTEM_COMPREHENSIVE_REPORT.md

- docs/analysis/phase7_governance/PHASE_1_7_GOVERNANCE_DRIFT_MAP.md

## Tables

The following tables live in the `control` schema:

- `control.rule_definition`

- `control.rule_source`

- `control.guard_definition` (future use)

They are created by the `*_control_rules_schema.sql` migration in `migrations/`.

## Commands

### 1. Dry-run ingestion (no DB writes)

```bash
make governance.ingest.rules.dryrun
```

This:

* Scans `.cursor/rules/*.mdc`

* Parses rule ids and names

* Logs what would be written to the DB

### 2. Real ingestion

```bash
make governance.ingest.rules
```

This:

* Upserts rows into `control.rule_definition`

* Inserts corresponding entries into `control.rule_source`

### 3. Guard: DB SSOT validation

```bash
make guard.rules.db.ssot
```

This:

* Compares local `.cursor/rules/*.mdc` to DB contents

* Emits a JSON verdict to stdout with `ok`, `mode`, and `reason`

* Is DB-off tolerant (mode `db_off` instead of crashing)

## Posture

* HINT on PRs and main (non-fatal mismatches)

* STRICT on tags (via `ops.tagproof` target)

## Phase-8C: Doc Content + Embeddings (RAG-Ready)

Phase-8C extends the governance DB SSOT to include full document content and embeddings:

### Doc Fragments

* **Ingestion**: `make governance.ingest.doc_content` fragments docs into `control.doc_fragment`
* **Guard**: `make guard.docs.fragments` validates Tier-0 AGENTS docs have fragments
* **STRICT**: Tier-0 docs must have fragments in STRICT mode

### Doc Embeddings

* **Ingestion**: `make governance.ingest.doc_embeddings` generates embeddings for fragments
* **Guard**: `make guard.docs.embeddings` validates Tier-0 AGENTS docs have embeddings
* **STRICT**: Tier-0 docs must have embeddings in STRICT mode

### Search

* **CLI**: `pmagent docs.search "query text" --k 10` performs semantic search over embeddings
* **Scope**: By default searches only Tier-0 docs (AGENTS_ROOT + AGENTS::*)
* **Usage**: `pmagent docs.search "STRICT guard for embeddings" --k 5 --json-only`

### Tier-0 Enforcement

In STRICT mode (tags), Tier-0 docs must satisfy all three guards:

1. **Registry + versions** (`guard_docs_db_ssot`)
2. **Fragments** (`guard_doc_fragments`)
3. **Embeddings** (`guard_doc_embeddings`)

All three are enforced in `ops.tagproof` STRICT lane.

