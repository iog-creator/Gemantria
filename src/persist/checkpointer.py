import os, json, uuid, time
from typing import Any, Dict, Optional

try:
    import psycopg
except Exception as e:  # defer import errors to runtime path that needs it
    psycopg = None


def _compact_state(state: Dict[str, Any]) -> Dict[str, Any]:
    """Small, stable summary to avoid giant JSON payloads."""
    out = {"keys": sorted(list(state.keys()))}
    for k in ("nouns", "enriched_nouns", "graph", "scored_graph", "stats"):
        v = state.get(k)
        if isinstance(v, list):
            out[f"{k}_len"] = len(v)
        elif isinstance(v, dict):
            out[f"{k}_keys"] = list(v.keys())[:10]
    return out


class BaseCheckpointer:
    def start_run(self, book: str) -> str:
        raise NotImplementedError
    def save(self, run_id: str, node: str, state: Dict[str, Any]) -> None:
        raise NotImplementedError
    def finish(self, run_id: str, status: str = "ok") -> None:
        raise NotImplementedError


class MemoryCheckpointer(BaseCheckpointer):
    def __init__(self): self._runs = {}
    def start_run(self, book: str) -> str:
        rid = str(uuid.uuid4()); self._runs[rid] = {"book": book, "events": []}; return rid
    def save(self, run_id: str, node: str, state: Dict[str, Any]) -> None:
        self._runs[run_id]["events"].append({"ts": time.time(), "node": node, "state": _compact_state(state)})
    def finish(self, run_id: str, status: str = "ok") -> None:
        self._runs[run_id]["status"] = status


class PostgresCheckpointer(BaseCheckpointer):
    def __init__(self, dsn: str, payload_mode: str = "summary"):
        if psycopg is None:
            raise RuntimeError("psycopg not available; install psycopg or use CHECKPOINTER=memory")
        self.dsn = dsn
        self.payload_mode = payload_mode
    def _conn(self):
        return psycopg.connect(self.dsn)
    def start_run(self, book: str) -> str:
        with self._conn() as c, c.cursor() as cur:
            cur.execute(
                "INSERT INTO gematria.runs(book, status) VALUES (%s,'running') RETURNING run_id",
                (book,),
            )
            rid = str(cur.fetchone()[0])
        return rid
    def save(self, run_id: str, node: str, state: Dict[str, Any]) -> None:
        payload = _compact_state(state) if self.payload_mode != "full" else state
        with self._conn() as c, c.cursor() as cur:
            cur.execute(
                "INSERT INTO gematria.checkpoints(run_id, node, payload) VALUES (%s,%s,%s::jsonb)",
                (run_id, node, json.dumps(payload)),
            )
    def finish(self, run_id: str, status: str = "ok") -> None:
        with self._conn() as c, c.cursor() as cur:
            cur.execute(
                "UPDATE gematria.runs SET finished_at=NOW(), status=%s WHERE run_id=%s",
                (status, run_id),
            )


def get_checkpointer() -> BaseCheckpointer:
    mode = (os.getenv("CHECKPOINTER") or "memory").lower()
    if mode == "postgres":
        dsn = os.getenv("GEMATRIA_DSN")
        if not dsn: raise RuntimeError("GEMATRIA_DSN is required when CHECKPOINTER=postgres")
        return PostgresCheckpointer(dsn=dsn, payload_mode=os.getenv("CHECKPOINT_PAYLOAD","summary"))
    return MemoryCheckpointer()
