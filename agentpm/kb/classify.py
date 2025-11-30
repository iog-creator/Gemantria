"""
Fragment Classification Module

Purpose: Classify document fragments with AI-derived metadata for KB organization.

This module provides classify_fragment() which uses the local_agent LM slot
(not theology) to analyze document fragments and extract structured metadata.
"""

from __future__ import annotations

import json
from typing import Any

from agentpm.adapters.lm_studio import chat as lm_studio_chat


def classify_fragment(text: str, doc_path: str) -> dict[str, Any]:
    """
    Classify a document fragment with AI-derived metadata.

    Args:
        text: Fragment text content (e.g., a page from a PDF)
        doc_path: Document path (e.g., "docs/Technical Audit of Gemantria's PostgreSQL & AI Integration.pdf")

    Returns:
        Dictionary with classification fields:
        - subsystem: "pm" | "ops" | "biblescholar" | "gematria" | "webui" | "general"
        - doc_role: "architecture_blueprint" | "audit" | "tutorial" | "historical_log" | "reference" | "other"
        - importance: "core" | "supporting" | "nice_to_have"
        - phase_relevance: List of phase names (e.g., ["Phase 14", "Phase 15"])
        - should_archive: bool (True if document is historical/archival)
        - kb_candidate: bool (True if fragment should be included in KB)

    Notes:
        - Uses local_agent model slot (PM/ops model, not theology)
        - Returns empty dict if LM is unavailable (hermetic behavior)
        - All fields are optional; missing fields indicate uncertainty
    """
    system_prompt = """You are a document classification assistant for the Gemantria project.
Analyze document fragments and extract structured metadata for knowledge base organization.

Return ONLY valid JSON with these fields:
- subsystem: One of "pm", "ops", "biblescholar", "gematria", "webui", "general"
- doc_role: One of "architecture_blueprint", "audit", "tutorial", "historical_log", "reference", "other"
- importance: One of "core", "supporting", "nice_to_have"
- phase_relevance: Array of phase names (e.g., ["Phase 14", "Phase 15"]) or empty array
- should_archive: Boolean (true if historical/archival, false if current)
- kb_candidate: Boolean (true if fragment should be in knowledge base)

Return ONLY the JSON object, no markdown, no explanation."""

    user_prompt = f"""Classify this document fragment:

Document: {doc_path}

Fragment text:
{text[:2000]}  # Limit to first 2000 chars for context

Return JSON with: subsystem, doc_role, importance, phase_relevance, should_archive, kb_candidate."""

    try:
        # Use local_agent slot for PM/ops tasks (not theology)
        response = lm_studio_chat(
            user_prompt,
            model_slot="local_agent",
            system=system_prompt,
        )

        # Parse JSON response
        # Handle case where response might be wrapped in markdown code blocks
        response = response.strip()
        if response.startswith("```"):
            # Extract JSON from code block
            lines = response.split("\n")
            json_lines = []
            in_json = False
            for line in lines:
                if line.strip().startswith("```"):
                    if in_json:
                        break
                    in_json = True
                    continue
                if in_json:
                    json_lines.append(line)
            response = "\n".join(json_lines)

        # Parse JSON
        meta = json.loads(response)

        # Validate and normalize fields
        result: dict[str, Any] = {}

        # subsystem: must be one of allowed values
        if "subsystem" in meta:
            subsystem = meta["subsystem"].lower()
            if subsystem in ["pm", "ops", "biblescholar", "gematria", "webui", "general"]:
                result["subsystem"] = subsystem

        # doc_role: must be one of allowed values
        if "doc_role" in meta:
            doc_role = meta["doc_role"].lower()
            allowed_roles = [
                "architecture_blueprint",
                "audit",
                "tutorial",
                "historical_log",
                "reference",
                "other",
            ]
            if doc_role in allowed_roles:
                result["doc_role"] = doc_role

        # importance: must be one of allowed values
        if "importance" in meta:
            importance = meta["importance"].lower()
            if importance in ["core", "supporting", "nice_to_have"]:
                result["importance"] = importance

        # phase_relevance: must be array of strings
        if "phase_relevance" in meta:
            if isinstance(meta["phase_relevance"], list):
                result["phase_relevance"] = [str(p) for p in meta["phase_relevance"] if isinstance(p, (str, int))]

        # should_archive: must be boolean
        if "should_archive" in meta:
            result["should_archive"] = bool(meta["should_archive"])

        # kb_candidate: must be boolean
        if "kb_candidate" in meta:
            result["kb_candidate"] = bool(meta["kb_candidate"])

        return result

    except Exception:
        # Hermetic behavior: return empty dict if LM is unavailable or parsing fails
        return {}
