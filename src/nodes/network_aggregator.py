import os
import uuid
from typing import Any, Dict, List
import psycopg
from pgvector.psycopg import register_vector
from src.services.lmstudio_client import get_lmstudio_client
from src.infra.structured_logger import get_logger, log_json

LOG = get_logger("gemantria.network_aggregator")

GEMATRIA_DSN = os.getenv("GEMATRIA_DSN")
VECTOR_DIM = int(os.getenv("VECTOR_DIM", "1024"))

class NetworkAggregationError(Exception):
    """Raised when network aggregation fails."""
    pass

def network_aggregator_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build semantic concept network from enriched nouns.

    Generates embeddings for each noun using lemma + insights, stores them
    in concept_network table, and computes pairwise similarities to create
    concept_relations with strong/weak linkage classification.
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
            "similarity_computations": 0
        }

        with psycopg.connect(GEMATRIA_DSN) as conn, conn.cursor() as cur:
            # Register pgvector
            register_vector(conn)

            # Process each noun: generate embedding and store in concept_network
            concept_ids = []
            for noun in nouns:
                noun_id = noun.get("noun_id", uuid.uuid4())

                # Create embedding text from lemma and insights
                lemma = noun.get("hebrew", "")
                insights = noun.get("insights", "")
                embedding_text = f"{lemma} {insights}".strip()

                if not embedding_text:
                    log_json(LOG, 30, "skipping_noun_no_text", noun_id=str(noun_id))
                    continue

                try:
                    # Generate embedding
                    embedding = client.generate_embedding(embedding_text)
                    network_summary["embeddings_generated"] += 1

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
                    concept_ids.append((noun_id, concept_network_id, embedding))

                    log_json(LOG, 20, "embedding_stored",
                            noun_id=str(noun_id),
                            network_id=str(concept_network_id))

                except Exception as e:
                    log_json(LOG, 30, "embedding_failed", noun_id=str(noun_id), error=str(e))
                    continue

            network_summary["total_nodes"] = len(concept_ids)

            # Compute pairwise similarities and create relations
            if len(concept_ids) >= 2:
                for i, (source_id, source_net_id, source_emb) in enumerate(concept_ids):
                    for j, (target_id, target_net_id, target_emb) in enumerate(concept_ids):
                        if i >= j:  # Skip self-comparisons and duplicates
                            continue

                        # Compute cosine similarity
                        similarity = _cosine_similarity(source_emb, target_emb)
                        network_summary["similarity_computations"] += 1

                        # Classify relation type
                        if similarity > 0.90:
                            relation_type = "strong"
                            network_summary["strong_edges"] += 1
                        elif similarity > 0.75:
                            relation_type = "weak"
                            network_summary["weak_edges"] += 1
                        else:
                            continue  # Skip low similarity relations

                        # Store relation (bidirectional)
                        cur.execute(
                            """INSERT INTO concept_relations
                               (source_id, target_id, similarity, relation_type)
                               VALUES (%s, %s, %s, %s)
                               ON CONFLICT (source_id, target_id) DO UPDATE SET
                               similarity = EXCLUDED.similarity,
                               relation_type = EXCLUDED.relation_type""",
                            (source_net_id, target_net_id, similarity, relation_type)
                        )

                        log_json(LOG, 20, "relation_created",
                                source=str(source_id),
                                target=str(target_id),
                                similarity=similarity,
                                type=relation_type)

            conn.commit()

        log_json(LOG, 20, "network_aggregation_complete",
                summary=network_summary)

        state["network_summary"] = network_summary
        return state

    except Exception as e:
        log_json(LOG, 40, "network_aggregation_failed", error=str(e))
        raise NetworkAggregationError(f"Network aggregation failed: {str(e)}")


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
