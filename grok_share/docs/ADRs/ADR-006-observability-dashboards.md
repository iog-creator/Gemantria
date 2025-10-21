# ADR-006: Observability Dashboards & Queries

## Status
Accepted

## Context
We need deterministic, resumable LangGraph pipeline observability without external dependencies. Every node must emit start/end/error events with timings and counters, tied to run/thread/checkpoint IDs for debugging and performance analysis.

## Decision
Provide SQL-first dashboards via Postgres views and (optional) OpenMetrics exporter. Keep core observability dependency-free; exporter is opt-in.

## Rationale
- **SQL views are portable, debuggable, and zero-dep.**
- **OpenMetrics allows Prometheus/Grafana without touching app internals.**
- **Materialized view + refresh function support low-latency dashboards.**
- **Query helpers ease CLI/report generation without hard dependencies.**

## Consequences
- **One migration** with views + optional materialized views.
- **Optional FastAPI exporter** gated by `PROM_EXPORTER_ENABLED`.
- **Views must be used** for all UI queries (no ad-hoc heavy queries).

## Implementation
- `004_metrics_views.sql` (views + refresh fn)
- `metrics_queries.py` (optional query helpers)
- `(optional) obs/prom_exporter.py` (FastAPI exporter)
- Example Grafana dashboard JSON
- Tests for view existence & shape
