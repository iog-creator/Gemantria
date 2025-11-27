from __future__ import annotations

"""BibleScholar reference answer slice (Phase-6P).

This module provides a single end-to-end BibleScholar interaction that:
- Resolves verse context from bible_db (read-only)
- Retrieves Gematria numeric patterns
- Optionally finds similar verses using vector similarity
- Performs LM Studio guarded call with budget & provenance
- Returns structured answer with trace and context

See:
- docs/SSOT/BIBLESCHOLAR_REFERENCE_SLICE.md
- agentpm/biblescholar/AGENTS.md
"""

from dataclasses import dataclass
from typing import Any

from agentpm.biblescholar.bible_db_adapter import BibleDbAdapter, VerseRecord
from agentpm.biblescholar.bible_passage_flow import parse_reference
from agentpm.biblescholar.gematria_flow import compute_verse_gematria
from agentpm.biblescholar.vector_flow import similar_verses_for_reference
from agentpm.runtime.lm_logging import guarded_lm_call
from agentpm.modules.gematria.utils.osis import normalize_book_to_osis


@dataclass
class ReferenceAnswerResult:
    """Result of a reference answer slice query.

    Attributes:
        answer: Synthesized answer from LM (or fallback message).
        trace: List of trace entries for each step in the flow.
        context_used: Dictionary of context sources used (verse refs, gematria values, etc.).
        lm_meta: LM call metadata (model, tokens, latency, budget_status).
    """

    answer: str
    trace: list[dict[str, Any]]
    context_used: dict[str, Any]
    lm_meta: dict[str, Any] | None


def _reference_to_osis(book_name: str, chapter_num: int, verse_num: int) -> str | None:
    """Convert a Bible reference to OSIS format.

    Args:
        book_name: Book name (e.g., "Genesis", "Matthew").
        chapter_num: Chapter number (1-indexed).
        verse_num: Verse number (1-indexed).

    Returns:
        OSIS reference string (e.g., "Gen.1.1") or None if book not recognized.
    """
    osis_book = normalize_book_to_osis(book_name.lower())
    if osis_book is None:
        return None
    return f"{osis_book}.{chapter_num}.{verse_num}"


def answer_reference_question(
    question: str, verse_ref: str | None = None, translation_source: str = "KJV"
) -> ReferenceAnswerResult:
    """Answer a Bible reference question using verse context, Gematria, and LM synthesis.

    This function orchestrates the complete Phase-6P flow:
    1. Resolve verse context from bible_db (if verse_ref provided)
    2. Retrieve Gematria patterns (if verse text contains Hebrew)
    3. Optionally find similar verses using vector similarity
    4. Call LM Studio with guarded_lm_call (budget enforcement, provenance)
    5. Return structured result with trace and context

    Args:
        question: Natural-language question (e.g., "What does Genesis 1:1 mean?").
        verse_ref: Optional Bible reference (e.g., "Genesis 1:1", "Gen.1.1").
                   If not provided, LM will answer from general knowledge.
        translation_source: Translation identifier (default: "KJV").

    Returns:
        ReferenceAnswerResult with answer, trace, context_used, and lm_meta.

    Examples:
        >>> result = answer_reference_question("What does Genesis 1:1 mean?", "Genesis 1:1")
        >>> assert "answer" in result.answer
        >>> assert len(result.trace) > 0
        >>> assert "verse_refs" in result.context_used
    """
    trace: list[dict[str, Any]] = []
    context_used: dict[str, Any] = {
        "verse_refs": [],
        "gematria_values": [],
        "similar_verses": [],
    }
    verse_record: VerseRecord | None = None
    osis_ref: str | None = None

    # Step 1: Verse Context Resolution
    if verse_ref:
        trace_entry: dict[str, Any] = {
            "step": "verse_context",
            "verse_ref": verse_ref,
        }

        # Try to parse and fetch verse
        parsed = parse_reference(verse_ref)
        if parsed:
            book_name, chapter_num, verse_num = parsed
            adapter = BibleDbAdapter()
            verse_record = adapter.get_verse(book_name, chapter_num, verse_num, translation_source)
            db_status = adapter.db_status

            trace_entry["db_status"] = db_status
            trace_entry["result"] = {
                "found": verse_record is not None,
                "book": book_name,
                "chapter": chapter_num,
                "verse": verse_num,
            }

            if verse_record:
                # Convert to OSIS format for Gematria
                osis_ref = _reference_to_osis(book_name, chapter_num, verse_num)
                context_used["verse_refs"].append(osis_ref or verse_ref)
        else:
            trace_entry["db_status"] = "parse_failed"
            trace_entry["result"] = {"found": False, "error": "Could not parse reference"}

        trace.append(trace_entry)

    # Step 2: Gematria Pattern Retrieval
    gematria_summary = None
    if verse_record and verse_record.text and osis_ref:
        trace_entry = {
            "step": "gematria_patterns",
            "verse_text": verse_record.text[:100],  # Truncate for trace
        }

        # Check if text contains Hebrew characters
        has_hebrew = any("\u0590" <= char <= "\u05ff" for char in verse_record.text)

        if has_hebrew:
            try:
                gematria_summary = compute_verse_gematria(verse_record.text, osis_ref)
                gematria_values = [result.value for result in gematria_summary.systems.values()]
                context_used["gematria_values"] = gematria_values

                trace_entry["patterns_found"] = True
                trace_entry["result"] = {
                    "systems": list(gematria_summary.systems.keys()),
                    "values": gematria_values,
                }
            except Exception as e:
                trace_entry["patterns_found"] = False
                trace_entry["result"] = {"error": str(e)}
        else:
            trace_entry["patterns_found"] = False
            trace_entry["result"] = {"reason": "no_hebrew"}

        trace.append(trace_entry)

    # Step 3: Optional Vector Similarity
    similar_verses_list: list[Any] = []
    if verse_ref:
        trace_entry = {
            "step": "vector_similarity",
            "verse_ref": verse_ref,
        }

        try:
            similar_verses_list = similar_verses_for_reference(verse_ref, translation_source, limit=3)
            context_used["similar_verses"] = [
                f"{v.book_name} {v.chapter_num}:{v.verse_num}" for v in similar_verses_list
            ]

            trace_entry["snippets_count"] = len(similar_verses_list)
            trace_entry["result"] = {
                "found": len(similar_verses_list) > 0,
                "count": len(similar_verses_list),
            }
        except Exception as e:
            trace_entry["snippets_count"] = 0
            trace_entry["result"] = {"error": str(e)}

        trace.append(trace_entry)

    # Step 4: LM Studio Guarded Call
    trace_entry = {
        "step": "lm_synthesis",
    }

    # Build context for LM prompt
    context_parts: list[str] = []
    if verse_record:
        context_parts.append(f"Verse: {verse_record.book_name} {verse_record.chapter_num}:{verse_record.verse_num}")
        context_parts.append(f"Text: {verse_record.text}")

    if gematria_summary:
        gematria_info = ", ".join([f"{sys}: {result.value}" for sys, result in gematria_summary.systems.items()])
        context_parts.append(f"Gematria values: {gematria_info}")

    if similar_verses_list:
        similar_refs = ", ".join([f"{v.book_name} {v.chapter_num}:{v.verse_num}" for v in similar_verses_list[:3]])
        context_parts.append(f"Similar verses: {similar_refs}")

    context_text = "\n".join(context_parts) if context_parts else "No specific verse context provided."

    # Build LM messages
    system_message = """You are a Bible scholar assistant. Answer questions about biblical verses using the provided context.
Be concise, accurate, and cite the verse references when relevant."""
    user_message = f"""Context:
{context_text}

Question: {question}

Please provide a clear, concise answer based on the context above."""

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message},
    ]

    # Call guarded_lm_call with BibleScholar app identifier
    lm_result = guarded_lm_call(
        call_site="biblescholar.reference_slice",
        messages=messages,
        app_name="biblescholar",
        max_tokens=512,
        temperature=0.2,
    )

    # Extract LM metadata
    lm_meta: dict[str, Any] | None = None
    if lm_result.get("ok") and lm_result.get("response"):
        response = lm_result["response"]
        lm_meta = {
            "call_site": lm_result.get("call_site", "biblescholar.reference_slice"),
            "mode": lm_result.get("mode", "unknown"),
            "tokens_used": response.get("usage", {}).get("total_tokens", 0) if isinstance(response, dict) else 0,
            "latency_ms": response.get("latency_ms", 0) if isinstance(response, dict) else 0,
            "budget_status": "ok" if lm_result.get("mode") == "lm_on" else lm_result.get("mode", "unknown"),
        }

        # Extract answer from response
        if isinstance(response, dict):
            choices = response.get("choices", [])
            if choices and len(choices) > 0:
                answer = choices[0].get("message", {}).get("content", "")
            else:
                answer = str(response.get("content", ""))
        else:
            answer = str(response)
    else:
        # Fallback answer when LM is unavailable or budget exceeded
        mode = lm_result.get("mode", "unknown")
        reason = lm_result.get("reason", "unknown")
        if mode == "budget_exceeded":
            answer = "I'm unable to provide an answer at this time due to budget constraints. Please try again later."
        elif mode == "lm_off":
            answer = "LM Studio is currently disabled. I can provide basic information from the verse context, but cannot generate a detailed answer."
        else:
            answer = f"Unable to generate answer (mode: {mode}, reason: {reason})."

        lm_meta = {
            "call_site": lm_result.get("call_site", "biblescholar.reference_slice"),
            "mode": mode,
            "tokens_used": 0,
            "latency_ms": 0,
            "budget_status": mode,
        }

    trace_entry["result"] = {
        "ok": lm_result.get("ok", False),
        "mode": lm_result.get("mode", "unknown"),
    }
    trace_entry["provenance"] = lm_meta
    trace.append(trace_entry)

    return ReferenceAnswerResult(
        answer=answer,
        trace=trace,
        context_used=context_used,
        lm_meta=lm_meta,
    )
