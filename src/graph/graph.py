"""
LangGraph pipeline orchestration and execution engine.
Coordinates AI-driven noun discovery, enrichment, and network building.

Related Rules: Rule-039 (Execution Contract), Rule-050 (OPS Contract), Rule-058 (Auto-Housekeeping)
Related ADRs: ADR-032 (Organic AI Discovery), ADR-019 (Data Contracts)
"""

from __future__ import annotations

from typing import Any, TypedDict, Dict, List
from datetime import datetime, UTC
import json
import os
import pathlib
import time

from langgraph.graph import StateGraph

from src.infra.env_loader import ensure_env_loaded
from src.graph.state import PipelineState
from src.graph.batch_processor import BatchProcessor, BatchAbortError
from src.nodes import network_aggregator
from src.nodes.enrichment import enrichment_node
from src.nodes.ai_noun_discovery import discover_nouns_for_book
from src.nodes.graph_scorer import graph_scorer_node
from src.nodes.math_verifier import math_verifier_node
from src.services.expert_agent import analyze_theological
from src.ssot.noun_adapter import adapt_ai_noun
from src.infra.runs_ledger import (
    create_run,
    update_run_status,
    get_model_versions,
    get_schema_version,
)
from src.persist.runs_ledger import mark_run_started, mark_run_finished

# Load environment variables from .env file
ensure_env_loaded()


class Graph(TypedDict):
    nodes: list[dict[str, Any]]
    edges: list[dict[str, Any]]


def _save_checkpoint(node_name: str, state: PipelineState, values: dict[str, Any]) -> None:
    """
    Persist a checkpoint for the current node in a checkpointer-agnostic way.
    Supports both PostgresCheckpointer (requires metadata and checkpoint_id) and MemorySaver.
    """
    try:
        from src.infra.checkpointer import get_checkpointer
    except Exception:
        return
    try:
        checkpointer = get_checkpointer()
        ts = state.get("ts", datetime.now(UTC).isoformat())
        run_id = state.get("run_id", "unknown")
        thread_id = f"pipeline-{run_id}"
        checkpoint_id = f"{node_name}-{run_id}-{int(datetime.now(UTC).timestamp())}"
        config = {"configurable": {"thread_id": thread_id, "checkpoint_id": checkpoint_id}}
        checkpoint = {"ts": ts, "values": values}
        metadata = {"ts": ts, "node": node_name}
        try:
            checkpointer.put(config, checkpoint, metadata)
        except TypeError:
            # Fallback for implementations that use 2-arg signature
            checkpointer.put(config, checkpoint)
    except Exception:
        # Never let checkpoint persistence break the pipeline
        return


def build_graph(nouns: List[Dict]) -> Dict:
    """
    Nodes must expose Hebrew + gematria for downstream UI/analytics.
    Node.id = noun_id; keep book if present on inputs.
    """
    nodes = []
    for raw in nouns:
        n = adapt_ai_noun(raw)
        nodes.append(
            {
                "id": n["noun_id"],
                "surface": n["surface"],
                "hebrew": n["hebrew_text"],
                "gematria": n["gematria_value"],
                "class": n["class"],
            }
        )
    edges = []  # existing edge derivation unchanged
    return {"schema": "gemantria/graph.v1", "nodes": nodes, "edges": edges}


def collect_nouns_node(state: PipelineState) -> PipelineState:
    """LangGraph node for noun collection and discovery."""
    # Collect nouns (AI-driven discovery, or use provided nouns)
    if "nouns" not in state:
        # Discover nouns via AI (nouns not provided)
        state["nouns"] = discover_nouns_for_book(state["book"])
        timing_samples = []
    else:
        # Nouns already provided (e.g., from file input)
        timing_samples = []

    # Normalize nouns using SSOT adapter at discovery boundary
    state["nouns"] = [adapt_ai_noun(n) for n in state["nouns"]]

    # Log metrics
    state["metrics"]["ai_call_latencies_ms"] = timing_samples

    # Auto-save checkpoint after node completion (tolerant across implementations)
    _save_checkpoint("collect_nouns", state, {"nouns": state["nouns"], "metrics": state["metrics"]})

    state["hints"].append("collect_nouns: completed")
    return state


def validate_batch_node(state: PipelineState) -> PipelineState:
    """LangGraph node for batch validation."""
    # Validate and weigh nouns (placeholder - function not implemented)
    state["weighted_nouns"] = state["nouns"]  # Pass through for now
    state["validated_nouns"] = state["weighted_nouns"]  # Set validated nouns for enrichment

    # Auto-save checkpoint after node completion
    _save_checkpoint(
        "validate_batch",
        state,
        {"weighted_nouns": state["weighted_nouns"], "validated_nouns": state["validated_nouns"]},
    )

    state["hints"].append("validate_batch: completed")
    return state


def enrichment_node_wrapper(state: PipelineState) -> PipelineState:
    """LangGraph node for noun enrichment."""
    if state.get("resume_from_enriched"):
        # Pre-enriched nouns supplied; ensure they remain normalized.
        state["enriched_nouns"] = [adapt_ai_noun(n) for n in state.get("enriched_nouns", state.get("nouns", []))]
        _save_checkpoint("enrichment", state, {"enriched_nouns": state["enriched_nouns"]})
        state["hints"].append("enrichment: skipped (pre-enriched)")
        return state

    # Enrich nouns with theological insights
    state = enrichment_node(state)

    # Normalize enriched nouns using SSOT adapter at enrichment boundary
    state["enriched_nouns"] = [adapt_ai_noun(n) for n in state.get("enriched_nouns", [])]

    # Auto-save checkpoint after node completion
    _save_checkpoint("enrichment", state, {"enriched_nouns": state["enriched_nouns"]})

    state["hints"].append("enrichment: completed")
    return state


def math_verifier_node_wrapper(state: PipelineState) -> PipelineState:
    """LangGraph node for math verification (gematria sanity checks via MATH_MODEL)."""
    # Verify gematria calculations using MATH_MODEL
    state = math_verifier_node(state)

    # Auto-save checkpoint after node completion
    _save_checkpoint("math_verifier", state, {"enriched_nouns": state["enriched_nouns"]})

    state["hints"].append("math_verifier: completed")
    return state


def confidence_validator_node(state: PipelineState) -> PipelineState:
    """LangGraph node for confidence validation and expert analysis."""
    # Expert agent analysis
    if state.get("use_agents"):
        enriched_nouns = state.get("enriched_nouns", [])
        analyzed_nouns_results = []
        for noun in enriched_nouns:
            analyzed_noun = analyze_theological(noun)
            analyzed_nouns_results.append(analyzed_noun)
        state["analyzed_nouns"] = analyzed_nouns_results
    else:
        # If agents are not used, pass enriched nouns directly
        state["analyzed_nouns"] = state.get("enriched_nouns", [])

    # Auto-save checkpoint after node completion
    _save_checkpoint("confidence_validator", state, {"analyzed_nouns": state["analyzed_nouns"]})

    state["hints"].append("confidence_validator: completed")
    return state


def network_aggregator_node_wrapper(state: PipelineState) -> PipelineState:
    """LangGraph node for network aggregation."""
    # Network aggregation (graph.build)
    # Use the network_aggregator_node to build the network
    state = network_aggregator.network_aggregator_node(state)
    if not state.get("graph"):
        state["graph"] = {"schema": "gemantria/graph.v1", "nodes": [], "edges": []}

    # Auto-save checkpoint after node completion
    _save_checkpoint("network_aggregator", state, {"graph": state["graph"]})

    state["hints"].append("network_aggregator: completed")
    return state


def analysis_runner_node(state: PipelineState) -> PipelineState:
    """LangGraph node for graph scoring and analysis."""
    # Graph scoring (graph.score)
    # Apply SSOT blend thresholds and classify edges
    state = graph_scorer_node(state)
    state["scored_graph"] = state.get("graph", {})

    # Auto-save checkpoint after node completion
    _save_checkpoint("analysis_runner", state, {"scored_graph": state["scored_graph"]})

    state["hints"].append("analysis_runner: completed")
    return state


def wrap_hints_node_wrapper(state: PipelineState) -> PipelineState:
    """LangGraph node for wrapping hints into envelope."""
    # Wrap hints into envelope for persistence
    state = wrap_hints_node(state)
    state["hints"].append("wrap_hints: completed")
    return state


def main(state: PipelineState) -> PipelineState:
    """Legacy main function - now delegates to LangGraph nodes."""
    # This function is kept for backwards compatibility but now uses the LangGraph
    # For now, just run all nodes sequentially (will be replaced by LangGraph orchestration)
    state = collect_nouns_node(state)
    state = validate_batch_node(state)
    state = enrichment_node_wrapper(state)
    state = confidence_validator_node(state)
    state = network_aggregator_node_wrapper(state)
    state = analysis_runner_node(state)
    state = wrap_hints_node_wrapper(state)
    return state


def run_pipeline(
    book: str = "Genesis",
    mode: str = "START",
    nouns: List[Dict[str, Any]] | None = None,
    stop_after_n_nodes: int | None = None,
) -> Dict[str, Any]:
    """
    Run the complete pipeline for a given book.

    Emits LOUD HINTS for Rule-039 (Execution Contract), Rule-050/051 (OPS Contract/Cursor Insight),
    Rule-052 (Tool Priority), Rule-053 (Idempotent Baseline), Rule-026 (System Enforcement Bridge).

    Args:
        book: The book name to process
        mode: Processing mode (START, RESUME, etc.)
        nouns: Optional list of nouns to use instead of AI discovery
        stop_after_n_nodes: Optional - stop execution after N nodes (for temporal testing)

    Returns:
        Dictionary with pipeline results and metadata

    Related Rules: Rule-039, Rule-050, Rule-051, Rule-052, Rule-053, Rule-026
    Related Agents: AGENTS.md Pipeline Execution, src/graph/AGENTS.md Pipeline State Management
    """
    # 🔥🔥🔥 LOUD HINT: Rule-039 (Cursor Execution Contract) - Drive, Don't Ask 🔥🔥🔥
    # 🔥🔥🔥 LOUD HINT: Rule-050 (OPS Contract v6.2.3) - Evidence-First Protocol 🔥🔥🔥
    # 🔥🔥🔥 LOUD HINT: Rule-051 (Cursor Insight & Handoff) - Baseline Evidence Required 🔥🔥🔥
    # 🔥🔥🔥 LOUD HINT: Rule-052 (Tool Priority & Context Guidance) - Local+GH → Codex → Gemini/MCP 🔥🔥🔥
    # 🔥🔥🔥 LOUD HINT: Rule-053 (Idempotent Baseline) - Cache Baseline Evidence 60m 🔥🔥🔥
    # 🔥🔥🔥 LOUD HINT: Rule-026 (System Enforcement Bridge) - Hints Envelope Required 🔥🔥🔥
    # 🔥🔥🔥 LOUD HINT: AGENTS.md Pipeline Execution - LangGraph orchestration with Qwen health gate 🔥🔥🔥
    # 🔥🔥🔥 LOUD HINT: src/graph/AGENTS.md - Pipeline state management and batch processing 🔥🔥🔥

    import subprocess

    hint_script = os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "hint.sh")

    def emit_loud_hint(msg: str):
        if os.path.exists(hint_script):
            subprocess.run([hint_script, msg], check=False)
        else:
            print(f"🔥🔥🔥 LOUD HINT: {msg} 🔥🔥🔥")
            print(f"HINT: {msg}")

    emit_loud_hint("pipeline: starting execution for book=" + book + " mode=" + mode + " (Rule-039 Execution Contract)")
    emit_loud_hint("pipeline: loading environment and creating run (Rule-050 OPS Contract Evidence-First)")
    emit_loud_hint("pipeline: nouns provided=" + str(nouns is not None) + " (src/graph/AGENTS.md Batch Processing)")

    # Create run in ledger
    versions = {
        "schema_version": get_schema_version(),
        "models": get_model_versions(),
    }
    run_id = create_run(book, versions)

    # Optional: record run start (tolerant if DSN missing)
    try:
        mark_run_started(run_id, book, notes="langgraph pipeline")
    except Exception as e:
        print(f"[runs_ledger.start] WARN: {e}")

    provided_adapted: list[Dict[str, Any]] = []
    resume_from_enriched = False

    # Discover nouns if not provided
    if nouns is None:
        discovered_nouns = discover_nouns_for_book(book)
        nouns_to_process = discovered_nouns
    else:
        provided_adapted = [adapt_ai_noun(n) for n in nouns]

        def _has_enrichment(noun: Dict[str, Any]) -> bool:
            analysis = noun.get("analysis")
            if isinstance(analysis, dict):
                if analysis.get("theology") or analysis.get("math_check"):
                    return True
            return bool(noun.get("insights") or noun.get("analysis"))

        unenriched_nouns = [
            adapted for raw, adapted in zip(nouns, provided_adapted, strict=False) if not _has_enrichment(raw)
        ]
        if len(unenriched_nouns) < len(provided_adapted):
            emit_loud_hint(f"pipeline: resuming enrichment for {len(unenriched_nouns)} of {len(nouns)} nouns")
        nouns_to_process = unenriched_nouns
        resume_from_enriched = len(unenriched_nouns) == 0 and len(provided_adapted) > 0

    # Validate batch size only if there are nouns to process
    batch_processor = BatchProcessor()
    batch_result = None
    if nouns_to_process:
        try:
            batch_processor.validate_batch_size(nouns_to_process)
            batch_result = batch_processor.process_nouns(nouns_to_process)
        except BatchAbortError as e:
            # Batch validation failed - return error result
            update_run_status(run_id, "failed")
            try:
                mark_run_finished(run_id, notes=f"batch_abort: {e}")
            except Exception as finish_e:
                print(f"[runs_ledger.finish] WARN: {finish_e}")
            return {
                "run_id": run_id,
                "book": book,
                "mode": mode,
                "success": False,
                "error": str(e),
                "batch_result": None,  # Test expects this
            }

    # Create initial state
    from datetime import datetime

    initial_state: PipelineState = {
        "run_id": run_id,
        "book_name": book,
        "book": book,  # DEPRECATED: for backwards compatibility
        "mode": mode,
        "ts": datetime.now(UTC).isoformat(),
        "nouns": nouns_to_process,
        "enriched_nouns": [],
        "analyzed_nouns": [],
        "weighted_nouns": [],
        "conflicts": [],
        "graph": {},
        "metrics": {},
        "metadata": {},
        "use_agents": True,  # Enable agentic processing by default
        "hints": [f"pipeline_start: {book} ({mode})"],  # Runtime hints collection
        "enveloped_hints": {},  # Wrapped hints envelope
    }

    if provided_adapted:
        initial_state["nouns"] = provided_adapted

    if resume_from_enriched:
        initial_state["resume_from_enriched"] = True
        initial_state["enriched_nouns"] = provided_adapted
        initial_state["validated_nouns"] = provided_adapted
        initial_state["weighted_nouns"] = provided_adapted
        initial_state["analyzed_nouns"] = provided_adapted

    try:
        # Run the LangGraph pipeline with checkpointer
        # Create thread ID for this run
        thread_id = f"pipeline-{run_id}"

        graph = get_graph(stop_after_n_nodes=stop_after_n_nodes)

        # Configure for resumable execution
        config = {"configurable": {"thread_id": thread_id, "checkpoint_id": f"run-{run_id}-start"}}

        # Run the pipeline with checkpointer
        emit_loud_hint("pipeline: executing LangGraph with checkpointer (Rule-039)")
        final_state = graph.invoke(initial_state, config=config)

        if os.getenv("NETWORK_AGGREGATOR_MODE", "").lower() == "fallback" or os.getenv("EXPORT_GRAPH_ALWAYS") == "1":
            _persist_graph_exports(final_state.get("graph") or {}, book)

        # Update run status to completed
        from datetime import datetime

        update_run_status(run_id, "completed", finished_at=datetime.utcnow())

        # Finish marker (always tolerant)
        try:
            mark_run_finished(run_id, notes="ok")
        except Exception as e:
            print(f"[runs_ledger.finish] WARN: {e}")

        if "enveloped_hints" not in final_state:
            final_state = wrap_hints_node(final_state)

        # Return results
        return {
            "run_id": final_state.get("run_id"),
            "book": book,
            "mode": mode,
            "success": True,
            "nouns_count": len(final_state.get("nouns", [])),
            "graph_nodes": len(final_state.get("graph", {}).get("nodes", [])),
            "graph_edges": len(final_state.get("graph", {}).get("edges", [])),
            "metrics": final_state.get("metrics", {}),
            "hints": final_state.get("hints", []),  # Include collected hints
            "enveloped_hints": final_state.get("enveloped_hints", {}),  # Include hints envelope
            "batch_result": batch_result,  # Test expects this
        }

    except Exception as e:
        # Update run status to failed
        update_run_status(run_id, "failed")
        # Optional: mark run finished with error (tolerant)
        try:
            mark_run_finished(run_id, notes=f"error: {str(e)[:100]}")
        except Exception as finish_e:
            print(f"[runs_ledger.finish] WARN: {finish_e}")
        # Wrap any collected hints even on error
        initial_state = wrap_hints_node(initial_state)

        return {
            "run_id": initial_state.get("run_id"),
            "book": book,
            "mode": mode,
            "success": False,
            "error": str(e),
            "hints": initial_state.get("hints", []),  # Include hints even on error
            "enveloped_hints": initial_state.get("enveloped_hints", {}),  # Include envelope even on error
            "batch_result": batch_result,  # Include batch_result even on error
        }


def _persist_graph_exports(graph: dict[str, Any], book: str) -> None:
    """
    Persist fallback graph outputs directly to exports/ for analytics fast-lane.
    Safe no-op when the graph is empty.
    """

    nodes = graph.get("nodes") or []
    edges = graph.get("edges") or []

    export_dir = pathlib.Path("exports")
    export_dir.mkdir(exist_ok=True)

    export_timestamp = datetime.now(UTC).isoformat()

    payload = {
        "schema": "gematria/graph.v1",
        "book": book,
        "generated_at": export_timestamp,
        "nodes": nodes,
        "edges": edges,
        "metadata": {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "export_timestamp": export_timestamp,
            "source": "fallback_fast_lane",
        },
    }
    (export_dir / "graph_latest.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")

    node_count = len(nodes)
    edge_count = len(edges)
    density = 0.0
    if node_count > 1:
        density = round((2.0 * edge_count) / (node_count * (node_count - 1)), 6)

    stats = {
        "book": book,
        "nodes": node_count,
        "edges": edge_count,
        "density": density,
        "generated_at": datetime.now(UTC).isoformat(),
    }
    (export_dir / "graph_stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2) + "\n")


def wrap_hints_node(state: PipelineState) -> PipelineState:
    """
    Wrap collected hints into envelope structure for persistence.

    Implements Rule-026 (System Enforcement Bridge) - Hints Envelope Required.
    Used by AGENTS.md Pipeline Execution and src/graph/AGENTS.md Pipeline State Management.

    Args:
        state: Pipeline state containing hints

    Returns:
        Updated state with enveloped_hints populated

    Related Rules: Rule-026 (System Enforcement Bridge)
    Related Agents: AGENTS.md Pipeline Execution, src/graph/AGENTS.md Pipeline State Management
    """
    hints = state.get("hints", [])
    if hints:
        state["enveloped_hints"] = {
            "type": "hints_envelope",
            "version": "1.0",
            "items": hints,
            "count": len(hints),
        }
    else:
        # Empty envelope for consistency
        state["enveloped_hints"] = {
            "type": "hints_envelope",
            "version": "1.0",
            "items": [],
            "count": 0,
        }

    return state


def get_graph(stop_after_n_nodes: int | None = None) -> StateGraph:
    """
    Create LangGraph workflow with optional stopping capability for temporal testing.

    Args:
        stop_after_n_nodes: If set, stop execution after this many nodes (for testing resume)
    """
    workflow = StateGraph(PipelineState)

    # Add individual pipeline nodes
    workflow.add_node("collect_nouns", collect_nouns_node)
    workflow.add_node("validate_batch", validate_batch_node)
    workflow.add_node("enrichment", enrichment_node_wrapper)
    workflow.add_node("math_verifier", math_verifier_node_wrapper)
    workflow.add_node("confidence_validator", confidence_validator_node)
    workflow.add_node("network_aggregator", network_aggregator_node_wrapper)
    workflow.add_node("analysis_runner", analysis_runner_node)
    workflow.add_node("wrap_hints", wrap_hints_node_wrapper)

    # Define the pipeline flow
    workflow.set_entry_point("collect_nouns")

    # Conditionally add edges based on stop_after_n_nodes
    node_sequence = [
        "collect_nouns",
        "validate_batch",
        "enrichment",
        "math_verifier",
        "confidence_validator",
        "network_aggregator",
        "analysis_runner",
        "wrap_hints",
    ]

    for i, current_node in enumerate(node_sequence[:-1]):
        next_node = node_sequence[i + 1]

        # Only add edge if we haven't reached the stop point
        if stop_after_n_nodes is None or (i + 1) < stop_after_n_nodes:
            workflow.add_edge(current_node, next_node)
        elif stop_after_n_nodes is not None and (i + 1) == stop_after_n_nodes:
            # At stop point, make current node a finish point
            workflow.set_finish_point(current_node)
            break

    # If no stop condition, set final node as finish point
    if stop_after_n_nodes is None or stop_after_n_nodes >= len(node_sequence):
        workflow.set_finish_point("wrap_hints")

    return workflow.compile()
