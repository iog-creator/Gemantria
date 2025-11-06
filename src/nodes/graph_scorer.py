"""
Graph scoring node for SSOT edge strength calculation and classification.

Applies cosine + rerank blend with SSOT thresholds to classify edges as
strong (≥0.90), weak (≥0.75), or candidate.

Related Rules: Rule-045 (Rerank Blend SSOT), Rule-039 (Execution Contract)
Related ADRs: ADR-015 (Semantic Reranking), ADR-019 (Data Contracts)
"""

from __future__ import annotations

import os
from typing import Any

import psycopg
from src.infra.structured_logger import get_logger, log_json

LOG = get_logger("gematria.graph_scorer")

# SSOT thresholds
EDGE_STRONG = float(os.getenv("EDGE_STRONG", "0.90"))
EDGE_WEAK = float(os.getenv("EDGE_WEAK", "0.75"))
EDGE_ALPHA = float(os.getenv("EDGE_ALPHA", "0.5"))

# Validate thresholds
if not (0.0 <= EDGE_ALPHA <= 1.0):
    raise ValueError(f"EDGE_ALPHA_OUT_OF_RANGE: {EDGE_ALPHA}")
if not (0.0 <= EDGE_WEAK <= EDGE_STRONG <= 1.0):
    raise ValueError(f"Invalid edge thresholds: weak={EDGE_WEAK}, strong={EDGE_STRONG}")


def compute_edge_strength(cosine: float, rerank_score: float) -> float:
    """
    Compute edge strength using SSOT blend formula: α*cosine + (1-α)*rerank_score.

    Args:
        cosine: Cosine similarity score [0,1]
        rerank_score: Reranker score [0,1]

    Returns:
        Edge strength [0,1]
    """
    return EDGE_ALPHA * float(cosine) + (1.0 - EDGE_ALPHA) * float(rerank_score)


def classify_edge(edge_strength: float) -> str:
    """
    Classify edge based on SSOT thresholds.

    Args:
        edge_strength: Computed edge strength [0,1]

    Returns:
        Classification: 'strong', 'weak', or 'candidate'
    """
    if edge_strength >= EDGE_STRONG:
        return "strong"
    elif edge_strength >= EDGE_WEAK:
        return "weak"
    else:
        return "candidate"


def graph_scorer_node(state: dict[str, Any]) -> dict[str, Any]:
    """
    Score all edges in the graph using SSOT blend formula and classify them.

    Updates concept_relations table with edge_strength and class columns.
    Emits counts to share/eval/edges/edge_class_counts.json.

    Args:
        state: Pipeline state with run_id

    Returns:
        Updated state with scoring results
    """
    run_id = state.get("run_id", "")
    dsn = os.getenv("GEMATRIA_DSN")
    if not dsn:
        log_json(LOG, 30, "graph_scorer_skipped", reason="no_dsn")
        return state

    log_json(LOG, 20, "graph_scorer_start", run_id=run_id, alpha=EDGE_ALPHA)

    try:
        with psycopg.connect(dsn) as conn, conn.cursor() as cur:
            # Get all edges that need scoring (have cosine and/or rerank_score but missing edge_strength/class)
            cur.execute(
                """
                SELECT source_id, target_id, COALESCE(cosine, 0.0) as cosine,
                       COALESCE(rerank_score, 0.0) as rerank_score,
                       COALESCE(edge_strength, 0.0) as current_edge_strength
                FROM concept_relations
                WHERE cosine IS NOT NULL OR rerank_score IS NOT NULL
                """
            )

            edges = cur.fetchall()
            scored_count = 0
            strong_count = 0
            weak_count = 0
            candidate_count = 0

            for source_id, target_id, cosine, rerank_score, current_edge_strength in edges:
                # Compute edge strength using SSOT blend
                edge_strength = compute_edge_strength(cosine, rerank_score)
                edge_class = classify_edge(edge_strength)

                # Update edge with computed strength and class
                cur.execute(
                    """
                    UPDATE concept_relations
                    SET edge_strength = %s,
                        class = %s
                    WHERE source_id = %s AND target_id = %s
                    """,
                    (edge_strength, edge_class, source_id, target_id),
                )

                scored_count += 1
                if edge_class == "strong":
                    strong_count += 1
                elif edge_class == "weak":
                    weak_count += 1
                else:
                    candidate_count += 1

            conn.commit()

            # Emit counts to share/eval/edges/edge_class_counts.json
            import json
            from pathlib import Path

            counts = {
                "total_edges": scored_count,
                "strong_edges": strong_count,
                "weak_edges": weak_count,
                "candidate_edges": candidate_count,
                "alpha": EDGE_ALPHA,
                "thresholds": {"strong": EDGE_STRONG, "weak": EDGE_WEAK},
            }

            output_dir = Path("share/eval/edges")
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / "edge_class_counts.json"
            output_file.write_text(json.dumps(counts, indent=2), encoding="utf-8")

            log_json(
                LOG,
                20,
                "graph_scorer_complete",
                run_id=run_id,
                scored=scored_count,
                strong=strong_count,
                weak=weak_count,
                candidate=candidate_count,
            )

            state["graph_scoring"] = {
                "scored_edges": scored_count,
                "strong_edges": strong_count,
                "weak_edges": weak_count,
                "candidate_edges": candidate_count,
            }

            return state

    except Exception as e:
        log_json(LOG, 40, "graph_scorer_error", error=str(e))
        state["graph_scoring_error"] = str(e)
        return state
