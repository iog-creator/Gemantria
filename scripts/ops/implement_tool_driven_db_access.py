#!/usr/bin/env python3
"""
OPS Script: Implement Tool-Driven Database Access (Enhancement B)
=================================================================
Updates `agentpm/tools/bible.py` and `agentpm/tools/__init__.py` to expose
BibleScholar search and lexicon flows as LLM tools.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
BIBLE_TOOLS_FILE = REPO_ROOT / "agentpm/tools/bible.py"
INIT_FILE = REPO_ROOT / "agentpm/tools/__init__.py"


def update_bible_tools():
    print(f"Updating {BIBLE_TOOLS_FILE}...")
    content = BIBLE_TOOLS_FILE.read_text()

    if "def search_bible_verses" in content:
        print("✓ search_bible_verses already present")
    else:
        # Add imports
        imports = """from agentpm.biblescholar.search_flow import search_verses
from agentpm.biblescholar.lexicon_flow import fetch_lexicon_entry
"""
        if "from agentpm.biblescholar.bible_passage_flow import get_db_status" in content:
            content = content.replace(
                "from agentpm.biblescholar.bible_passage_flow import get_db_status",
                "from agentpm.biblescholar.bible_passage_flow import get_db_status\n" + imports,
            )

        # Add functions
        new_functions = """

def search_bible_verses(query: str, translation: str = "KJV", limit: int = 10, **kwargs: Any) -> dict[str, Any]:
    \"\"\"Search Bible verses by keyword.

    Args:
        query: Search keyword (minimum 2 characters).
        translation: Translation identifier (default: "KJV").
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
    \"\"\"
    try:
        results = search_verses(query, translation=translation, limit=limit)
        return {
            "ok": True,
            "query": query,
            "results": [r.to_dict() for r in results],
            "count": len(results),
            "error": None
        }
    except Exception as e:
        return {
            "ok": False,
            "query": query,
            "results": [],
            "count": 0,
            "error": str(e)
        }


def lookup_lexicon_entry(strongs_id: str, **kwargs: Any) -> dict[str, Any]:
    \"\"\"Lookup a lexicon entry by Strong's number.

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
    \"\"\"
    try:
        entry = fetch_lexicon_entry(strongs_id)
        return {
            "ok": True,
            "strongs_id": strongs_id,
            "entry": entry.to_dict() if entry else None,
            "found": entry is not None,
            "error": None
        }
    except Exception as e:
        return {
            "ok": False,
            "strongs_id": strongs_id,
            "entry": None,
            "found": False,
            "error": str(e)
        }
"""
        content += new_functions
        BIBLE_TOOLS_FILE.write_text(content)
        print("✓ Added search_bible_verses and lookup_lexicon_entry")


def update_init_file():
    print(f"Updating {INIT_FILE}...")
    content = INIT_FILE.read_text()

    if "search_bible_verses" in content:
        print("✓ __init__.py already updated")
        return

    # Update imports
    if "from agentpm.tools.bible import retrieve_bible_passages" in content:
        content = content.replace(
            "from agentpm.tools.bible import retrieve_bible_passages",
            "from agentpm.tools.bible import retrieve_bible_passages, search_bible_verses, lookup_lexicon_entry",
        )

    # Update __all__
    if '"retrieve_bible_passages",' in content:
        content = content.replace(
            '"retrieve_bible_passages",',
            '"retrieve_bible_passages",\n    "search_bible_verses",\n    "lookup_lexicon_entry",',
        )

    INIT_FILE.write_text(content)
    print("✓ Updated __init__.py exports")


def main():
    update_bible_tools()
    update_init_file()
    print("SUCCESS: Tool-Driven Database Access implemented")


if __name__ == "__main__":
    main()
