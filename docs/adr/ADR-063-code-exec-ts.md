# ADR-063: TS Code-Execution Sandbox (PoC)

## Context

Introduce a Node/TS sandbox for on-demand code-exec to reduce token load without altering the existing Python/LangGraph pipeline.

## Decision

Gate behind feature flag; v2 pipeline remains default. Always-applied rules remain 050/051/052 (029 ADR coverage applies).

## Consequences

No schema/DB changes in the PoC; CI stays hermetic; guards unchanged.

## Verification

SSOT (ruff) green; ci.exports.smoke & guards.all pass; no change in exports shape.

