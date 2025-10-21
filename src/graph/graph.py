from __future__ import annotations

import json, uuid
from typing import Any, Callable, Dict, TypedDict

from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver

from src.graph.batch_processor import BatchProcessor, BatchConfig, BatchResult, BatchAbortError
from src.infra.checkpointer import get_checkpointer
from src.infra.metrics import get_metrics_client, NodeTimer
from src.infra.structured_logger import get_logger, log_json

LOG = get_logger("gemantria.graph")


class PipelineState(TypedDict, total=False):
    book_name: str
    mode: str
    nouns: list[str]  # Raw noun strings for processing
    batch_result: BatchResult
    conflicts: list[dict[str, Any]]
    predictions: dict[str, Any]
    metadata: dict[str, Any]


def with_metrics(node_fn: Callable[[Dict[str, Any]], Dict[str, Any]], node_name: str) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    metrics = get_metrics_client()
    def _wrapped(state: Dict[str, Any]) -> Dict[str, Any]:
        run_id = state.get("run_id") or uuid.uuid4()
        thread_id = state.get("thread_id") or "default"
        state["run_id"] = run_id
        state["thread_id"] = thread_id
        nt = NodeTimer(metrics, run_id, thread_id, node_name, meta={"checkpoint_id": state.get("checkpoint_id")})
        items_in = None
        if isinstance(state.get("items"), list):
            items_in = len(state["items"])
        nt.start(items_in=items_in)
        try:
            out = node_fn(state)
            items_out = None
            if isinstance(out.get("items"), list):
                items_out = len(out["items"])
            nt.end(items_out=items_out, status="ok")
            return out
        except Exception as e:
            nt.error(e)
            raise
    return _wrapped


def collect_nouns_node(state: PipelineState) -> PipelineState:
    """Collect nouns from book for batch processing."""
    # Placeholder: in real implementation, this would extract nouns from book
    # For now, return empty list to trigger batch validation
    nouns = []  # Would be populated from actual book parsing
    return {**state, "nouns": nouns}


def validate_batch_node(state: PipelineState) -> PipelineState:
    """Process nouns through validation pipeline."""
    nouns = state.get("nouns", [])
    batch_config = BatchConfig.from_env()

    processor = BatchProcessor(batch_config)
    try:
        batch_result = processor.process_nouns(nouns)
        return {**state, "batch_result": batch_result}
    except BatchAbortError as e:
        # Handle batch abort specifically
        new_state = state.copy()
        new_state["batch_result"] = None
        new_state["error"] = str(e)
        new_state["review_file"] = str(e.review_file)
        return new_state
    except Exception as e:
        # Log error and continue with empty result
        return {**state, "batch_result": None, "error": str(e)}


def create_graph() -> StateGraph:
    """Create the LangGraph pipeline with batch processing."""
    graph = StateGraph(PipelineState)

    # Add nodes with metrics wrapping
    graph.add_node("collect_nouns", with_metrics(collect_nouns_node, "collect_nouns"))
    graph.add_node("validate_batch", with_metrics(validate_batch_node, "validate_batch"))

    # Define flow
    graph.add_edge("collect_nouns", "validate_batch")

    # Set entry point
    graph.set_entry_point("collect_nouns")

    # Add checkpointer
    checkpointer = get_checkpointer()
    graph.checkpointer = checkpointer

    return graph.compile()


def run_pipeline(book: str = "Genesis", mode: str = "START") -> PipelineState:
    """Run the complete pipeline."""
    graph = create_graph()

    initial_state = {
        "book_name": book,
        "mode": mode,
        "nouns": [],
        "conflicts": [],
        "metadata": {}
    }

    # Run the graph
    result = graph.invoke(initial_state)

    return result


# Backward compatibility
def run_hello(book: str = "Genesis", mode: str = "START") -> PipelineState:
    """Legacy function - delegates to new pipeline."""
    return run_pipeline(book, mode)


if __name__ == "__main__":
    print(json.dumps(run_hello(), ensure_ascii=False))
