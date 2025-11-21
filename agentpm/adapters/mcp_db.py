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


def catalog_read_ro(dsn: str | None = None) -> Dict[str, Any]:
    """
    PLAN-091: Minimal Postgres RO adapter for mcp.v_catalog.
    Reads tool catalog from DB using centralized DSN loader.
    Opt-in only (not wired into CI); fails closed if DSN/view unavailable.
    """
    if not dsn:
        # Try to load from centralized loader (RO mode)
        try:
            from scripts.config.env import get_ro_dsn

            dsn = get_ro_dsn()
        except Exception:
            pass

    if not dsn:
        return {"ok": False, "error": "DSN not available", "tools": []}

    try:
        import psycopg

        with psycopg.connect(dsn, autocommit=True) as conn:
            with conn.cursor() as cur:
                # Try to read from mcp.v_catalog (if exists)
                cur.execute("SELECT id, name, ring FROM mcp.v_catalog ORDER BY id")
                tools = [{"id": row[0], "name": row[1], "ring": row[2]} for row in cur.fetchall()]
                return {"ok": True, "tools": tools, "count": len(tools)}
    except Exception as e:
        return {"ok": False, "error": str(e), "tools": []}
