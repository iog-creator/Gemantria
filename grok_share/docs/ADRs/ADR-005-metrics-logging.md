# ADR-005: Metrics & Structured Logging

## Status
Accepted

## Context
We need deterministic, resumable LangGraph pipeline observability without external dependencies. Every node must emit start/end/error events with timings and counters, tied to run/thread/checkpoint IDs for debugging and performance analysis.

## Decision
Implement structured JSON logging to stdout plus optional Postgres sink via `metrics_log` table, gated by `METRICS_ENABLED` env var. Use `NodeTimer` class for consistent event emission and fail-open design.

## Rationale
- **Zero external deps**: stdlib JSON logging only
- **Deterministic**: events tied to UUID run_ids and checkpoint_ids
- **Fail-open**: metrics failures never break pipeline execution
- **Gated**: `METRICS_ENABLED=0` disables DB writes but keeps stdout logging
- **Complete coverage**: every node wrapped with `with_metrics` for consistent observability

## Consequences
- Slight performance overhead from metrics emission (acceptable for observability)
- All nodes must be registered via `with_metrics` wrapper (CI check added)
- Adds one migration and small infra layer
- Enables dashboarding and historical analysis via Postgres queries

## Implementation
- `structured_logger.py`: JSON stdout formatter with millisecond timestamps
- `metrics.py`: Postgres sink with NodeTimer class and fail-open semantics
- `graph.py`: `with_metrics` wrapper applied to all nodes at registration
- `migrations/003_metrics_logging.sql`: schema with proper indexing
- Environment: `METRICS_ENABLED`, `LOG_LEVEL`, `WORKFLOW_ID`

## Alternatives Considered
- **External monitoring services**: Rejected due to added complexity and deps
- **Custom binary protocol**: Rejected in favor of human-readable JSON
- **Embedded metrics in checkpoints**: Rejected due to checkpoint size concerns
- **No metrics**: Rejected as insufficient for production debugging

## Testing
- Unit: logger formatter, disabled client behavior
- Integration: DB roundtrip, wrapper propagation
- E2E: metrics emission during actual pipeline runs
