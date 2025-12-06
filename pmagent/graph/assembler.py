from __future__ import annotations

from typing import Any, Dict, Iterable, List
from collections import defaultdict
from datetime import UTC, datetime
import hashlib
import json
import uuid

from pmagent.extractors.provenance import stamp_batch, _coerce_seed_int


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


def provenance_hash(prov: Dict[str, Any]) -> str:
    """Stable SHA-256 over sorted JSON of provenance."""
    blob = json.dumps(prov, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(blob).hexdigest()


def assemble_graph(items: Iterable[Dict[str, Any]], model: str, seed: int | str, base_dt: datetime) -> Dict[str, Any]:
    """
    Build graph with provenance propagation and audit trail.
    - Uses stamp_batch(..., base_dt=...) to stamp ts_iso (monotonic) + attach model/seed.
    - Propagates provenance into node.meta.provenance.
    - Adds node.meta.audit = {batch_id, provenance_hash}.
    - Computes graph.meta.provenance_rollup (models, seeds, ts_min, ts_max).
    - Returns {batch_id, meta, nodes}, preserving input order 1:1.
    """
    stamped = stamp_batch(list(items), model, seed, base_dt=base_dt)
    bid = batch_id_v7(base_dt, seed)
    nodes: List[Dict[str, Any]] = []
    models: set[str] = set()
    seeds: set[int] = set()
    ts_vals: List[str] = []

    for it in stamped:
        prov = {k: it[k] for k in ("model", "seed", "ts_iso")}
        models.add(prov["model"])
        seeds.add(int(prov["seed"]))
        ts_vals.append(prov["ts_iso"])
        node = {
            "data": it,
            "meta": {
                "provenance": prov,
                "audit": {"batch_id": bid, "provenance_hash": provenance_hash(prov)},
            },
        }
        nodes.append(node)

    ensure_nodes_have_provenance(nodes)
    rollup = {
        "models": sorted(models),
        "seeds": sorted(seeds),
        "ts_min": min(ts_vals) if ts_vals else None,
        "ts_max": max(ts_vals) if ts_vals else None,
    }
    return {"batch_id": bid, "meta": {"provenance_rollup": rollup}, "nodes": nodes}


def correlate_nodes_across_batches(graphs: Iterable[Dict[str, Any]], key_field: str) -> Dict[Any, List[str]]:
    """
    Cross-batch correlation (E19): for each graph, map node.data[key_field] -> batch_id list.
    Order of batch_ids follows input graphs order; duplicates avoided.
    """
    mapping: defaultdict[Any, List[str]] = defaultdict(list)
    for g in graphs:
        bid = g.get("batch_id")
        for n in g.get("nodes", []):
            k = n.get("data", {}).get(key_field)
            if k is None:
                continue
            if not mapping[k] or mapping[k][-1] != bid:
                mapping[k].append(bid)
    return dict(mapping)
