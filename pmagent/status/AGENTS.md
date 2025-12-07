# AGENTS.md - pmagent/status Directory

## Directory Purpose

The `pmagent/status/` directory contains status components for the Gematria analysis pipeline.

## Key Components

- `snapshot.py`: Unified system snapshot helpers used by `pm.snapshot` and `/api/status/system`. Now includes advisory `kb_doc_health` metrics (AgentPM-Next:M3).
- `kb_metrics.py`: KB documentation health metrics helper (AgentPM-Next:M3) that aggregates KB registry freshness + M2 fix manifests into doc-health metrics for reporting surfaces (`pmagent report kb`, `pm.snapshot`, and future status integration).
- `explain.py`: Human-readable status explanation generator (using LM or heuristics).
- `eval_exports.py`: Eval export analysis for snapshot integration (Phase-8/10).

## API Contracts

### `pmagent.status.snapshot`

```python
def get_system_snapshot(
    include_reality_check: bool = True,
    include_ai_tracking: bool = True,
    include_share_manifest: bool = True,
    include_eval_insights: bool = True,
    include_kb_registry: bool = True,
    include_kb_doc_health: bool = True,  # New in AgentPM-Next:M3
    reality_check_mode: str = "HINT",
    use_lm_for_explain: bool = False,
) -> dict[str, Any]:
    """
    Compose a comprehensive system snapshot for operator or UI consumption.
    
    Returns:
        dict: Nested snapshot object including health, explanations, tracking, manifests,
              eval insights, KB registry summary, and KB doc-health metrics.
    """
```

### `pmagent.status.kb_metrics`

```python
def compute_kb_doc_health_metrics(
    registry_path: str = "share/kb_registry.json"
) -> dict[str, Any]:
    """
    Compute documentation health metrics from the KB registry and fix manifests.
    
    Returns:
        dict: {
            "available": bool,
            "metrics": {
                "kb_fresh_ratio": { "overall": float, "by_subsystem": dict },
                "kb_missing_count": int,
                "kb_stale_count_by_subsystem": dict,
                "kb_fixes_applied_last_7d": int,
                "notes": list[str]
            },
            "error": str (optional)
        }
    """
```

## Testing Strategy

<!-- Add testing approach and coverage requirements here -->

## Development Guidelines

<!-- Add coding standards and patterns specific to this directory here -->

## Related ADRs

| Component/Function | Related ADRs |
|-------------------|--------------|
<!-- Add ADR references here -->
