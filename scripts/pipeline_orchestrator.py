from scripts.config.env import get_rw_dsn
# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
"""
Unified Pipeline Orchestrator

Coordinates all pipeline components: noun extraction, embeddings, book processing,
analysis, and exports into a cohesive workflow.
"""

import argparse
import os
import sys
import json
from typing import Any, Dict, List

from src.infra.env_loader import ensure_env_loaded
from src.infra.structured_logger import get_logger, log_json

LOG = get_logger("pipeline_orchestrator")

# Load environment
ensure_env_loaded()


def _validate_envelope_first() -> Dict[str, Any]:
    """
    ENVELOPE-FIRST HARDENING: Validate any existing envelopes before pipeline operations.

    This implements the envelope-first principle by checking envelope integrity
    before allowing any downstream processing. Uses COMPASS mathematical validation
    and schema validation to ensure data quality gates are met.

    Returns:
        Dict with validation results:
        {
            "passed": bool,
            "errors": List[str],
            "compass_score": float (optional),
            "schema_valid": bool (optional)
        }
    """
    validation_result = {
        "passed": True,
        "errors": [],
        "envelopes_checked": [],
    }

    try:
        from pathlib import Path

        # Check for unified envelope
        envelope_path = Path("share/exports/envelope.json")
        if envelope_path.exists():
            validation_result["envelopes_checked"].append("unified_envelope")

            # Try COMPASS mathematical validation
            try:
                from scripts.compass.scorer import score_envelope

                compass_score = score_envelope(str(envelope_path))
                validation_result["compass_score"] = compass_score

                # COMPASS gate: >80% correctness threshold
                if compass_score < 0.8:
                    validation_result["passed"] = False
                    validation_result["errors"].append(
                        f"COMPASS validation failed: {compass_score:.1%} < 80% threshold"
                    )

                log_json(LOG, 20, "compass_validation_complete", score=compass_score)

            except Exception as e:
                log_json(LOG, 30, "compass_validation_failed", error=str(e))
                validation_result["passed"] = False
                validation_result["errors"].append(f"COMPASS validation error: {e}")

            # Try schema validation
            try:
                import jsonschema

                schema_path = Path("docs/SSOT/unified-envelope.schema.json")
                if schema_path.exists():
                    with open(envelope_path) as f:
                        envelope_data = json.load(f)
                    with open(schema_path) as f:
                        schema = json.load(f)

                    jsonschema.validate(envelope_data, schema)
                    validation_result["schema_valid"] = True
                    log_json(LOG, 20, "envelope_schema_validation_passed")
                else:
                    validation_result["errors"].append("Envelope schema file not found")

            except jsonschema.ValidationError as e:
                validation_result["passed"] = False
                validation_result["errors"].append(f"Envelope schema validation failed: {e.message}")
            except Exception as e:
                validation_result["passed"] = False
                validation_result["errors"].append(f"Envelope validation error: {e}")

        else:
            # No envelope exists - this is acceptable for fresh runs
            log_json(LOG, 20, "no_envelope_present", note="Acceptable for fresh pipeline runs")

        # Check for temporal analysis envelopes
        temporal_path = Path("share/exports/temporal_patterns.json")
        if temporal_path.exists():
            validation_result["envelopes_checked"].append("temporal_patterns")

            try:
                import jsonschema

                schema_path = Path("docs/SSOT/temporal-patterns.schema.json")
                if schema_path.exists():
                    with open(temporal_path) as f:
                        temporal_data = json.load(f)
                    with open(schema_path) as f:
                        schema = json.load(f)

                    jsonschema.validate(temporal_data, schema)
                    log_json(LOG, 20, "temporal_schema_validation_passed")
                else:
                    validation_result["errors"].append("Temporal schema file not found")

            except jsonschema.ValidationError as e:
                validation_result["passed"] = False
                validation_result["errors"].append(f"Temporal schema validation failed: {e.message}")
            except Exception as e:
                validation_result["passed"] = False
                validation_result["errors"].append(f"Temporal validation error: {e}")

        # Check for forecast envelope
        forecast_path = Path("share/exports/pattern_forecast.json")
        if forecast_path.exists():
            validation_result["envelopes_checked"].append("pattern_forecast")

            try:
                import jsonschema

                schema_path = Path("docs/SSOT/pattern-forecast.schema.json")
                if schema_path.exists():
                    with open(forecast_path) as f:
                        forecast_data = json.load(f)
                    with open(schema_path) as f:
                        schema = json.load(f)

                    jsonschema.validate(forecast_data, schema)
                    log_json(LOG, 20, "forecast_schema_validation_passed")
                else:
                    validation_result["errors"].append("Forecast schema file not found")

            except jsonschema.ValidationError as e:
                validation_result["passed"] = False
                validation_result["errors"].append(f"Forecast schema validation failed: {e.message}")
            except Exception as e:
                validation_result["passed"] = False
                validation_result["errors"].append(f"Forecast validation error: {e}")

        log_json(
            LOG,
            20 if validation_result["passed"] else 40,
            "envelope_first_validation_complete",
            passed=validation_result["passed"],
            envelopes_checked=validation_result["envelopes_checked"],
            error_count=len(validation_result["errors"]),
        )

    except Exception as e:
        log_json(LOG, 40, "envelope_first_validation_unexpected_error", error=str(e))
        validation_result["passed"] = False
        validation_result["errors"].append(f"Unexpected validation error: {e}")

    return validation_result


def run_full_pipeline(
    book: str = "Genesis", mode: str = "START", nouns: List[Dict[str, Any]] | None = None
) -> Dict[str, Any]:
    """
    Run the complete integrated pipeline with envelope-first hardening.

    This orchestrates:
    1. Envelope-first validation (COMPASS + schema gates)
    2. Noun extraction from Bible database (or use provided nouns)
    3. Gematria calculation and enrichment
    4. Semantic network building with embeddings
    5. Schema validation
    6. Graph analysis and export

    Args:
        book: The book name to process
        mode: Processing mode (START, RESUME, etc.)
        nouns: Optional list of nouns to use instead of AI discovery
    """
    log_json(LOG, 20, "pipeline_orchestrator_start", book=book, mode=mode, nouns_provided=nouns is not None)

    try:
        # ENVELOPE-FIRST HARDENING: Validate any existing envelopes before proceeding
        envelope_validation = _validate_envelope_first()
        if not envelope_validation["passed"]:
            log_json(LOG, 40, "envelope_validation_failed", errors=envelope_validation["errors"])
            return {
                "success": False,
                "book": book,
                "error": f"Envelope validation failed: {envelope_validation['errors']}",
                "envelope_validation": envelope_validation,
            }

        from src.graph.graph import run_pipeline

        # Run the main pipeline
        result = run_pipeline(book=book, mode=mode, nouns=nouns)

        # Extract results
        success = "error" not in result
        run_id = str(result.get("run_id", "unknown"))

        # Log completion
        log_json(LOG, 20, "pipeline_orchestrator_complete", success=success, run_id=run_id, book=book)

        return {
            "success": success,
            "run_id": run_id,
            "book": book,
            "result": result,
        }

    except Exception as e:
        log_json(LOG, 40, "pipeline_orchestrator_failed", book=book, error=str(e))
        return {
            "success": False,
            "book": book,
            "error": str(e),
        }


def run_book_processing(config_path: str, operation: str) -> Dict[str, Any]:
    """
    Run book-level processing operations.

    Operations: plan, dry, go, stop, resume
    """
    log_json(LOG, 20, "book_processing_start", config=config_path, operation=operation)

    try:
        from scripts.run_book import cmd_plan, cmd_dry, cmd_go, cmd_stop, cmd_resume

        # Create a mock args object
        class MockArgs:
            def __init__(self, **kwargs):
                for k, v in kwargs.items():
                    setattr(self, k, v)

        if operation == "plan":
            args = MockArgs(cfg=config_path)
            cmd_plan(args)
        elif operation == "dry":
            args = MockArgs(cfg=config_path)
            cmd_dry(args)
        elif operation == "go":
            args = MockArgs(cfg=config_path)
            cmd_go(args)
        elif operation == "stop":
            # Need N parameter for stop
            n = getattr(sys.modules["__main__"], "stop_n", 5)
            args = MockArgs(cfg=config_path, n=n)
            cmd_stop(args)
        elif operation == "resume":
            args = MockArgs()
            cmd_resume(args)

        log_json(LOG, 20, "book_processing_complete", operation=operation)
        return {"success": True, "operation": operation}

    except Exception as e:
        log_json(LOG, 40, "book_processing_failed", operation=operation, error=str(e))
        return {"success": False, "operation": operation, "error": str(e)}


def run_analysis(operation: str) -> Dict[str, Any]:
    """
    Run analysis operations.

    Operations: graph, export, temporal, all
    """
    log_json(LOG, 20, "analysis_start", operation=operation)

    try:
        if operation == "graph":
            from scripts.analyze_graph import main as analyze_main

            analyze_main()
        elif operation == "export":
            from scripts.export_graph import main as export_main
            from scripts.export_stats import main as stats_main

            export_main()
            stats_main()
        elif operation == "temporal":
            # Run temporal analysis via analysis_runner_node
            from src.nodes.analysis_runner import _run_temporal_analysis

            state = {"operation": "temporal", "book": "Genesis"}
            result = _run_temporal_analysis(state)
            log_json(LOG, 20, "temporal_analysis_complete", result=result)
        elif operation == "all":
            # Run both graph analysis and exports
            from scripts.analyze_graph import main as analyze_main
            from scripts.export_graph import main as export_main
            from scripts.export_stats import main as stats_main

            analyze_main()
            export_main()
            stats_main()

        log_json(LOG, 20, "analysis_complete", operation=operation)
        return {"success": True, "operation": operation}

    except Exception as e:
        log_json(LOG, 40, "analysis_failed", operation=operation, error=str(e))
        return {"success": False, "operation": operation, "error": str(e)}


def run_embeddings_backfill(model: str = "text-embedding-qwen3-embedding-0.6b", dim: int = 1024) -> Dict[str, Any]:
    """
    Run embeddings backfill for existing nouns.
    """
    log_json(LOG, 20, "embeddings_backfill_start", model=model, dim=dim)

    try:
        from scripts.backfill_noun_embeddings import backfill_noun_embeddings
        import os

        # Get DSN from environment
        dsn = get_rw_dsn()
        if not dsn:
            raise ValueError("GEMATRIA_DSN environment variable not set")

        # Get LM Studio URL
        lmstudio_url = os.getenv("LM_STUDIO_HOST", "http://127.0.0.1:1234")

        # Run backfill
        backfill_noun_embeddings(
            dsn=dsn, lmstudio_base=lmstudio_url, model_name=model, dim=dim, batch_size=512, sleep_sec=1.0
        )

        log_json(LOG, 20, "embeddings_backfill_complete", model=model, dim=dim)
        return {"success": True, "model": model, "dim": dim}

    except Exception as e:
        log_json(LOG, 40, "embeddings_backfill_failed", error=str(e))
        return {"success": False, "error": str(e)}


def main():
    """Main CLI entry point."""
    import json

    parser = argparse.ArgumentParser(description="Unified Pipeline Orchestrator")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Pipeline command
    pipeline_parser = subparsers.add_parser("pipeline", help="Run main pipeline")
    pipeline_parser.add_argument("--book", default="Genesis", help="Book to process")
    pipeline_parser.add_argument("--mode", default="START", help="Pipeline mode")
    pipeline_parser.add_argument(
        "--nouns-json",
        dest="nouns_json",
        default=None,
        help="Optional path to ai-nouns envelope; skips discovery if supplied.",
    )

    # Book processing command
    book_parser = subparsers.add_parser("book", help="Book processing operations")
    book_parser.add_argument("operation", choices=["plan", "dry", "go", "stop", "resume"], help="Operation to perform")
    book_parser.add_argument("--config", default="config/book_plan.yaml", help="Book configuration file")
    book_parser.add_argument("--stop-n", type=int, default=5, help="Number of chapters for stop operation")

    # Analysis command
    analysis_parser = subparsers.add_parser("analysis", help="Analysis operations")
    analysis_parser.add_argument(
        "operation", choices=["graph", "export", "temporal", "all"], help="Analysis operation to perform"
    )

    # Embeddings command
    embeddings_parser = subparsers.add_parser("embeddings", help="Embeddings backfill")
    embeddings_parser.add_argument(
        "--model", default="text-embedding-qwen3-embedding-0.6b", help="Embedding model name"
    )
    embeddings_parser.add_argument("--dim", type=int, default=1024, help="Embedding dimension")

    # Full workflow command
    full_parser = subparsers.add_parser("full", help="Run complete workflow")
    full_parser.add_argument("--book", default="Genesis", help="Book to process")
    full_parser.add_argument("--config", default="config/book_plan.yaml", help="Book configuration file")
    full_parser.add_argument("--skip-analysis", action="store_true", help="Skip analysis step")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        if args.command == "pipeline":
            nouns = None
            if args.nouns_json:
                if not os.path.exists(args.nouns_json):
                    raise FileNotFoundError(f"Nouns file not found: {args.nouns_json}")
                with open(args.nouns_json, encoding="utf-8") as f:
                    envelope = json.load(f)
                if "nodes" not in envelope or not isinstance(envelope["nodes"], list):
                    raise ValueError("Invalid nouns envelope: missing 'nodes' list")
                nouns = envelope["nodes"]
            result = run_full_pipeline(book=args.book, mode=args.mode, nouns=nouns)

        elif args.command == "book":
            # Store stop_n for use in run_book_processing
            if hasattr(args, "stop_n"):
                sys.modules["__main__"].stop_n = args.stop_n
            result = run_book_processing(args.config, args.operation)

        elif args.command == "analysis":
            result = run_analysis(args.operation)

        elif args.command == "embeddings":
            result = run_embeddings_backfill(model=args.model, dim=args.dim)

        elif args.command == "full":
            # Run complete workflow: pipeline -> analysis -> temporal analytics -> exports
            log_json(LOG, 20, "full_workflow_start", book=args.book)

            # Load nouns if provided
            nouns = None
            if args.nouns_json:
                if not os.path.exists(args.nouns_json):
                    raise FileNotFoundError(f"Nouns file not found: {args.nouns_json}")
                with open(args.nouns_json, encoding="utf-8") as f:
                    envelope = json.load(f)
                if "nodes" not in envelope or not isinstance(envelope["nodes"], list):
                    raise ValueError("Invalid nouns envelope: missing 'nodes' list")
                nouns = envelope["nodes"]

            # 1. Run main pipeline
            pipeline_result = run_full_pipeline(book=args.book, nouns=nouns)
            if not pipeline_result["success"]:
                result = {"success": False, "error": "Pipeline failed", "stage": "pipeline"}
            else:
                # Wrap raw exports to SSOT if raw files exist (assume run_pipeline writes raw)
                import subprocess

                book = args.book
                if os.path.exists("exports/ai_nouns.raw.json"):
                    subprocess.check_call(
                        [
                            "python3",
                            "scripts/guards/wrap_ssot.py",
                            "ai-nouns",
                            "exports/ai_nouns.raw.json",
                            "share/exports/ai_nouns.json",
                            book,
                        ]
                    )
                if os.path.exists("exports/graph_latest.raw.json"):
                    subprocess.check_call(
                        [
                            "python3",
                            "scripts/guards/wrap_ssot.py",
                            "graph",
                            "exports/graph_latest.raw.json",
                            "share/exports/graph_latest.json",
                            book,
                        ]
                    )

                # 2. Run analysis (unless skipped)
                if not args.skip_analysis:
                    analysis_result = run_analysis("all")
                    if not analysis_result["success"]:
                        result = {"success": False, "error": "Analysis failed", "stage": "analysis"}
                    else:
                        # 3. Phase-8 temporal analytics (rolling windows + forecast)
                        print("[phase8] running temporal analytics...")
                        import json

                        graph_file = "exports/graph_latest.json"
                        if os.path.exists(graph_file):
                            with open(graph_file, encoding="utf-8") as f:
                                graph_data = json.load(f)
                        else:
                            graph_data = {}
                        from scripts.temporal_analytics import analyze_temporal_patterns, generate_forecast

                        tp = analyze_temporal_patterns(graph_data)
                        fc = generate_forecast(tp)
                        print("[phase8] temporal analytics complete")
                        result = {
                            "success": True,
                            "pipeline": pipeline_result,
                            "analysis": analysis_result,
                            "temporal": {"patterns": tp, "forecast": fc},
                        }
                else:
                    result = {"success": True, "pipeline": pipeline_result}

            log_json(LOG, 20, "full_workflow_complete", success=result["success"], book=args.book)

        # Output result as JSON
        print(json.dumps(result, indent=2, default=str))

        # Exit with appropriate code
        sys.exit(0 if result.get("success", False) else 1)

    except KeyboardInterrupt:
        log_json(LOG, 30, "orchestrator_interrupted")
        print(json.dumps({"success": False, "error": "Interrupted by user"}))
        sys.exit(130)
    except Exception as e:
        log_json(LOG, 50, "orchestrator_unexpected_error", error=str(e))
        print(json.dumps({"success": False, "error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
