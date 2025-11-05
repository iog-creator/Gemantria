from __future__ import annotations

import json
import os
import uuid
from collections.abc import Callable
from typing import Any, TypedDict

from langgraph.graph import StateGraph

from src.graph.batch_processor import (
    BatchAbortError,
    BatchConfig,
    BatchProcessor,
    BatchResult,
)
from src.infra.checkpointer import get_checkpointer
from src.infra.db import get_gematria_rw
from src.infra.env_loader import ensure_env_loaded
from src.infra.metrics_core import NodeTimer, get_metrics_client
from src.infra.structured_logger import get_logger, log_json
from src.nodes.ai_noun_discovery import discover_nouns_for_book
from src.nodes.confidence_validator import (
    ConfidenceValidationError,
    confidence_validator_node,
)
from src.nodes.enrichment import enrichment_node
from src.nodes.network_aggregator import (
    NetworkAggregationError,
    network_aggregator_node,
)
from src.nodes.schema_validator import schema_validator_node
from src.nodes.analysis_runner import analysis_runner_node
from src.services.lmstudio_client import (
    EMBEDDING_MODEL,
    RERANKER_MODEL,
    THEOLOGY_MODEL,
    QwenHealth,
    QwenUnavailableError,
    assert_qwen_live,
)
from src.services.planner_agent import plan_processing
from src.services.math_model_client import verify_gematria_calculation
from src.services.semantic_agent import extract_semantic_features
from src.services.expert_agent import analyze_theological
from src.utils.json_sanitize import parse_llm_json

# Load environment variables from .env file
ensure_env_loaded()

LOG = get_logger("gematria.graph")


# Environment precedence guard - detect conflicting env sources
def _check_env_precedence():
    """Check for environment variable conflicts between .env and .env.local."""
    import re  # noqa: E402
    from pathlib import Path  # noqa: E402

    def read_env_file(path: Path) -> dict[str, str]:
        if not path.exists():
            return {}
        data = {}
        for line in path.read_text().splitlines():
            if not line or line.strip().startswith("#"):
                continue
            m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)=(.*)$", line.strip())
            if m:
                k, v = m.group(1), m.group(2)
                # strip optional quotes
                if v and ((v[0] == v[-1]) and v[0] in ['"', "'"]):
                    v = v[1:-1]
                data[k] = v
        return data

    base_env = read_env_file(Path(".env"))
    local_env = read_env_file(Path(".env.local"))
    conflicts = [k for k in local_env if k in base_env and local_env[k] != base_env[k]]

    if conflicts:
        print(f"[ENV WARNING] .env.local overrides {len(conflicts)} vars: {', '.join(conflicts)}")
        LOG.warning(
            "env_precedence_conflict",
            conflicts=conflicts,
            message=".env.local overrides .env",
        )


_check_env_precedence()


# LM Studio verification
def _verify_lm_studio():
    """Verify LM Studio connectivity and log configuration."""
    host = os.getenv("LM_STUDIO_HOST")
    if host:
        print(f"[LM STUDIO] Using host: {host}")
        log_json(LOG, 20, "lm_studio_config", host=host)
    else:
        print("[LM STUDIO] Warning: LM_STUDIO_HOST not set")
        log_json(LOG, 30, "lm_studio_missing", message="LM_STUDIO_HOST not set")


_verify_lm_studio()


# Postgres connectivity guard
def _verify_postgres():
    """Verify Postgres connectivity on startup."""
    import psycopg  # noqa: E402

    dsn = os.getenv("GEMATRIA_DSN")
    if not dsn:
        raise SystemExit("[DB FATAL] GEMATRIA_DSN environment variable required")

    try:
        psycopg.connect(dsn, connect_timeout=5).close()
        log_json(
            LOG,
            20,
            "postgres_verified",
            dsn_masked=dsn.replace(dsn.split("@")[0], "***") if "@" in dsn else "***",
        )
    except Exception as e:
        raise SystemExit(f"[DB FATAL] Cannot connect using GEMATRIA_DSN: {e}") from e


_verify_postgres()


# Python environment guard
def _verify_python_env():
    """Verify we're running in the correct Python environment."""
    import sys  # noqa: E402

    venv_expected = ".venv" in sys.executable
    if not venv_expected:
        raise SystemExit(f"[PY ENV] Not using project venv: {sys.executable}")


_verify_python_env()


# Environment validation
GEMATRIA_DSN = os.getenv("GEMATRIA_DSN")
BIBLE_DB_DSN = os.getenv("BIBLE_DB_DSN")

if not GEMATRIA_DSN:
    LOG.warning("GEMATRIA_DSN not set. Database operations will fail. Set GEMATRIA_DSN for full functionality.")

if not BIBLE_DB_DSN:
    LOG.warning("BIBLE_DB_DSN not set. Bible data access will fail. Set BIBLE_DB_DSN for full functionality.")


def log_qwen_health(
    run_id: str,
    health: QwenHealth,
    embedding_model: str,
    reranker_model: str,
    theology_model: str | None = None,
) -> None:
    """Log Qwen health check results to database for production verification."""
    try:
        db = get_gematria_rw()
        # Convert string run_id to UUID for database
        import uuid  # noqa: E402

        uuid_run_id = uuid.UUID(run_id)
        # Execute the insert and consume the generator to ensure it runs
        list(
            db.execute(
                """
            INSERT INTO qwen_health_log (
                run_id, embedding_model, reranker_model, embed_dim,
                lat_ms_embed, lat_ms_rerank, verified, reason
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
                (
                    uuid_run_id,
                    embedding_model,
                    reranker_model,
                    health.embed_dim,
                    health.lat_ms_embed,
                    health.lat_ms_rerank,
                    health.ok,
                    health.reason,
                ),
            )
        )
        log_json(
            LOG,
            20,
            "qwen_health_logged",
            run_id=str(run_id),
            verified=health.ok,
            reason=health.reason,
            models_checked=(
                [embedding_model, reranker_model, theology_model]
                if theology_model
                else [embedding_model, reranker_model]
            ),
        )
    except Exception as e:
        # Log failure but don't fail pipeline - health checks are for evidence, not blocking
        log_json(LOG, 30, "qwen_health_log_failed", run_id=str(run_id), error=str(e))


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
    hints: list[str]  # Runtime hints emitted during pipeline execution
    enveloped_hints: dict[str, Any]  # Hints wrapped in envelope structure for persistence


def with_metrics(
    node_fn: Callable[[dict[str, Any]], dict[str, Any]], node_name: str
) -> Callable[[dict[str, Any]], dict[str, Any]]:
    metrics = get_metrics_client()

    def _wrapped(state: dict[str, Any]) -> dict[str, Any]:
        run_id = state.get("run_id", uuid.uuid4())
        thread_id = state.get("thread_id", "default")
        # Ensure run_id and thread_id are set in state for consistency
        state.setdefault("run_id", run_id)
        state.setdefault("thread_id", thread_id)
        nt = NodeTimer(
            metrics,
            run_id,
            thread_id,
            node_name,
            meta={"checkpoint_id": state.get("checkpoint_id")},
        )
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
    """AI-driven organic noun discovery from Hebrew text."""
    book = state.get("book_name", "Genesis")
    nouns = discover_nouns_for_book(book)
    return {**state, "nouns": nouns}


def validate_batch_node(state: PipelineState) -> PipelineState:
    """Process nouns through validation pipeline."""
    nouns = state.get("nouns", [])

    # For AI-discovered nouns, skip strict batch size validation
    # Allow organic discovery without artificial limits
    is_ai_discovered = any(noun.get("ai_discovered", False) for noun in nouns)

    if is_ai_discovered:
        # AI-driven discovery: validate but don't enforce batch size limits
        log_json(LOG, 20, "ai_nouns_validation_start", noun_count=len(nouns))
        batch_config = BatchConfig.from_env()
        # Temporarily allow partial batches for AI discovery
        batch_config.allow_partial = True
        batch_config.partial_reason = "AI organic noun discovery"
    else:
        # Legacy database-driven: enforce batch size rules
        batch_config = BatchConfig.from_env()

    # Extract hebrew strings for batch processing
    hebrew_strings = [noun["hebrew"] for noun in nouns]

    processor = BatchProcessor(batch_config)
    try:
        batch_result = processor.process_nouns(hebrew_strings)
        # Pass validated nouns to enrichment stage
        validated_nouns = []
        for noun_input, result in zip(nouns, batch_result.results, strict=False):
            validated_noun = {
                **noun_input,
                "noun_id": result.get("noun_id", uuid.uuid4()),
                "normalized": result.get("normalized"),
                "gematria": result.get("gematria"),
                "gematria_confidence": 1.0,  # Assume perfect confidence for code-based calculations
            }
            validated_nouns.append(validated_noun)

        result_state = {
            **state,
            "batch_result": batch_result,
            "validated_nouns": validated_nouns,
        }
        log_json(LOG, 20, "validate_batch_complete",
                validated_count=len(validated_nouns), ai_discovered=is_ai_discovered)
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


def planner_node(state: PipelineState) -> PipelineState:
    """Plan processing sequence for nouns."""
    nouns = state.get("validated_nouns", [])
    if not nouns:
        return {**state, "planned_nouns": []}
    plans = []
    for noun in nouns:
        try:
            plan_result = plan_processing(noun)
            plan_text = plan_result.get("text", "")
            plan_data = parse_llm_json(plan_text) if plan_text else {}
            plans.append({**noun, "plan": plan_data})
        except Exception as e:
            log_json(LOG, 30, "planner_error", noun_id=noun.get("noun_id"), error=str(e))
            plans.append({**noun, "plan": {"needs_math": False, "needs_semantic": False, "needs_expert": False}})
    return {**state, "planned_nouns": plans}


def math_agent_node(state: PipelineState) -> PipelineState:
    """Verify gematria calculations using math model."""
    nouns = state.get("planned_nouns", [])
    if not nouns:
        return {**state, "math_verified_nouns": []}
    verified = []
    for noun in nouns:
        plan = noun.get("plan", {})
        if plan.get("needs_math", False):
            try:
                result = verify_gematria_calculation(noun, noun.get("gematria", 0))
                verified.append({**noun, "math_verification": result})
            except Exception as e:
                log_json(LOG, 30, "math_agent_error", noun_id=noun.get("noun_id"), error=str(e))
                verified.append(noun)
        else:
            verified.append(noun)
    return {**state, "math_verified_nouns": verified}


def semantic_agent_node(state: PipelineState) -> PipelineState:
    """Extract semantic features."""
    nouns = state.get("math_verified_nouns", [])
    if not nouns:
        return {**state, "semantic_nouns": []}
    semantic = []
    for noun in nouns:
        plan = noun.get("plan", {})
        if plan.get("needs_semantic", False):
            try:
                features = extract_semantic_features(noun)
                semantic.append({**noun, "semantic_features": features})
            except Exception as e:
                log_json(LOG, 30, "semantic_agent_error", noun_id=noun.get("noun_id"), error=str(e))
                semantic.append(noun)
        else:
            semantic.append(noun)
    return {**state, "semantic_nouns": semantic}


def expert_agent_node(state: PipelineState) -> PipelineState:
    """Apply expert theological analysis."""
    nouns = state.get("semantic_nouns", [])
    if not nouns:
        return {**state, "enriched_nouns": []}
    expert = []
    for noun in nouns:
        plan = noun.get("plan", {})
        if plan.get("needs_expert", False):
            try:
                analysis = analyze_theological(noun)
                expert.append({**noun, "expert_analysis": analysis})
            except Exception as e:
                log_json(LOG, 30, "expert_agent_error", noun_id=noun.get("noun_id"), error=str(e))
                expert.append(noun)
        else:
            expert.append(noun)
    return {**state, "enriched_nouns": expert}


def wrap_hints_node(state: PipelineState) -> PipelineState:
    """
    Wrap hints emitted during pipeline execution into envelope structure for persistence.

    Collects hints from state.hints (if present) and wraps them in a structured envelope
    that can be persisted in exports and validated by rules_guard.py.
    """
    hints = state.get("hints", [])

    # Create envelope structure for hints
    envelope = {
        "type": "hints_envelope",
        "version": "1.0",
        "items": hints,
        "count": len(hints),
    }

    # Also collect hints from metadata if they were stored there
    metadata_hints = state.get("metadata", {}).get("hints", [])
    if metadata_hints and isinstance(metadata_hints, list):
        all_hints = list(hints) + [h for h in metadata_hints if h not in hints]
        envelope["items"] = all_hints
        envelope["count"] = len(all_hints)

    log_json(LOG, 20, "hints_enveloped", hint_count=envelope["count"])

    return {**state, "enveloped_hints": envelope}


def create_graph() -> StateGraph:
    """Create the LangGraph pipeline with batch processing, AI enrichment, confidence validation, and network aggregation."""  # noqa: E501
    graph = StateGraph(PipelineState)

    # Add nodes with metrics wrapping
    graph.add_node("collect_nouns", with_metrics(collect_nouns_node, "collect_nouns"))
    graph.add_node("validate_batch", with_metrics(validate_batch_node, "validate_batch"))
    graph.add_node("enrichment", with_metrics(enrichment_node, "enrichment"))
    graph.add_node(
        "confidence_validator",
        with_metrics(confidence_validator_node, "confidence_validator"),
    )
    graph.add_node(
        "network_aggregator",
        with_metrics(network_aggregator_node, "network_aggregator"),
    )
    graph.add_node(
        "schema_validator",
        with_metrics(schema_validator_node, "schema_validator"),
    )
    graph.add_node(
        "analysis_runner",
        with_metrics(analysis_runner_node, "analysis_runner"),
    )
    graph.add_node("wrap_hints", with_metrics(wrap_hints_node, "wrap_hints"))
    # Agent nodes (optional - can be enabled via USE_AGENTS env var)
    graph.add_node("planner", with_metrics(planner_node, "planner"))
    graph.add_node("math_agent", with_metrics(math_agent_node, "math_agent"))
    graph.add_node("semantic_agent", with_metrics(semantic_agent_node, "semantic_agent"))
    graph.add_node("expert_agent", with_metrics(expert_agent_node, "expert_agent"))

    # Define flow
    graph.add_edge("collect_nouns", "validate_batch")
    # Conditional: use agents if USE_AGENTS=true, otherwise use existing enrichment
    use_agents = os.getenv("USE_AGENTS", "false").lower() == "true"
    if use_agents:
        graph.add_edge("validate_batch", "planner")
        graph.add_edge("planner", "math_agent")
        graph.add_edge("math_agent", "semantic_agent")
        graph.add_edge("semantic_agent", "expert_agent")
        graph.add_edge("expert_agent", "confidence_validator")
    else:
        graph.add_edge("validate_batch", "enrichment")
        graph.add_edge("enrichment", "confidence_validator")
    graph.add_edge("confidence_validator", "network_aggregator")
    graph.add_edge("network_aggregator", "schema_validator")
    graph.add_edge("schema_validator", "analysis_runner")
    graph.add_edge("analysis_runner", "wrap_hints")

    # Set entry point
    graph.set_entry_point("collect_nouns")

    # Add checkpointer
    checkpointer = get_checkpointer()
    graph.checkpointer = checkpointer

    return graph.compile()


def debug_connectivity() -> dict:
    """
    Test all external connections and report detailed diagnostics.
    Returns dict with connection status for troubleshooting.
    """
    results = {
        "lm_studio": {"status": "unknown", "details": {}},
        "gematria_db": {"status": "unknown", "details": {}},
        "bible_db": {"status": "unknown", "details": {}},
    }

    # Test LM Studio
    try:
        from src.services.lmstudio_client import (  # noqa: E402
            HOST,
            EMBEDDING_MODEL,
            RERANKER_MODEL,
            THEOLOGY_MODEL,
            assert_qwen_live,
        )

        results["lm_studio"]["details"]["host"] = HOST

        health = assert_qwen_live([EMBEDDING_MODEL, RERANKER_MODEL, THEOLOGY_MODEL])
        results["lm_studio"]["status"] = "ok" if health.ok else "error"
        results["lm_studio"]["details"].update(
            {
                "verified": health.ok,
                "reason": health.reason,
                "embed_dim": health.embed_dim,
                "lat_ms_embed": health.lat_ms_embed,
                "lat_ms_rerank": health.lat_ms_rerank,
            }
        )
    except Exception as e:
        results["lm_studio"]["status"] = "error"
        results["lm_studio"]["details"]["error"] = str(e)

    # Test Gematria DB
    try:
        from src.infra.db import get_gematria_rw  # noqa: E402

        db = get_gematria_rw()
        if db.dsn:
            # Try a simple query
            results["gematria_db"]["status"] = "ok"
            results["gematria_db"]["details"]["dsn_configured"] = True
            try:
                list(db.execute("SELECT 1"))
                results["gematria_db"]["details"]["connection_test"] = "success"
            except Exception as e:
                results["gematria_db"]["details"]["connection_test"] = f"failed: {e}"
        else:
            results["gematria_db"]["status"] = "error"
            results["gematria_db"]["details"]["error"] = "GEMATRIA_DSN not set"
    except Exception as e:
        results["gematria_db"]["status"] = "error"
        results["gematria_db"]["details"]["error"] = str(e)

    # Test Bible DB
    try:
        from src.infra.db import get_bible_ro  # noqa: E402

        db = get_bible_ro()
        if db.dsn:
            results["bible_db"]["status"] = "ok"
            results["bible_db"]["details"]["dsn_configured"] = True
            try:
                list(db.execute("SELECT 1"))
                results["bible_db"]["details"]["connection_test"] = "success"
            except Exception as e:
                results["bible_db"]["details"]["connection_test"] = f"failed: {e}"
        else:
            results["bible_db"]["status"] = "error"
            results["bible_db"]["details"]["error"] = "BIBLE_DB_DSN not set"
    except Exception as e:
        results["bible_db"]["status"] = "error"
        results["bible_db"]["details"]["error"] = str(e)

    return results


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
        "metadata": {},
    }

    try:
        # Qwen Live Gate: Assert ALL required models are available before any work
        required_models = [EMBEDDING_MODEL, RERANKER_MODEL, THEOLOGY_MODEL]
        qwen_health = assert_qwen_live(required_models)
        log_json(
            LOG,
            20,
            "qwen_health_check",
            verified=qwen_health.ok,
            reason=qwen_health.reason,
            embed_dim=qwen_health.embed_dim,
            lat_ms_embed=qwen_health.lat_ms_embed,
            lat_ms_rerank=qwen_health.lat_ms_rerank,
        )

        # Log health check to database for production verification
        log_qwen_health(
            str(pipeline_run_id),
            qwen_health,
            EMBEDDING_MODEL,
            RERANKER_MODEL,
            THEOLOGY_MODEL,
        )

        # Store health check results in metadata for reporting
        initial_state["metadata"]["qwen_health"] = {
            "verified": qwen_health.ok,
            "reason": qwen_health.reason,
            "embed_dim": qwen_health.embed_dim,
            "lat_ms_embed": qwen_health.lat_ms_embed,
            "lat_ms_rerank": qwen_health.lat_ms_rerank,
        }

        # Hard fail if Qwen models are not live
        if not qwen_health.ok:
            raise QwenUnavailableError(f"Qwen health check failed: {qwen_health.reason}")

        # Run the graph
        result = graph.invoke(initial_state)
        # Convert UUID run_id to string for JSON serialization
        if "run_id" in result and isinstance(result["run_id"], uuid.UUID):
            result["run_id"] = str(result["run_id"])
        # Convert BatchResult to dict for JSON serialization
        if (
            "batch_result" in result
            and result["batch_result"] is not None
            and hasattr(result["batch_result"], "to_dict")
        ):
            result["batch_result"] = result["batch_result"].to_dict()
        return result
    except ConfidenceValidationError as e:
        # Handle confidence validation failure
        log_json(
            LOG,
            40,
            "pipeline_aborted_confidence_validation",
            book=book,
            low_confidence_nouns=e.low_confidence_nouns,
        )
        return {
            **initial_state,
            "error": str(e),
            "confidence_validation_failed": True,
            "low_confidence_nouns": e.low_confidence_nouns,
        }
    except NetworkAggregationError as e:
        # Handle network aggregation failure
        log_json(LOG, 40, "pipeline_aborted_network_aggregation", book=book, error=str(e))
        return {**initial_state, "error": str(e), "network_aggregation_failed": True}
    except QwenUnavailableError as e:
        # Handle Qwen unavailability - fail-closed for production
        log_json(LOG, 40, "pipeline_aborted_qwen_unavailable", book=book, error=str(e))
        return {**initial_state, "error": str(e), "qwen_unavailable": True}
    except Exception as e:
        # Handle other pipeline errors
        log_json(LOG, 40, "pipeline_failed", book=book, error=str(e))
        return {**initial_state, "error": str(e), "pipeline_failed": True}


# Backward compatibility
def run_hello(book: str = "Genesis", mode: str = "START") -> PipelineState:
    """Legacy function - delegates to new pipeline."""
    return run_pipeline(book, mode)


if __name__ == "__main__":
    import sys  # noqa: E402

    if len(sys.argv) > 1 and sys.argv[1] == "--debug-connectivity":
        print("🔍 Connectivity Debug Report")
        print("=" * 40)
        results = debug_connectivity()
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        # Minimal CLI parsing to accept --book without changing public API
        book = "Genesis"
        if "--book" in sys.argv:
            try:
                i = sys.argv.index("--book")
                book = sys.argv[i + 1]
            except Exception:
                pass
        result = run_pipeline(book=book)

        # Convert any UUID objects to strings for JSON serialization
        def convert_uuids(obj):
            if isinstance(obj, uuid.UUID):
                return str(obj)
            elif isinstance(obj, dict):
                return {k: convert_uuids(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_uuids(item) for item in obj]
            elif hasattr(obj, "to_dict"):
                return obj.to_dict()
            else:
                return obj

        print(json.dumps(convert_uuids(result), ensure_ascii=False))
