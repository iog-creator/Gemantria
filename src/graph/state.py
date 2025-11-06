"""
Pipeline State Management

TypedDict definitions for LangGraph pipeline state management.
"""

from typing import Any, Dict, List, TypedDict


class PipelineState(TypedDict, total=False):
    """LangGraph pipeline state dictionary."""

    # Core identifiers
    run_id: str
    book_name: str
    book: str  # DEPRECATED: for backwards compatibility

    # Execution mode
    mode: str

    # Noun processing stages
    nouns: List[Dict[str, Any]]
    enriched_nouns: List[Dict[str, Any]]
    analyzed_nouns: List[Dict[str, Any]]
    weighted_nouns: List[Dict[str, Any]]

    # Analysis results
    conflicts: List[Dict[str, Any]]
    graph: Dict[str, Any]
    metrics: Dict[str, Any]
    metadata: Dict[str, Any]

    # Agent configuration
    use_agents: bool

    # Enrichment and cross-reference persistence
    crossrefs_persisted: int | None

    # Hints collection
    hints: List[str]
    enveloped_hints: Dict[str, Any]

    # Qwen health verification
    qwen_health: Dict[str, Any]

    # Validation status
    validated_nouns: List[Dict[str, Any]]
    ai_enrichments_generated: int

    # Network analysis
    network_summary: Dict[str, Any]
