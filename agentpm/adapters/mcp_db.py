from typing import List, Dict, Any


def catalog_read() -> List[Dict[str, Any]]:
    """
    Read-only adapter stub: returns a deterministic tool catalog for unit tests.
    STRICT/tag lanes can replace this with a real DB call to mcp.v_catalog.
    """
    return [
        {"id": 1, "name": "retrieve_bible_passages", "ring": 1},
        {"id": 2, "name": "rerank_passages", "ring": 1},
    ]
