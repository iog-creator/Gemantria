import os
import uuid
import time
import math
from typing import Any, Dict, List, Tuple
import psycopg
from pgvector.psycopg import register_vector
from src.services.lmstudio_client import get_lmstudio_client
from src.infra.structured_logger import get_logger, log_json

LOG = get_logger("gemantria.network_aggregator")

GEMATRIA_DSN = os.getenv("GEMATRIA_DSN")
VECTOR_DIM = int(os.getenv("VECTOR_DIM", "1024"))

# Rerank configuration
NN_TOPK = int(os.getenv("NN_TOPK", "20"))
RERANK_MIN = float(os.getenv("RERANK_MIN", "0.50"))
EDGE_STRONG = float(os.getenv("EDGE_STRONG", "0.90"))
EDGE_WEAK = float(os.getenv("EDGE_WEAK", "0.75"))


def _l2_normalize(vec: List[float]) -> List[float]:
    """L2 normalize a vector to unit length."""
    norm = math.sqrt(sum(x*x for x in vec)) or 1.0
    return [x / norm for x in vec]

class NetworkAggregationError(Exception):
    """Raised when network aggregation fails."""
    pass

def network_aggregator_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build semantic concept network from enriched nouns using rerank-driven relationships.

    Generates embeddings for each noun, then uses pgvector KNN + Qwen reranker
    to create precise theological relationships with rerank evidence.
    """
    nouns = state.get("enriched_nouns", [])
    run_id = state.get("run_id", uuid.uuid4())

    if not nouns:
        log_json(LOG, 20, "network_aggregation_skipped", reason="no_nouns")
        return state

    log_json(LOG, 20, "network_aggregation_start", noun_count=len(nouns))

    try:
        client = get_lmstudio_client()
        network_summary = {
            "total_nodes": 0,
            "strong_edges": 0,
            "weak_edges": 0,
            "embeddings_generated": 0,
            "similarity_computations": 0,
            "rerank_calls": 0,
            "avg_edge_strength": 0.0,
            "rerank_yes_ratio": 0.0
        }

        with psycopg.connect(GEMATRIA_DSN) as conn, conn.cursor() as cur:
            # Register pgvector
            register_vector(conn)

            # Process nouns: generate embeddings and store in concept_network
            # Use transaction context for auto-commit enforcement
            with conn.transaction():
                concept_data = _generate_and_store_embeddings(client, cur, nouns, network_summary)

                if not concept_data:
                    log_json(LOG, 30, "no_valid_embeddings_generated")
                    return state

                network_summary["total_nodes"] = len(concept_data)

                # Build rerank-driven relationships using KNN + reranker
                if len(concept_data) >= 2:
                    _build_rerank_relationships(client, cur, concept_data, network_summary)

                # Transaction commits automatically on successful exit

        log_json(LOG, 20, "network_aggregation_complete", summary=network_summary)

        state["network_summary"] = network_summary
        return state

    except Exception as e:
        log_json(LOG, 40, "network_aggregation_failed", error=str(e))
        raise NetworkAggregationError(f"Network aggregation failed: {str(e)}")


def _generate_and_store_embeddings(client, cur, nouns: List[Dict], summary: Dict) -> List[Tuple]:
    """
    Generate embeddings for nouns and store them in concept_network table.
    Returns list of (noun_id, network_id, embedding, doc_string) tuples.
    """
    embedding_texts = []
    valid_nouns = []

    for noun in nouns:
        doc_string = _build_document_string(noun)
        if not doc_string:
            log_json(LOG, 30, "skipping_noun_incomplete_data", noun_name=noun.get("name"))
            continue

        embedding_texts.append(doc_string)
        valid_nouns.append(noun)

    if not embedding_texts:
        return []

    # Batch process embeddings
    concept_data = []
    batch_size = 16

    for i in range(0, len(embedding_texts), batch_size):
        batch_texts = embedding_texts[i:i+batch_size]
        batch_nouns = valid_nouns[i:i+batch_size]

        try:
            batch_embeddings = client.get_embeddings(batch_texts)
            summary["embeddings_generated"] += len(batch_embeddings)

            # Runtime dimension guard and normalization
            for i, embedding in enumerate(batch_embeddings):
                if len(embedding) != VECTOR_DIM:
                    raise RuntimeError(
                        f"Embedding dimension mismatch: expected {VECTOR_DIM}, got {len(embedding)} "
                        f"(candidate index {i} in batch). Fix by aligning VECTOR_DIM and column type."
                    )
            # L2 normalize all embeddings
            batch_embeddings = [_l2_normalize(vec) for vec in batch_embeddings]

            # Debug log once per batch
            log_json(LOG, 20, "concept_network_upsert_batch",
                    batch_size=len(batch_embeddings),
                    vector_dim=VECTOR_DIM)

            for noun, embedding, doc_text in zip(batch_nouns, batch_embeddings, batch_texts):
                noun_id = noun.get("noun_id", uuid.uuid4())

                # Store in concept_network
                cur.execute(
                    """INSERT INTO concept_network (concept_id, embedding)
                       VALUES (%s, %s)
                       ON CONFLICT (concept_id) DO UPDATE SET
                       embedding = EXCLUDED.embedding,
                       created_at = now()
                       RETURNING id""",
                    (noun_id, embedding)
                )
                concept_network_id = cur.fetchone()[0]
                concept_data.append((noun_id, concept_network_id, embedding, doc_text))

                log_json(LOG, 20, "embedding_stored",
                        noun_id=str(noun_id),
                        noun_name=noun.get("name"),
                        network_id=str(concept_network_id))

        except Exception as e:
            log_json(LOG, 30, "batch_embedding_failed",
                    batch_start=i, batch_size=len(batch_texts), error=str(e))
            continue

    return concept_data


def _build_document_string(noun: Dict[str, Any]) -> str:
    """Build standardized document string for embedding/reranking."""
    name = noun.get("name", "")
    hebrew = noun.get("hebrew", "")
    primary_verse = noun.get("primary_verse", "")
    value = noun.get("value", "")
    insight = noun.get("insight", "")

    # Use placeholder if primary_verse not available
    if not primary_verse:
        primary_verse = "Genesis (reference)"

    return f"""Document: {name}
Meaning: {hebrew}
Primary Verse: {primary_verse}
Gematria: {value}
Insight: {insight}""".strip()


def _build_rerank_relationships(client, cur, concept_data: List[Tuple], summary: Dict):
    """Build relationships using KNN recall + reranker precision."""
    total_edge_strength = 0.0
    total_yes_scores = 0
    total_rerank_calls = 0

    # Process each concept as a potential source
    for source_id, source_net_id, source_emb, source_doc in concept_data:
        # Get KNN neighbors using pgvector
        neighbors = _get_knn_neighbors(cur, source_net_id, NN_TOPK)

        if not neighbors:
            continue

        # Build candidate documents (excluding self)
        candidates = []
        neighbor_data = []

        for neighbor_net_id, neighbor_cosine in neighbors:
            if neighbor_net_id == source_net_id:
                continue

            # Find the neighbor's data
            for n_id, n_net_id, n_emb, n_doc in concept_data:
                if n_net_id == neighbor_net_id:
                    candidates.append(n_doc)
                    neighbor_data.append((n_id, n_net_id, neighbor_cosine, n_emb))
                    break

        if not candidates:
            continue

        # Rerank candidates using Qwen reranker
        start_time = time.time()
        rerank_scores = client.rerank(source_doc, candidates)
        rerank_latency_ms = (time.time() - start_time) * 1000

        summary["rerank_calls"] += len(rerank_scores)
        total_rerank_calls += len(rerank_scores)

        # Count yes responses for metrics
        yes_count = sum(1 for score in rerank_scores if score >= 0.5)
        total_yes_scores += yes_count

        # Log rerank batch metrics
        log_json(LOG, 20, "rerank_batch",
                model=os.getenv("QWEN_RERANKER_MODEL", "qwen-reranker"),
                k=len(candidates),
                kept=sum(1 for score in rerank_scores if score >= RERANK_MIN),
                yes_ratio=yes_count / len(rerank_scores) if rerank_scores else 0,
                lat_ms=round(rerank_latency_ms, 1))

        # Process rerank results and create edges
        for (target_id, target_net_id, cosine_sim, target_emb), rerank_score in zip(neighbor_data, rerank_scores):
            # Filter by rerank threshold
            if rerank_score < RERANK_MIN:
                continue

            # Compute edge strength: 0.5 * cosine + 0.5 * rerank_score
            edge_strength = 0.5 * cosine_sim + 0.5 * rerank_score
            total_edge_strength += edge_strength

            # Classify edge type
            if edge_strength >= EDGE_STRONG:
                relation_type = "strong"
                summary["strong_edges"] += 1
            elif edge_strength >= EDGE_WEAK:
                relation_type = "weak"
                summary["weak_edges"] += 1
            else:
                continue  # Skip edges below weak threshold

            # Store relationship with rerank evidence
            rerank_model = os.getenv("QWEN_RERANKER_MODEL", "qwen-reranker")
            cur.execute(
                """INSERT INTO concept_relations
                   (source_id, target_id, similarity, relation_type, cosine, rerank_score, edge_strength, rerank_model)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                   ON CONFLICT (source_id, target_id) DO UPDATE SET
                   similarity = EXCLUDED.similarity,
                   relation_type = EXCLUDED.relation_type,
                   cosine = EXCLUDED.cosine,
                   rerank_score = EXCLUDED.rerank_score,
                   edge_strength = EXCLUDED.edge_strength,
                   rerank_model = EXCLUDED.rerank_model,
                   rerank_at = now()""",
                (source_net_id, target_net_id, cosine_sim, relation_type,
                 cosine_sim, rerank_score, edge_strength, rerank_model)
            )

            log_json(LOG, 20, "relation_created",
                    source=str(source_id),
                    target=str(target_id),
                    cosine=round(cosine_sim, 4),
                    rerank_score=round(rerank_score, 4),
                    edge_strength=round(edge_strength, 4),
                    type=relation_type)

    # Update summary metrics
    if summary["strong_edges"] + summary["weak_edges"] > 0:
        summary["avg_edge_strength"] = total_edge_strength / (summary["strong_edges"] + summary["weak_edges"])

    if total_rerank_calls > 0:
        summary["rerank_yes_ratio"] = total_yes_scores / total_rerank_calls


def _get_knn_neighbors(cur, source_net_id: uuid.UUID, top_k: int) -> List[Tuple[uuid.UUID, float]]:
    """Get KNN neighbors using pgvector cosine similarity."""
    cur.execute(
        """SELECT id, 1 - (embedding <=> (SELECT embedding FROM concept_network WHERE id = %s)) as cosine
           FROM concept_network
           WHERE id != %s
           ORDER BY embedding <=> (SELECT embedding FROM concept_network WHERE id = %s)
           LIMIT %s""",
        (source_net_id, source_net_id, source_net_id, top_k)
    )

    return [(row[0], float(row[1])) for row in cur.fetchall()]


def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    import math

    if len(vec1) != len(vec2):
        raise ValueError("Vectors must have same length")

    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return dot_product / (norm1 * norm2)
