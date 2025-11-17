"""BibleScholar passage service with commentary generation.

Phase-9A: Provides passage lookup and theology-aware commentary using the theology LM slot.
"""

from __future__ import annotations

from typing import Any

from agentpm.adapters.theology import chat as theology_chat
from agentpm.biblescholar.bible_passage_flow import fetch_passage


def fetch_passage_dict(reference: str, translation_source: str = "KJV") -> dict[str, Any]:
    """Fetch a passage by reference string and return as dict.

    Args:
        reference: Bible reference string (e.g., "John 3:16-18").
        translation_source: Translation identifier (default: "KJV").

    Returns:
        Dict with:
        {
            "reference": str,
            "verses": [
                {
                    "book": str,
                    "chapter": int,
                    "verse": int,
                    "text": str,
                },
                ...
            ],
            "errors": list[str],  # Empty if no errors
        }
    """
    errors: list[str] = []
    verses_list: list[dict[str, Any]] = []

    if not reference or not reference.strip():
        errors.append("Reference cannot be empty")
        return {"reference": reference, "verses": [], "errors": errors}

    try:
        verse_records = fetch_passage(reference.strip(), translation_source=translation_source)
    except Exception as e:
        errors.append(f"Error fetching passage: {e!s}")
        return {"reference": reference, "verses": [], "errors": errors}

    if not verse_records:
        errors.append(f"No verses found for reference: {reference}")
        return {"reference": reference, "verses": [], "errors": errors}

    for verse in verse_records:
        verses_list.append(
            {
                "book": verse.book_name,
                "chapter": verse.chapter_num,
                "verse": verse.verse_num,
                "text": verse.text,
            }
        )

    return {"reference": reference, "verses": verses_list, "errors": errors}


def generate_commentary(passage: dict[str, Any], *, use_lm: bool = True) -> dict[str, Any]:
    """Generate commentary for a passage using theology LM or fallback.

    Args:
        passage: Dict from fetch_passage_dict() with "reference" and "verses" keys.
        use_lm: If True, attempt to use theology LM; if False, return fallback.

    Returns:
        Dict with:
        {
            "source": "lm_theology" | "fallback",
            "text": str,
        }
    """
    if not use_lm:
        return {
            "source": "fallback",
            "text": "Theology model commentary is disabled. Passage text is shown without commentary.",
        }

    verses = passage.get("verses", [])
    if not verses:
        return {
            "source": "fallback",
            "text": "No passage text available for commentary.",
        }

    # Build passage text for the prompt
    passage_text_parts: list[str] = []
    for verse in verses:
        book = verse.get("book", "")
        chapter = verse.get("chapter", 0)
        verse_num = verse.get("verse", 0)
        text = verse.get("text", "")
        passage_text_parts.append(f"{book} {chapter}:{verse_num} {text}")

    passage_text = "\n".join(passage_text_parts)
    reference = passage.get("reference", "unknown")

    # System prompt for theology-aware commentary
    system_prompt = """You are a Christian Bible expert providing concise, theologically sound commentary.
Focus on:
- Context and historical background
- Key themes and theological significance
- How the passage relates to broader biblical themes
- Practical application when appropriate

Keep commentary to 2-5 paragraphs. Avoid doctrinal extremes; maintain a balanced, scholarly tone.
Cite specific verses when making cross-references."""

    user_prompt = f"""Please provide a brief theological commentary on this passage:

Reference: {reference}

{passage_text}

Commentary:"""

    try:
        commentary_text = theology_chat(user_prompt, system=system_prompt)
        return {"source": "lm_theology", "text": commentary_text}
    except Exception as e:
        # LM unavailable or error - return fallback
        return {
            "source": "fallback",
            "text": f"Theology model is currently unavailable ({e!s}). Passage text is shown without commentary.",
        }


def get_passage_and_commentary(
    reference: str, *, use_lm: bool = True, translation_source: str = "KJV"
) -> dict[str, Any]:
    """Get passage and commentary in a single call.

    Args:
        reference: Bible reference string (e.g., "John 3:16-18").
        use_lm: If True, attempt to generate LM commentary; if False, use fallback.
        translation_source: Translation identifier (default: "KJV").

    Returns:
        Dict with:
        {
            "reference": str,
            "verses": list[dict],
            "commentary": {
                "source": "lm_theology" | "fallback",
                "text": str,
            },
            "errors": list[str],
        }
        Never raises; errors are included in the "errors" field.
    """
    passage = fetch_passage_dict(reference, translation_source=translation_source)
    commentary = generate_commentary(passage, use_lm=use_lm)

    return {
        "reference": passage["reference"],
        "verses": passage["verses"],
        "commentary": commentary,
        "errors": passage["errors"],
    }
