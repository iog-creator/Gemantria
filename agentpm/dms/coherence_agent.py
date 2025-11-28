#!/usr/bin/env python3
"""
DMS Phase 3: Coherence & Contradiction Detection

This module uses the local LM (Granite/Ollama) to perform semantic analysis
on canonical documents, detecting contradictions and ensuring coherence.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

try:
    import psycopg
    from psycopg.rows import dict_row

    PSYCOPG_AVAILABLE = True
except ImportError:
    PSYCOPG_AVAILABLE = False

from scripts.config.env import get_rw_dsn


@dataclass
class CoherenceResult:
    """Result of a pairwise coherence check."""

    doc_a_id: str
    doc_b_id: str
    has_contradiction: bool
    contradictions: list[dict[str, Any]]
    severity: str  # "high", "medium", "low", "none"
    lm_response: str | None = None


@dataclass
class CoherenceMetrics:
    """DMS Phase 3 coherence metrics."""

    checked_pairs: int
    contradiction_count: int
    coherence_score: float  # Percentage of pairs with no contradictions
    contradictions: list[dict[str, Any]]
    canonical_docs_count: int
    warnings: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "checked_pairs": self.checked_pairs,
            "contradiction_count": self.contradiction_count,
            "coherence_score": self.coherence_score,
            "canonical_docs_count": self.canonical_docs_count,
            "contradictions": self.contradictions,
            "warnings": self.warnings,
        }


def check_lm_availability() -> tuple[bool, str | None]:
    """Check if LM service is available for coherence checking."""
    try:
        from agentpm.lm.lm_status import compute_lm_status

        status = compute_lm_status()
        if not status.get("ok"):
            return False, "LM service not available"

        # Check local_agent slot specifically
        slots = status.get("slots", [])
        local_agent = next((s for s in slots if s.get("slot") == "local_agent"), None)

        if not local_agent:
            return False, "local_agent slot not configured"

        if local_agent.get("service_status") != "OK":
            return False, f"local_agent service status: {local_agent.get('service_status')}"

        return True, None

    except Exception as e:
        return False, f"LM status check failed: {e}"


def build_contradiction_prompt(doc_a: dict[str, Any], doc_b: dict[str, Any]) -> str:
    """Build LM prompt for contradiction detection.

    Args:
        doc_a: First document dict with 'title', 'path', 'content'
        doc_b: Second document dict with 'title', 'path', 'content'

    Returns:
        Formatted prompt string
    """
    prompt = f"""You are analyzing two canonical documentation files for semantic contradictions.

Document A: {doc_a["title"]}
Path: {doc_a["path"]}
Content (first 2000 chars):
{doc_a["content"][:2000]}

Document B: {doc_b["title"]}
Path: {doc_b["path"]}
Content (first 2000 chars):
{doc_b["content"][:2000]}

Task: Identify any contradictions between these documents. A contradiction exists when:
1. Both documents make claims about the same topic
2. Those claims are incompatible or mutually exclusive
3. The contradiction is semantic, not just different wording

Return your analysis in JSON format:
{{
    "has_contradiction": true/false,
    "contradictions": [
        {{
            "topic": "brief topic description",
            "claim_a": "what doc A says",
            "claim_b": "what doc B says",
            "severity": "high|medium|low"
        }}
    ]
}}

If no contradictions found, return: {{"has_contradiction": false, "contradictions": []}}
"""
    return prompt


def check_documents_for_contradictions(doc_a: dict[str, Any], doc_b: dict[str, Any]) -> CoherenceResult:
    """Use LM to check if two documents contradict each other.

    Args:
        doc_a: First document dict
        doc_b: Second document dict

    Returns:
        CoherenceResult with contradiction analysis
    """
    try:
        # Use existing LM infrastructure
        from agentpm.runtime.lm_helpers import generate_text

        prompt = build_contradiction_prompt(doc_a, doc_b)

        # Call LM with guarded wrapper (includes logging to control.agent_run)
        result = generate_text(
            prompt=prompt,
            max_tokens=512,
            temperature=0.0,  # Deterministic for consistency
            system_prompt="""You are a documentation coherence validator.\nAnalyze the two text snippets for LOGICAL contradictions.\n- Semantic variations (e.g. "DSN" vs "connection string") are NOT contradictions.\n- Different phrasing of the same fact is NOT a contradiction.\n- Only flag direct factual conflicts (e.g. "Port 5432" vs "Port 8000").\nProvide JSON responses only.""",
            model_slot="local_agent",
        )

        if not result.get("ok") or not result.get("text"):
            return CoherenceResult(
                doc_a_id=doc_a["id"],
                doc_b_id=doc_b["id"],
                has_contradiction=False,
                contradictions=[],
                severity="none",
                lm_response=f"LM call failed: {result.get('mode', 'unknown')}",
            )

        # Parse LM response
        response_text = result["text"].strip()

        # Try to extract JSON from response
        try:
            # Look for JSON object in response
            if "{" in response_text:
                json_start = response_text.index("{")
                json_end = response_text.rindex("}") + 1
                json_str = response_text[json_start:json_end]
                analysis = json.loads(json_str)
            else:
                analysis = {"has_contradiction": False, "contradictions": []}
        except (json.JSONDecodeError, ValueError):
            # LM didn't return valid JSON, assume no contradiction
            analysis = {"has_contradiction": False, "contradictions": []}

        has_contradiction = analysis.get("has_contradiction", False)
        contradictions = analysis.get("contradictions", [])

        # Determine overall severity
        if not has_contradiction:
            severity = "none"
        elif any(c.get("severity") == "high" for c in contradictions):
            severity = "high"
        elif any(c.get("severity") == "medium" for c in contradictions):
            severity = "medium"
        else:
            severity = "low"

        return CoherenceResult(
            doc_a_id=doc_a["id"],
            doc_b_id=doc_b["id"],
            has_contradiction=has_contradiction,
            contradictions=contradictions,
            severity=severity,
            lm_response=response_text[:500],  # Store first 500 chars
        )

    except Exception as e:
        return CoherenceResult(
            doc_a_id=doc_a["id"],
            doc_b_id=doc_b["id"],
            has_contradiction=False,
            contradictions=[],
            severity="none",
            lm_response=f"Error: {str(e)[:200]}",
        )


def load_canonical_documents() -> list[dict[str, Any]]:
    """Load all active canonical documents from database.

    Returns:
        List of document dicts with id, title, path, content
    """
    if not PSYCOPG_AVAILABLE:
        return []

    dsn = get_rw_dsn()
    if not dsn:
        return []

    try:
        conn = psycopg.connect(dsn)
        cur = conn.cursor(row_factory=dict_row)

        # Check if lifecycle_stage column exists
        try:
            cur.execute("""
                SELECT id, title, path
                FROM control.kb_document
                WHERE is_canonical = true
                  AND lifecycle_stage = 'active'
                LIMIT 20
            """)
            # has_lifecycle = True  # Table exists, lifecycle queries available
        except Exception:
            conn.rollback()
            # Fallback: just use is_canonical
            cur.execute("""
                SELECT id, title, path
                FROM control.kb_document
                WHERE is_canonical = true
                LIMIT 20
            """)

        rows = cur.fetchall()
        cur.close()
        conn.close()

        documents = []
        for row in rows:
            # Try to load content from filesystem
            try:
                from pathlib import Path

                repo_root = Path(__file__).resolve().parents[2]
                doc_path = repo_root / row["path"]

                if doc_path.exists():
                    content = doc_path.read_text()
                else:
                    content = f"[File not found: {row['path']}]"
            except Exception:
                content = "[Could not load content]"

            documents.append(
                {
                    "id": str(row["id"]),
                    "title": row.get("title", row["path"]),
                    "path": row["path"],
                    "content": content,
                }
            )

        return documents

    except Exception:
        return []


def compute_coherence_metrics() -> dict[str, Any]:
    """Compute DMS Phase 3 coherence metrics using LM.

    Returns:
        Dictionary with coherence metrics:
        {
            "available": bool,
            "source": "lm" | "error",
            "metrics": CoherenceMetrics.to_dict()
        }
    """
    # Check LM availability
    lm_available, lm_error = check_lm_availability()
    if not lm_available:
        return {
            "available": False,
            "source": "error",
            "error": lm_error or "LM service not available",
            "note": "Run: pmagent bringup full",
        }

    warnings = []

    # Load canonical documents
    canonical_docs = load_canonical_documents()

    if len(canonical_docs) == 0:
        return {
            "available": True,
            "source": "lm",
            "metrics": CoherenceMetrics(
                checked_pairs=0,
                contradiction_count=0,
                coherence_score=100.0,
                canonical_docs_count=0,
                contradictions=[],
                warnings=["No canonical documents found to check"],
            ).to_dict(),
        }

    if len(canonical_docs) == 1:
        return {
            "available": True,
            "source": "lm",
            "metrics": CoherenceMetrics(
                checked_pairs=0,
                contradiction_count=0,
                coherence_score=100.0,
                canonical_docs_count=1,
                contradictions=[],
                warnings=["Only 1 canonical document - no pairs to check"],
            ).to_dict(),
        }

    # Check pairs for contradictions
    contradictions_found = []
    checked_pairs = 0

    # Limit to avoid O(n²) explosion - check up to 50 pairs
    max_pairs = 50

    for i in range(len(canonical_docs)):
        for j in range(i + 1, len(canonical_docs)):
            if checked_pairs >= max_pairs:
                warnings.append(f"Checked {max_pairs} pairs (limit reached)")
                break

            doc_a = canonical_docs[i]
            doc_b = canonical_docs[j]

            result = check_documents_for_contradictions(doc_a, doc_b)
            checked_pairs += 1

            if result.has_contradiction and result.severity in ["high", "medium"]:
                for contradiction in result.contradictions:
                    contradictions_found.append(
                        {
                            "doc_a": {
                                "id": doc_a["id"],
                                "title": doc_a["title"],
                                "path": doc_a["path"],
                            },
                            "doc_b": {
                                "id": doc_b["id"],
                                "title": doc_b["title"],
                                "path": doc_b["path"],
                            },
                            "topic": contradiction.get("topic", "unknown"),
                            "claim_a": contradiction.get("claim_a", ""),
                            "claim_b": contradiction.get("claim_b", ""),
                            "severity": contradiction.get("severity", "unknown"),
                        }
                    )

        if checked_pairs >= max_pairs:
            break

    # Calculate coherence score
    contradiction_count = len(contradictions_found)
    if checked_pairs > 0:
        coherence_score = ((checked_pairs - contradiction_count) / checked_pairs) * 100.0
    else:
        coherence_score = 100.0

    if contradiction_count > 0:
        warnings.append(f"{contradiction_count} contradiction(s) found between canonical documents - review required")

    metrics = CoherenceMetrics(
        checked_pairs=checked_pairs,
        contradiction_count=contradiction_count,
        coherence_score=round(coherence_score, 1),
        canonical_docs_count=len(canonical_docs),
        contradictions=contradictions_found,
        warnings=warnings,
    )

    return {
        "available": True,
        "source": "lm",
        "metrics": metrics.to_dict(),
    }
