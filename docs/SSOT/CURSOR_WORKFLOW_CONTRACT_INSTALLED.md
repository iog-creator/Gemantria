# Cursor Workflow Contract (SSOT)

## Purpose
Defines how Cursor must execute OPS blocks coming from PM.

## Core Workflow Rules

### 1. OPS Execution
- Execute **only** the commands in the OPS block.
- Do not infer, expand, or modify instructions unless OPS explicitly instructs you to.
- Do not generate new questions to the Orchestrator.
- Keep all changes within the boundaries defined by SSOT and RULES_INDEX.md.

### 2. Governance Compliance
- Enforce Rule-050, Rule-051, Rule-052.
- Apply hermetic test bundle rules.
- Perform ruff format + ruff check unless instructed otherwise.
- Treat DB unavailability as acceptable in hermetic mode.
- Never require the Orchestrator to provide DSNs, ports, or environment fixes.

### 3. Evidence Return
Cursor must always return:
- Code diffs (if applicable)
- File creation paths
- Lint/test results
- Git status (`git status -sb`)

### 4. No Runtime Promises
- Cursor must not defer work.
- All OPS work must be executed synchronously.

## Versioning
This document is authoritative for Cursor behavior. Updates require PR + RULES_INDEX.md update.
