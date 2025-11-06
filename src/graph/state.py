"""
Pipeline State Definitions

TypedDict classes for LangGraph pipeline state management.
"""

from typing import Any, Dict, List, TypedDict


class PipelineState(TypedDict):
    """Main pipeline state for LangGraph orchestration."""

    # Run metadata
    run_id: str
    book_name: str
    book: str  # DEPRECATED: for backwards compatibility

    # Execution mode
    mode: str

    # Data progression
    nouns: List[Dict[str, Any]]
    enriched_nouns: List[Dict[str, Any]]
    analyzed_nouns: List[Dict[str, Any]]
    weighted_nouns: List[Dict[str, Any]]

    # Processing artifacts
    conflicts: List[Dict[str, Any]]
    graph: Dict[str, Any]
    metrics: Dict[str, Any]
    metadata: Dict[str, Any]

    # Agent configuration
    use_agents: bool


class Graph(TypedDict):
    """Graph structure for analysis."""

    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    metadata: Dict[str, Any] | None
