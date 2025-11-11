"""Example instrumented agent: extract_book."""
from __future__ import annotations

from scripts.observability.otel_helpers import span_tool


def extract_book(sql: str, db_executor):
    """Extract book data from database (instrumented example)."""
    verb = (sql.split()[0] if sql else "query").upper()
    with span_tool("pg.query", sql_verb=verb, table="unknown"):
        rows = db_executor(sql)
    return rows


if __name__ == "__main__":
    def dummy_exec(q):
        return [{"row": 1}]

    print(extract_book("SELECT 1", dummy_exec))
