"""Semantic agent for extracting semantic features from nouns."""

from typing import Dict, Any

from src.services.lmstudio_client import chat_completion


def extract_semantic_features(noun: Dict[str, Any]) -> Dict[str, Any]:
    """Extract semantic features from a noun using LLM analysis.

    Args:
        noun: Noun dictionary with Hebrew text and metadata

    Returns:
        Dictionary with semantic features
    """
    hebrew_text = noun.get("hebrew_text", "")
    gematria_value = noun.get("gematria_value", 0)

    # Create semantic analysis prompt
    messages = [
        {
            "role": "system",
            "content": """You are a biblical Hebrew semantic expert.
            Analyze the semantic features of this Hebrew noun in the context of biblical theology.

            Return JSON with:
            - semantic_category: the semantic category (e.g., "divine", "human", "creation", etc.)
            - theological_significance: brief description of theological meaning
            - lexical_field: related concepts or words
            - confidence: confidence score 0.0-1.0""",
        },
        {
            "role": "user",
            "content": f"Extract semantic features for this Hebrew noun:\n\nHebrew: {hebrew_text}\nGematria: {gematria_value}\n\nReturn analysis as JSON.",
        },
    ]

    try:
        # Use the THEOLOGY_MODEL for semantic analysis
        model = "christian-bible-expert-v2.0-12b"  # Default theology model
        results = chat_completion([messages], model, temperature=0.0)
        if results and len(results) > 0:
            return {"semantic_text": results[0], "extracted": True}
        else:
            # Fallback
            return {
                "semantic_text": '{"semantic_category": "unknown", "theological_significance": "Analysis unavailable", "lexical_field": [], "confidence": 0.0}',
                "extracted": False,
            }
    except Exception as e:
        # Fail gracefully
        return {
            "semantic_text": '{"semantic_category": "error", "theological_significance": "Error in analysis: '
            + str(e)
            + '", "lexical_field": [], "confidence": 0.0}',
            "extracted": False,
        }
