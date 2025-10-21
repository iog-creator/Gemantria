from __future__ import annotations

import json
from typing import Any, TypedDict


class PipelineState(TypedDict, total=False):
    book_name: str
    mode: str
    nouns: list[dict[str, Any]]
    conflicts: list[dict[str, Any]]
    predictions: dict[str, Any]
    metadata: dict[str, Any]

def run_hello(book: str = "Genesis", mode: str = "START") -> PipelineState:
    # placeholder runner; real graph with nodes arrives in later PRs
    # checkpointer available via get_checkpointer() - will be wired to StateGraph
    return {"book_name": book, "mode": mode, "nouns": [], "conflicts": []}

if __name__ == "__main__":
    print(json.dumps(run_hello(), ensure_ascii=False))
