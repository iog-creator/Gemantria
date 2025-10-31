from __future__ import annotations

import os
from typing import Any

from src.core.books import normalize_book
from src.infra.db import get_bible_ro

DEFAULT_SQL = """
SELECT
  lemma,
  MIN(book)||' '||MIN(chapter)||':'||MIN(verse) AS primary_verse,
  COUNT(*) AS freq
FROM v_hebrew_tokens
WHERE book = %s AND pos IN ('NOUN','PROPN')
GROUP BY lemma
ORDER BY freq DESC
"""

SQL_FALLBACK = """
SELECT
  lemma,
  MIN(book)||' '||MIN(chapter)||':'||MIN(verse) AS primary_verse,
  COUNT(*) AS freq
FROM v_hebrew_tokens
WHERE (LOWER(book)=LOWER(%s) OR LOWER(book) IN ('gen','בראשית'))
GROUP BY lemma
ORDER BY freq DESC
"""


def _get_sql() -> str:
    override = os.getenv("HEBREW_TOKENS_SQL_OVERRIDE")
    if override:
        return override.strip()
    return DEFAULT_SQL or SQL_FALLBACK


def collect_nouns_for_book(book: str) -> list[dict[str, Any]]:
    b = normalize_book(book)
    sql = _get_sql()
    out: list[dict[str, Any]] = []
    rows = get_bible_ro().execute(sql, (b,))
    for lemma, primary_verse, freq in rows:
        out.append(
            {
                "hebrew": lemma,
                "name": lemma,
                "value": None,
                "primary_verse": primary_verse,
                "freq": int(freq),
                "book": b,
            }
        )
    if not out:
        raise RuntimeError(f"No nouns found for book={b}")

    # Sanity check: fail-fast if we clearly undercounting
    if len(out) < 10:
        raise RuntimeError(
            f"Suspiciously low noun count for {book}: {len(out)}. "
            f"Check book/POS mapping or view source. "
            f"Found: {[n['hebrew'] for n in out]}"
        )

    return out
