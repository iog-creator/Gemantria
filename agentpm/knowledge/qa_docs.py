#!/usr/bin/env python3
"""
Document Q&A Module

E2E Pipeline (Reality Check #1): Answer questions using SSOT docs via LM Studio guarded calls.
"""

from __future__ import annotations

from typing import Any

from agentpm.knowledge.retrieval import retrieve_doc_sections
from agentpm.runtime.lm_logging import guarded_lm_call


def answer_doc_question(question: str) -> dict[str, Any]:
    """
    Answer a question using SSOT documentation via LM Studio.

    Args:
        question: User question string

    Returns:
        Dictionary with:
        - answer: str | None (answer text if ok)
        - sources: list[str] (section IDs used)
        - lm_meta: dict | None (LM metadata if available)
        - mode: str (lm_on, lm_off, fallback, budget_exceeded, db_off)
        - ok: bool (True if answer generated)
    """
    # Retrieve matching doc sections
    sections = retrieve_doc_sections(question, limit=5)

    # Prepare context from sections
    context_parts: list[str] = []
    source_ids: list[str] = []

    for section in sections:
        source_ids.append(section["id"])
        section_title = section.get("section_title") or "Untitled Section"
        section_body = section.get("body", "")[:500]  # Limit excerpt length
        context_parts.append(f"- {section_title}\n  {section_body}")

    context_text = (
        "\n\n".join(context_parts) if context_parts else "No relevant documentation found."
    )

    # Prepare LM messages
    system_prompt = "Answer strictly using the provided project documentation. If the documentation does not contain relevant information, say so clearly."
    user_prompt = f"""QUESTION: {question}

CONTEXT:
{context_text}

Please provide a concise answer based on the context above."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    # Call LM Studio via guarded_lm_call
    result = guarded_lm_call(
        call_site="knowledge.qa_docs.answer_doc_question",
        messages=messages,
        temperature=0.0,
        max_tokens=2000,  # Strict budget: <= 2000 tokens
        app_name="gemantria.knowledge",
    )

    # Extract answer from response
    answer = None
    lm_meta = None

    if result.get("ok") and result.get("response"):
        response = result["response"]
        # Extract text from response (handle different response formats)
        if isinstance(response, dict):
            if "choices" in response and len(response["choices"]) > 0:
                answer = response["choices"][0].get("message", {}).get("content", "")
            elif "text" in response:
                answer = response["text"]
            elif "content" in response:
                answer = response["content"]
            # Extract LM metadata
            lm_meta = {
                "usage": response.get("usage"),
                "model": response.get("model"),
                "call_site": result.get("call_site"),
            }
        elif isinstance(response, str):
            answer = response

    # Determine mode
    mode = result.get("mode", "unknown")
    if not sections:
        mode = "db_off"  # No sections found (DB unavailable or no matches)

    return {
        "answer": answer,
        "sources": source_ids,
        "lm_meta": lm_meta,
        "mode": mode,
        "ok": result.get("ok", False) and answer is not None,
    }
