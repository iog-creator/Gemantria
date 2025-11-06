"""Expert agent for theological analysis of nouns."""

from typing import Dict, Any, List

from src.services.lmstudio_client import chat_completion
from src.ssot.noun_adapter import adapt_ai_noun
from logging import getLogger
from types import SimpleNamespace

logger = getLogger(__name__)


def _text(x: Any) -> str:
    return x.text if isinstance(x, SimpleNamespace) and hasattr(x, "text") else (x or "")


def enrich_with_theology(ai_nouns: List[Dict[str, Any]], llm) -> List[Dict[str, Any]]:
    """
    Produce concise Christian-theology enrichment in analysis.theology for each noun.
    Uses 'christian' model via llm client already injected by caller.
    """
    out: List[Dict[str, Any]] = []
    for raw in ai_nouns:
        n = adapt_ai_noun(raw)
        prompt = (
            f"Provide concise Christian-theology context for the Hebrew noun '{n['surface']}'. "
            "Return JSON with keys: themes (1-3 short strings), cross_refs (0-5 ref strings), notes (<=120 chars). "
            "Do not invent sources; draw from canonical motifs."
        )
        resp = llm.complete(prompt)  # supports SimpleNamespace.text or str
        txt = _text(resp)
        # tolerant parse; keep it safe if model returns plain text
        themes, refs, notes = [], [], txt.strip()[:120]
        try:
            import json

            j = json.loads(txt)
            themes = j.get("themes") or themes
            refs = j.get("cross_refs") or refs
            notes = j.get("notes") or notes
        except Exception:
            pass
        analysis = dict(n.get("analysis") or {})
        analysis["theology"] = {"themes": themes, "cross_refs": refs, "notes": notes}
        n["analysis"] = analysis
        out.append(n)
    return out


def analyze_theological(noun: Dict[str, Any]) -> Dict[str, Any]:
    """Perform expert theological analysis on a noun.

    Args:
        noun: Noun dictionary with Hebrew text and metadata

    Returns:
        Dictionary with theological analysis
    """
    hebrew_text = noun.get("hebrew_text", "")
    gematria_value = noun.get("gematria_value", 0)
    semantic_features = noun.get("semantic_features", {})

    # Create expert analysis prompt
    messages = [
        {
            "role": "system",
            "content": """You are a biblical theology expert with deep knowledge of Hebrew etymology and biblical patterns.
            Provide expert theological analysis of this Hebrew noun in its biblical context.

            Return JSON with:
            - etymological_roots: Hebrew word roots and their meanings
            - biblical_context: how this word appears in biblical narratives
            - theological_themes: key theological themes associated with this word
            - interpretive_significance: significance for biblical interpretation
            - confidence: confidence score 0.0-1.0""",
        },
        {
            "role": "user",
            "content": f"Provide expert theological analysis for this Hebrew noun:\n\nHebrew: {hebrew_text}\nGematria: {gematria_value}\nSemantic features: {semantic_features}\n\nReturn expert analysis as JSON.",
        },
    ]

    try:
        # Use the THEOLOGY_MODEL for expert analysis
        model = "christian-bible-expert-v2.0-12b"  # Default theology model
        results = chat_completion([messages], model, temperature=0.0)
        if results and len(results) > 0:
            return {"expert_text": results[0], "analyzed": True}
        else:
            # Fallback
            return {
                "expert_text": '{"etymological_roots": "unknown", "biblical_context": "Analysis unavailable", "theological_themes": [], "interpretive_significance": "Limited analysis available", "confidence": 0.0}',
                "analyzed": False,
            }
    except Exception as e:
        # Fail gracefully
        return {
            "expert_text": '{"etymological_roots": "error", "biblical_context": "Error in analysis: '
            + str(e)
            + '", "theological_themes": [], "interpretive_significance": "Analysis failed", "confidence": 0.0}',
            "analyzed": False,
        }
