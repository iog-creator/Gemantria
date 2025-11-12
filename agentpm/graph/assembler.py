from __future__ import annotations

from typing import Any, Dict, Iterable, List
from datetime import UTC, datetime
import hashlib
import uuid

from agentpm.extractors.provenance import stamp_batch, _coerce_seed_int


def _uuid7_from_hash(h: bytes) -> str:
    b = bytearray(h[:16])
    b[6] = (b[6] & 0x0F) | 0x70  # version 7
    b[8] = (b[8] & 0x3F) | 0x80  # RFC 4122 variant
    return str(uuid.UUID(bytes=bytes(b)))


def batch_id_v7(base_dt: datetime, seed: int | str) -> str:
    """Deterministic UUIDv7 derived from (base_dt UTC seconds, seed)."""
    if base_dt.tzinfo is None:
        base = base_dt.replace(tzinfo=UTC, microsecond=0)
    else:
        base = base_dt.astimezone(UTC).replace(microsecond=0)
    ms = int(base.timestamp() * 1000)
    s = _coerce_seed_int(seed)
    h = hashlib.sha256(f"{ms}:{s}".encode()).digest()
    return _uuid7_from_hash(h)


def ensure_nodes_have_provenance(nodes: Iterable[Dict[str, Any]]) -> None:
    """Guard: every node.meta.provenance must include model, seed, ts_iso."""
    for i, n in enumerate(nodes):
        meta = n.get("meta") or {}
        prov = meta.get("provenance") or {}
        if not all(k in prov for k in ("model", "seed", "ts_iso")):
            raise ValueError(f"node[{i}] missing provenance")


def assemble_graph(items: Iterable[Dict[str, Any]], model: str, seed: int | str, base_dt: datetime) -> Dict[str, Any]:
    """
    Propagates provenance into downstream graph nodes; preserves input order 1:1.
    - Uses provenance.stamp_batch(..., base_dt=base_dt) for monotonic RFC3339 ts_iso.
    - Attaches node.meta.provenance = {model, seed, ts_iso}.
    - Returns {'batch_id', 'nodes'} and enforces the guard.
    """
    stamped = stamp_batch(list(items), model, seed, base_dt=base_dt)
    nodes: List[Dict[str, Any]] = []
    for it in stamped:
        prov = {k: it[k] for k in ("model", "seed", "ts_iso")}
        nodes.append({"data": it, "meta": {"provenance": prov}})
    ensure_nodes_have_provenance(nodes)
    return {"batch_id": batch_id_v7(base_dt, seed), "nodes": nodes}
