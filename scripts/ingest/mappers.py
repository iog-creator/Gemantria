from __future__ import annotations
from typing import Dict, Any

_MAX_LABEL = 120
_MAX_TYPE = 40


def normalize_label(label: str) -> str:
    if label is None:
        return ""
    s = " ".join(str(label).split())
    return s[:_MAX_LABEL]


def normalize_type(t: str) -> str:
    if t is None:
        return ""
    s = " ".join(str(t).split())
    return s[:_MAX_TYPE]


def clamp_weight(value: float) -> float:
    try:
        v = float(value)
    except Exception:
        return 0.0
    if v < 0.0:
        return 0.0
    if v > 1.0:
        return 1.0
    return v


def normalize_verse_ref(book: str, chapter: int, verse: int) -> str:
    return f"{book} {int(chapter)}:{int(verse)}"


def map_node(raw: Dict[str, Any]) -> Dict[str, Any]:
    rid = str(raw.get("id", "")).strip()
    label = normalize_label(raw.get("label", ""))
    ntype = normalize_type(raw.get("type", "")) if raw.get("type") is not None else ""
    attrs = raw.get("attrs") or {}
    return {"id": rid, "label": label, "type": ntype, "attrs": attrs}


def map_edge(raw: Dict[str, Any]) -> Dict[str, Any]:
    src = str(raw.get("src", "")).strip()
    dst = str(raw.get("dst", "")).strip()
    rtype = normalize_type(raw.get("rel_type", ""))
    weight = clamp_weight(raw.get("weight", 0.0))
    return {"src": src, "dst": dst, "rel_type": rtype, "weight": weight}
