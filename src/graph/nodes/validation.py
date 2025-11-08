# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

from __future__ import annotations

import os
from typing import Any

from src.core.hebrew_utils import calculate_gematria
from src.core.ids import normalize_hebrew
from src.infra.db import get_bible_ro


# Public API
def validate_noun(hebrew_surface: str) -> dict[str, Any]:
    """
    Deterministic validation:
    - Code gematria/normalization are the source of truth.
    - bible_db: presence + strong_number + lemma_frequency + verse_context (if DSN present).
    - LLM: metadata-only (confidence fields optional; no gating).
    """
    norm = normalize_hebrew(hebrew_surface)
    gematria = calculate_gematria(norm)

    db_info: dict[str, Any] = {
        "present_in_bible_db": False,
        "strong_number": None,
        "lemma_frequency": None,
        "verse_context": [],
    }

    # Optional DB lookup
    try:
        ro = get_bible_ro()
        # Example parameterized SQL; projects may adjust to real schema.
        # Finds lemma row + frequency, and grabs a small context window.
        rows = list(
            ro.execute(
                """
            SELECT strong_number, lemma, frequency
            FROM lemmas
            WHERE lemma = %s
            """,
                (norm,),
            )
        )
        if rows:
            strong, _lemma, freq = rows[0]
            db_info["present_in_bible_db"] = True
            db_info["strong_number"] = strong
            db_info["lemma_frequency"] = int(freq)

            ctx = list(
                ro.execute(
                    """
                SELECT book, chapter, verse, verse_text
                FROM verses
                WHERE lemma = %s
                ORDER BY book, chapter, verse
                LIMIT 5
                """,
                    (norm,),
                )
            )
            db_info["verse_context"] = [
                {"book": c[0], "chapter": int(c[1]), "verse": int(c[2]), "text": c[3]} for c in ctx
            ]
    except RuntimeError:
        # No DSN / no driver: allowed; we just skip DB augmentation.
        pass

    # LLM metadata (no gating)
    llm_meta = {
        "provider": "lm_studio",
        "endpoint": os.getenv("LM_STUDIO_HOST", "http://127.0.0.1:1234"),
        "confidence": None,  # reserved for future use; not used for validation logic
    }

    return {
        "surface": hebrew_surface,
        "normalized": norm,
        "gematria": gematria,
        "db": db_info,
        "llm": llm_meta,
    }
