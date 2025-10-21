"""Simplified LangGraph-inspired runner used for early bootstrapping."""

from __future__ import annotations

from argparse import ArgumentParser
from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class GraphRunResult:
    """A tiny value object describing a graph invocation."""

    book: str
    mode: str
    dry_run: bool

    def message(self) -> str:
        dry_run_prefix = "[dry-run] " if self.dry_run else ""
        return f"{dry_run_prefix}Would execute {self.mode} for {self.book}."

    def __str__(self) -> str:  # pragma: no cover - delegation tested via message()
        return self.message()


class HelloGraph:
    """A deterministic runner that stands in for the future LangGraph pipeline."""

    def __init__(self, book: str):
        if not book:
            msg = "A book name must be provided."
            raise ValueError(msg)
        self.book = book

    def run(self, mode: str, dry_run: bool) -> GraphRunResult:
        normalized_mode = mode.upper() or "START"
        if not dry_run:
            msg = "The bootstrap graph only supports dry-run execution."
            raise RuntimeError(msg)
        return GraphRunResult(book=self.book, mode=normalized_mode, dry_run=dry_run)


def build_parser() -> ArgumentParser:
    parser = ArgumentParser(description="Execute the bootstrap hello graph")
    parser.add_argument("book", help="Book to use for the dry-run execution.")
    parser.add_argument(
        "--mode",
        default="START",
        help="Name of the state machine entry point to simulate.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only simulate execution without side effects.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    graph = HelloGraph(args.book)
    result = graph.run(mode=args.mode, dry_run=args.dry_run)
    print(result.message())
    return 0


if __name__ == "__main__":  # pragma: no cover - manual execution hook
    raise SystemExit(main())  # pragma: no cover
