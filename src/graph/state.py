from typing import TypedDict, List, Dict, Any


class PipelineState(TypedDict, total=False):
    """
    Represents the state of the data processing pipeline.
    """

    run_id: str
    book_name: str
    mode: str  # e.g., START, RESUME
    nouns: List[Dict[str, Any]]
    enriched_nouns: List[Dict[str, Any]]
    analyzed_nouns: List[Dict[str, Any]]
    weighted_nouns: List[Dict[str, Any]]
    conflicts: List[Dict[str, Any]]
    graph: Dict[str, Any]
    metrics: Dict[str, Any]
    metadata: Dict[str, Any]
    book: str  # DEPRECATED
    use_agents: bool
