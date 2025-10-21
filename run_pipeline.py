#!/usr/bin/env python3
"""
Gemantria Pipeline Runner

Usage:
    python3 run_pipeline.py <book_name> [--batch-size N]

Examples:
    python3 run_pipeline.py Genesis
    python3 run_pipeline.py Genesis --batch-size 10
"""

import argparse
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.graph.graph import run_pipeline

def main():
    parser = argparse.ArgumentParser(description="Run Gemantria pipeline")
    parser.add_argument("book", help="Book name to process (e.g., Genesis)")
    parser.add_argument("--batch-size", type=int, help="Override batch size (sets BATCH_SIZE env var)")

    args = parser.parse_args()

    # Set environment variable if batch-size provided
    if args.batch_size:
        os.environ["BATCH_SIZE"] = str(args.batch_size)

    # Run the pipeline
    try:
        result = run_pipeline(book=args.book)
        print(f"✅ Pipeline complete for {args.book}")
        print(f"Result: {result}")
        return 0
    except Exception as e:
        print(f"❌ Pipeline failed: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
