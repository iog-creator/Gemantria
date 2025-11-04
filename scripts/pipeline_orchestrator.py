#!/usr/bin/env python3
"""
Unified Pipeline Orchestrator

Coordinates all pipeline components: noun extraction, embeddings, book processing,
analysis, and exports into a cohesive workflow.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

# Add src to Python path
script_dir = Path(__file__).parent
project_root = script_dir.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from src.infra.env_loader import ensure_env_loaded
from src.infra.structured_logger import get_logger, log_json

# Load environment
ensure_env_loaded()

LOG = get_logger("pipeline_orchestrator")


def run_full_pipeline(book: str = "Genesis", mode: str = "START") -> Dict[str, Any]:
    """
    Run the complete integrated pipeline.

    This orchestrates:
    1. Noun extraction from Bible database
    2. Gematria calculation and enrichment
    3. Semantic network building with embeddings
    4. Schema validation
    5. Graph analysis and export
    """
    log_json(LOG, 20, "pipeline_orchestrator_start", book=book, mode=mode)

    try:
        from src.graph.graph import run_pipeline

        # Run the main pipeline
        result = run_pipeline(book=book, mode=mode)

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

    Operations: graph, export, all
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
        dsn = os.getenv("GEMATRIA_DSN")
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
    parser = argparse.ArgumentParser(description="Unified Pipeline Orchestrator")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Pipeline command
    pipeline_parser = subparsers.add_parser("pipeline", help="Run main pipeline")
    pipeline_parser.add_argument("--book", default="Genesis", help="Book to process")
    pipeline_parser.add_argument("--mode", default="START", help="Pipeline mode")

    # Book processing command
    book_parser = subparsers.add_parser("book", help="Book processing operations")
    book_parser.add_argument("operation", choices=["plan", "dry", "go", "stop", "resume"], help="Operation to perform")
    book_parser.add_argument("--config", default="config/book_plan.yaml", help="Book configuration file")
    book_parser.add_argument("--stop-n", type=int, default=5, help="Number of chapters for stop operation")

    # Analysis command
    analysis_parser = subparsers.add_parser("analysis", help="Analysis operations")
    analysis_parser.add_argument("operation", choices=["graph", "export", "all"], help="Analysis operation to perform")

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
            result = run_full_pipeline(book=args.book, mode=args.mode)

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
            # Run complete workflow: pipeline -> analysis -> exports
            log_json(LOG, 20, "full_workflow_start", book=args.book)

            # 1. Run main pipeline
            pipeline_result = run_full_pipeline(book=args.book)
            if not pipeline_result["success"]:
                result = {"success": False, "error": "Pipeline failed", "stage": "pipeline"}
            else:
                # 2. Run analysis (unless skipped)
                if not args.skip_analysis:
                    analysis_result = run_analysis("all")
                    if not analysis_result["success"]:
                        result = {"success": False, "error": "Analysis failed", "stage": "analysis"}
                    else:
                        result = {"success": True, "pipeline": pipeline_result, "analysis": analysis_result}
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
