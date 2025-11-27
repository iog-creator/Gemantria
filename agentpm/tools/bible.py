#!/usr/bin/env python3
"""
Bible Tools - Retrieve Bible passages.
"""

from __future__ import annotations

from typing import Any

from agentpm.biblescholar.passage import get_passage_and_commentary
from agentpm.biblescholar.bible_passage_flow import get_db_status
from agentpm.biblescholar.bible_db_adapter import BibleDbAdapter
from agentpm.biblescholar.lexicon_adapter import LexiconAdapter
from agentpm.runtime.lm_logging import write_agent_run


def retrieve_bible_passages(reference: str, use_lm: bool = True, **kwargs: Any) -> dict[str, Any]:
    """Retrieve Bible passages by reference.

    Args:
        reference: Bible reference string (e.g., "John 3:16-18").
        use_lm: If True, generate theology commentary (fail-closed if unavailable); if False, return fallback.
        **kwargs: Additional arguments (ignored for now).

    Returns:
        Dict with:
        {
            "ok": bool,
            "reference": str,
            "verses": list[dict],
            "commentary": dict,
            "errors": list[str],
        }

    Raises:
        RuntimeError: If database is unavailable or use_lm=True and theology model service is unavailable (fail-closed).
        ValueError: If reference is empty or invalid.
    """
    if not reference or not reference.strip():
        raise ValueError("Reference cannot be empty")

    # Fail-closed: check database availability first
    db_status = get_db_status()
    if db_status != "available":
        raise RuntimeError(f"Bible database unavailable: {db_status}")

    # Fail-closed: let RuntimeError propagate if use_lm=True and service unavailable
    result = get_passage_and_commentary(reference, use_lm=use_lm)

    return {
        "ok": len(result.get("errors", [])) == 0,
        **result,
    }


def search_bible_verses(query: str, translation: str, limit: int = 10, **kwargs: Any) -> dict[str, Any]:
    """Search Bible verses by keyword.

    Args:
        query: Search keyword (minimum 2 characters).
        translation: Translation identifier (required, e.g., "KJV", "ESV", "ASV", "YLT").
        limit: Maximum number of results (default: 10).
        **kwargs: Additional arguments (ignored).

    Returns:
        Dict with:
        {
            "ok": bool,
            "query": str,
            "results": list[dict],
            "count": int,
            "error": str | None
        }
    """
    try:
        if not query or len(query.strip()) < 2:
            return {"ok": True, "query": query, "results": [], "count": 0, "error": None}

        adapter = BibleDbAdapter()
        results = adapter.search_verses(query.strip(), translation_source=translation, limit=limit)

        results_list = []
        for r in results:
            results_list.append(
                {
                    "verse_id": r.verse_id,
                    "book_name": r.book_name,
                    "chapter_num": r.chapter_num,
                    "verse_num": r.verse_num,
                    "text": r.text,
                    "translation_source": r.translation_source,
                }
            )

        write_agent_run(
            tool="search_bible_verses",
            args_json={"query": query, "translation": translation, "limit": limit},
            result_json={"count": len(results), "ok": True},
        )

        return {
            "ok": True,
            "query": query,
            "results": results_list,
            "count": len(results),
            "error": None,
        }
    except Exception as e:
        write_agent_run(
            tool="search_bible_verses",
            args_json={"query": query, "translation": translation, "limit": limit},
            result_json={"ok": False, "error": str(e)},
            violations_json=[{"type": "exception", "reason": str(e)}],
        )
        return {"ok": False, "query": query, "results": [], "count": 0, "error": str(e)}


def lookup_lexicon_entry(strongs_id: str, **kwargs: Any) -> dict[str, Any]:
    """Lookup a lexicon entry by Strong's number.

    Args:
        strongs_id: Strong's number (e.g., "H1", "G1").
        **kwargs: Additional arguments (ignored).

    Returns:
        Dict with:
        {
            "ok": bool,
            "strongs_id": str,
            "entry": dict | None,
            "found": bool,
            "error": str | None
        }
    """
    try:
        adapter = LexiconAdapter()
        sid = strongs_id.upper()
        entry = None

        if sid.startswith("H"):
            entry = adapter.get_hebrew_entry(sid)
        elif sid.startswith("G"):
            entry = adapter.get_greek_entry(sid)
        else:
            entry = adapter.get_hebrew_entry(sid)
            if not entry:
                entry = adapter.get_greek_entry(sid)

        entry_dict = None
        if entry:
            entry_dict = {
                "entry_id": entry.entry_id,
                "strongs_id": entry.strongs_id,
                "lemma": entry.lemma,
                "transliteration": entry.transliteration,
                "definition": entry.definition,
                "usage": entry.usage,
                "gloss": entry.gloss,
            }

        write_agent_run(
            tool="lookup_lexicon_entry",
            args_json={"strongs_id": strongs_id},
            result_json={"found": entry is not None, "ok": True},
        )

        return {
            "ok": True,
            "strongs_id": strongs_id,
            "entry": entry_dict,
            "found": entry is not None,
            "error": None,
        }
    except Exception as e:
        write_agent_run(
            tool="lookup_lexicon_entry",
            args_json={"strongs_id": strongs_id},
            result_json={"ok": False, "error": str(e)},
            violations_json=[{"type": "exception", "reason": str(e)}],
        )
        return {"ok": False, "strongs_id": strongs_id, "entry": None, "found": False, "error": str(e)}
