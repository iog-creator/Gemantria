"""Noun processing planner agent."""

import json
from typing import Dict, Any

from src.services.lmstudio_client import chat_completion


def plan_processing(noun: Dict[str, Any]) -> Dict[str, str]:
    """Plan processing strategy for a noun.

    Args:
        noun: Noun dictionary with Hebrew text, gematria values, etc.

    Returns:
        Dictionary with 'text' key containing planning analysis.
    """
    # Handle both dict and object formats
    if isinstance(noun, dict):
        noun_name = noun.get("name", noun.get("hebrew", "")).strip()
        noun_surface = noun.get("surface", noun.get("hebrew", noun_name))
        gematria = noun.get("gematria", noun.get("value", 0))
        classification = noun.get("classification", "")
    else:
        # Fallback for object format
        noun_name = (
            getattr(noun, "name", getattr(noun, "hebrew", "")).strip()
            if hasattr(noun, "name") or hasattr(noun, "hebrew")
            else str(noun).strip()
        )
        noun_surface = getattr(noun, "surface", getattr(noun, "hebrew", noun_name))
        gematria = getattr(noun, "gematria", getattr(noun, "value", 0))
        classification = getattr(noun, "classification", "")

    # Create planning prompt
    messages = [
        {
            "role": "system",
            "content": """You are a biblical Hebrew expert analyzing nouns for gematria processing.
            Determine what types of analysis this noun needs:

            - needs_math: true if complex gematria calculations or mathematical patterns are required
            - needs_semantic: true if theological or semantic analysis would be valuable
            - needs_expert: true if this requires specialized biblical knowledge

            Return only valid JSON with these boolean fields.""",
        },
        {
            "role": "user",
            "content": f"Analyze this Hebrew noun for processing needs:\n\nHebrew: {noun_surface}\nName: {noun_name}\nGematria: {gematria}\nClassification: {classification}\n\nReturn JSON with needs_math, needs_semantic, needs_expert fields.",
        },
    ]

    try:
        # Use the THEOLOGY_MODEL for planning
        model = "christian-bible-expert-v2.0-12b"  # Default theology model
        results = chat_completion(messages, model, temperature=0.0)
        if results and len(results) > 0:
            return {"text": results[0].text}
        else:
            # Fallback if no result
            return {"text": '{"needs_math": false, "needs_semantic": false, "needs_expert": false}'}
    except Exception:
        # Fail gracefully with default planning
        return {"text": '{"needs_math": false, "needs_semantic": false, "needs_expert": false}'}


def parse_llm_json(text: str) -> Dict[str, Any]:
    """Parse JSON response from LLM, handling various formats."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to extract JSON from markdown
        import re

        json_match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        # Fallback to default
        return {"needs_math": False, "needs_semantic": False, "needs_expert": False}
