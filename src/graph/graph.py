from __future__ import annotations

import json, uuid
from typing import Any, Callable, Dict, TypedDict

from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver

from src.graph.batch_processor import BatchProcessor, BatchConfig, BatchResult, BatchAbortError
from src.infra.checkpointer import get_checkpointer
from src.infra.metrics import get_metrics_client, NodeTimer
from src.infra.structured_logger import get_logger, log_json
from src.nodes.enrichment import enrichment_node
from src.nodes.confidence_validator import confidence_validator_node, ConfidenceValidationError
from src.nodes.network_aggregator import network_aggregator_node, NetworkAggregationError

LOG = get_logger("gemantria.graph")


class PipelineState(TypedDict, total=False):
    book_name: str
    mode: str
    nouns: list[str]  # Raw noun strings for processing
    batch_result: BatchResult
    validated_nouns: list[dict[str, Any]]  # Nouns after batch validation
    enriched_nouns: list[dict[str, Any]]  # Nouns with AI enrichment
    confidence_validation: dict[str, Any]  # Confidence validation results
    network_summary: dict[str, Any]  # Network aggregation results
    conflicts: list[dict[str, Any]]
    predictions: dict[str, Any]
    metadata: dict[str, Any]


def with_metrics(node_fn: Callable[[Dict[str, Any]], Dict[str, Any]], node_name: str) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    metrics = get_metrics_client()
    def _wrapped(state: Dict[str, Any]) -> Dict[str, Any]:
        run_id = state.get("run_id", uuid.uuid4())
        thread_id = state.get("thread_id", "default")
        # Ensure run_id and thread_id are set in state for consistency
        state.setdefault("run_id", run_id)
        state.setdefault("thread_id", thread_id)
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
    # For testing: return some sample Hebrew nouns with their expected gematria values
    # In real implementation, this would extract nouns from actual book text
    sample_nouns = [
        {"hebrew": "אָדָם", "name": "adam", "value": 45},  # Adam
        {"hebrew": "הֶבֶל", "name": "hevel", "value": 37},  # Abel
    ]
    return {**state, "nouns": sample_nouns}


def validate_batch_node(state: PipelineState) -> PipelineState:
    """Process nouns through validation pipeline."""
    nouns = state.get("nouns", [])
    batch_config = BatchConfig.from_env()

    # Extract hebrew strings for batch processing
    hebrew_strings = [noun["hebrew"] for noun in nouns]

    processor = BatchProcessor(batch_config)
    try:
        batch_result = processor.process_nouns(hebrew_strings)
        # Pass validated nouns to enrichment stage
        validated_nouns = []
        for noun_input, result in zip(nouns, batch_result.results):
            validated_noun = {
                **noun_input,
                "noun_id": result.get("noun_id", uuid.uuid4()),
                "normalized": result.get("normalized"),
                "gematria": result.get("gematria"),
                "gematria_confidence": 1.0  # Assume perfect confidence for code-based calculations
            }
            validated_nouns.append(validated_noun)

        result_state = {**state, "batch_result": batch_result, "validated_nouns": validated_nouns}
        log_json(LOG, 20, "validate_batch_complete", validated_count=len(validated_nouns))
        return result_state
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
    """Create the LangGraph pipeline with batch processing, AI enrichment, confidence validation, and network aggregation."""
    graph = StateGraph(PipelineState)

    # Add nodes with metrics wrapping
    graph.add_node("collect_nouns", with_metrics(collect_nouns_node, "collect_nouns"))
    graph.add_node("validate_batch", with_metrics(validate_batch_node, "validate_batch"))
    graph.add_node("enrichment", with_metrics(enrichment_node, "enrichment"))
    graph.add_node("confidence_validator", with_metrics(confidence_validator_node, "confidence_validator"))
    graph.add_node("network_aggregator", with_metrics(network_aggregator_node, "network_aggregator"))

    # Define flow
    graph.add_edge("collect_nouns", "validate_batch")
    graph.add_edge("validate_batch", "enrichment")
    graph.add_edge("enrichment", "confidence_validator")
    graph.add_edge("confidence_validator", "network_aggregator")

    # Set entry point
    graph.set_entry_point("collect_nouns")

    # Add checkpointer
    checkpointer = get_checkpointer()
    graph.checkpointer = checkpointer

    return graph.compile()


def run_pipeline(book: str = "Genesis", mode: str = "START") -> PipelineState:
    """Run the complete pipeline."""
    graph = create_graph()

    # Generate a consistent run_id for the entire pipeline
    pipeline_run_id = uuid.uuid4()

    initial_state = {
        "run_id": pipeline_run_id,
        "book_name": book,
        "mode": mode,
        "nouns": [],
        "conflicts": [],
        "metadata": {}
    }

    try:
        # Run the graph
        result = graph.invoke(initial_state)
        return result
    except ConfidenceValidationError as e:
        # Handle confidence validation failure
        log_json(LOG, 40, "pipeline_aborted_confidence_validation",
                 book=book, low_confidence_nouns=e.low_confidence_nouns)
        return {
            **initial_state,
            "error": str(e),
            "confidence_validation_failed": True,
            "low_confidence_nouns": e.low_confidence_nouns
        }
    except NetworkAggregationError as e:
        # Handle network aggregation failure
        log_json(LOG, 40, "pipeline_aborted_network_aggregation",
                 book=book, error=str(e))
        return {
            **initial_state,
            "error": str(e),
            "network_aggregation_failed": True
        }
    except Exception as e:
        # Handle other pipeline errors
        log_json(LOG, 40, "pipeline_failed", book=book, error=str(e))
        return {
            **initial_state,
            "error": str(e),
            "pipeline_failed": True
        }


# Backward compatibility
def run_hello(book: str = "Genesis", mode: str = "START") -> PipelineState:
    """Legacy function - delegates to new pipeline."""
    return run_pipeline(book, mode)


if __name__ == "__main__":
    print(json.dumps(run_hello(), ensure_ascii=False))
