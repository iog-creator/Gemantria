from __future__ import annotations

import hashlib
import re
import unicodedata
import uuid
from typing import Any

MAQAF = "\u05BE"
SOF_PASUQ = "\u05C3"
_PUNCT = re.compile(r"[^\w\u0590-\u05FF]+", re.UNICODE)


def normalize_hebrew(text: str) -> str:
    """NFKD → strip combining → remove maqaf/sof pasuq/punct → NFC"""
    nk = unicodedata.normalize("NFKD", text)
    no_marks = "".join(ch for ch in nk if not unicodedata.combining(ch))
    no_punct = no_marks.replace(MAQAF, "").replace(SOF_PASUQ, "")
    no_punct = _PUNCT.sub("", no_punct)
    return unicodedata.normalize("NFC", no_punct)


def content_hash(payload: dict[str, Any], keys: list[str]) -> str:
    """Canonical SHA-256 over selected keys (order matters)."""
    data = "|".join(str(payload.get(k, "")) for k in keys)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def uuidv7_surrogate() -> str:
    """Sortable surrogate id. Identity remains content_hash."""
    return str(uuid.uuid4())
