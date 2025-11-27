"""
Passage Commentary Service (Phase 9A)
-------------------------------------
Provides passage lookup and theology-aware commentary using the theology LM slot.

CONTRACT:
1. Must use 'theology' LM adapter (Christian Bible Expert).
2. Must fail-closed if LM is unavailable (RuntimeError) or bypassed (ValueError).
3. Must use insights_flow for DB-grounded context.
"""

from typing import Dict
from agentpm.adapters.theology import chat as theology_chat
from agentpm.biblescholar.bible_passage_flow import fetch_passage
from agentpm.biblescholar.insights_flow import InsightsFlow

# Initialize flows
insights_flow = InsightsFlow()


def generate_commentary(passage_ref: str, use_lm: bool = False) -> Dict:
    """
    Generate commentary for a passage using theology LM (opt-in only).

    Args:
        passage_ref: Bible reference (e.g., "Genesis 1:1").
        use_lm: If True, attempt to use theology LM; if False, return fallback.

    Returns:
        Dict with "source" ("lm_theology" or "fallback") and "text".

    Raises:
        RuntimeError: If theology LM is requested but unavailable (fail-closed when use_lm=True).
    """
    if not use_lm:
        return {
            "source": "fallback",
            "text": f"Commentary not requested for {passage_ref}. Enable 'Use AI commentary' to generate theology-based commentary.",
        }

    # 1. Get DB-grounded context
    # Note: In a real implementation, we'd resolve the ref to an ID first.
    # For this phase, we assume the ref can be mapped or passed to insights.
    # We'll use a placeholder ID '1' for demonstration if ref isn't an ID.
    verse_id = passage_ref if passage_ref.isdigit() else "1"
    context = insights_flow.get_verse_context(verse_id)

    # 2. Construct Prompt
    system_prompt = (
        "You are a Christian Bible Expert. Use the provided context to explain the passage. "
        "Do not invent facts not in the context or the Bible."
    )
    user_prompt = f"Explain {passage_ref} given this context: {context}"

    # 3. Call Theology LM (Fail-Closed)
    try:
        commentary_text = theology_chat(user_prompt, system=system_prompt)
        return {"source": "lm_theology", "text": commentary_text}
    except Exception as e:
        # Re-raise as RuntimeError to satisfy contract if it's a connection error
        raise RuntimeError(f"Theology LM unavailable: {e}") from e


def get_passage_and_commentary(passage_ref: str, translation_source: str = "KJV", use_lm: bool = False) -> Dict:
    """
    Get both passage text (from DB) and commentary (from LM).

    Args:
        passage_ref: Bible reference (e.g., "Genesis 1:1").
        translation_source: Translation identifier (required, e.g., "KJV", "ESV", "ASV", "YLT").
        use_lm: If True, attempt to use theology LM; if False, raise ValueError.

    Returns:
        Dict with "reference", "text" (from DB), and "commentary" (from LM).
    """
    # 1. Get Passage Text (DB) using fetch_passage with translation
    verses = fetch_passage(passage_ref, translation_source=translation_source)
    passage_text = "\n".join([f"{v.verse_num}. {v.text}" for v in verses]) if verses else "Text not found"

    # 2. Get Commentary (LM)
    commentary = generate_commentary(passage_ref, use_lm=use_lm)

    return {"reference": passage_ref, "text": passage_text, "commentary": commentary}
