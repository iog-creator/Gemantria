from __future__ import annotations

from datetime import datetime, timedelta, UTC
from typing import Any, Dict, Iterable, List


RFC3339_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


def rfc3339_now() -> str:
    return datetime.now(UTC).strftime(RFC3339_FORMAT)


def _coerce_seed_int(seed: Any) -> int:
    if isinstance(seed, bool):
        raise ValueError("seed must be int, not bool")
    try:
        s = int(seed)
    except Exception as e:
        raise ValueError("seed must be int") from e
    return s


def ensure_provenance(model: str, seed: int | str, analysis: str | None) -> Dict[str, Any]:
    """
    Ensures model/seed/ts_iso are present; preserves analysis even if empty/whitespace.
    Raises ValueError for missing/invalid provenance.
    """
    if not model or not isinstance(model, str):
        raise ValueError("model is required")
    s = _coerce_seed_int(seed)
    ts = rfc3339_now()
    out: Dict[str, Any] = {"model": model, "seed": s, "ts_iso": ts}
    if analysis is not None:
        out["analysis"] = analysis
    return out


def stamp_batch(items: Iterable[Dict[str, Any]], model: str, seed: int | str) -> List[Dict[str, Any]]:
    """
    Stamps a batch with monotonic RFC3339 timestamps (1s increments) and required provenance.
    """
    s = _coerce_seed_int(seed)
    base = datetime.now(UTC).replace(microsecond=0)
    stamped: List[Dict[str, Any]] = []
    for i, it in enumerate(items):
        ts = (base + timedelta(seconds=i)).strftime(RFC3339_FORMAT)
        rec = {**it, "model": model, "seed": s, "ts_iso": ts}
        stamped.append(rec)
    return stamped
