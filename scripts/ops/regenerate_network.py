#!/usr/bin/env python3
"""
Regenerate concept_network from the concepts table.
This replaces the orphaned/anonymous nodes with fully identified nodes derived from the canonical concepts table.
"""

import os
import sys
import uuid
import psycopg
from typing import Dict, Any

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.infra.env_loader import ensure_env_loaded
from src.infra.db_utils import get_connection_dsn
from src.services.lmstudio_client import get_lmstudio_client

ensure_env_loaded()


def build_document_string(concept: Dict[str, Any]) -> str:
    """Build standardized document string for embedding."""
    # Format similar to network_aggregator but using concept data
    return (
        f"Concept Name: {concept['name']}\n"
        f"Hebrew Text: {concept['hebrew_text']}\n"
        f"Gematria: {concept['gematria_value']}\n"
        f"Primary Verse: {concept['primary_verse']}\n"
        f"Book: {concept['book_source']}\n"
        f"Meaning: {concept['english_meaning']}\n"
        f"Insights: {concept['insights']}"
    )


import numpy as np


def regenerate_network():
    dsn = get_connection_dsn("GEMATRIA_DSN")
    client = get_lmstudio_client()

    print("Connecting to DB...")
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            # 1. Fetch all concepts
            print("Fetching concepts...")
            cur.execute("""
                SELECT id, name, hebrew_text, gematria_value, book_source, primary_verse, english_meaning, insights
                FROM concepts
            """)
            rows = cur.fetchall()
            print(f"Found {len(rows)} concepts to embed.")

            concepts = []
            for r in rows:
                concepts.append(
                    {
                        "id": r[0],
                        "name": r[1],
                        "hebrew_text": r[2],
                        "gematria_value": r[3],
                        "book_source": r[4],
                        "primary_verse": r[5],
                        "english_meaning": r[6],
                        "insights": r[7] or "",
                    }
                )

            # 2. Generate Embeddings (Batch)
            batch_size = 50
            total_processed = 0

            # Prepare to clear old data
            print(
                "🔥🔥🔥 LOUD HINT [ops.regenerate_truncation]: Regeneration TRUNCATES concept_network. Ensure canonical data is backed up. 🔥🔥🔥",
                file=sys.stderr,
            )
            print("Clearing orphaned network data...")
            cur.execute("TRUNCATE TABLE concept_network CASCADE")
            cur.execute("TRUNCATE TABLE concept_metadata CASCADE")
            cur.execute("TRUNCATE TABLE concept_clusters CASCADE")
            cur.execute("TRUNCATE TABLE concept_centrality CASCADE")
            cur.execute("TRUNCATE TABLE concept_relations CASCADE")

            print("Regenerating network nodes...")

            for i in range(0, len(concepts), batch_size):
                batch = concepts[i : i + batch_size]
                texts = [build_document_string(c) for c in batch]

                try:
                    embeddings = client.get_embeddings(texts)
                except Exception as e:
                    print(f"Error generating embeddings for batch {i}: {e}")
                    continue

                # Insert into DB
                for concept, embedding in zip(batch, embeddings):
                    node_uuid = uuid.uuid4()

                    # Insert into concept_network
                    cur.execute(
                        """
                        INSERT INTO concept_network (id, concept_id, embedding)
                        VALUES (%s, %s, %s)
                    """,
                        (node_uuid, node_uuid, embedding),
                    )

                    # Insert into concept_metadata
                    source_tag = f"bible_db:concept_id:{concept['id']}"

                    cur.execute(
                        """
                        INSERT INTO concept_metadata (concept_id, label, description, source)
                        VALUES (%s, %s, %s, %s)
                    """,
                        (
                            node_uuid,
                            concept["name"],
                            f"Hebrew: {concept['hebrew_text']} ({concept['gematria_value']})",
                            source_tag,
                        ),
                    )

                total_processed += len(batch)
                print(f"Processed {total_processed}/{len(concepts)} nodes...")

            # 3. Generate Edges
            print("Generating edges...")
            cur.execute("SELECT id, embedding FROM concept_network")
            rows = cur.fetchall()

            if not rows:
                print("No nodes found, skipping edge generation.")
                return

            ids = [r[0] for r in rows]
            # Convert string vector to list if needed, but psycopg adapts pgvector to list/numpy
            # Assuming psycopg returns list or numpy array for vector column
            embeddings = np.array([np.array(r[1]) for r in rows])

            # Normalize
            norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
            # Avoid divide by zero
            norms[norms == 0] = 1.0
            embeddings = embeddings / norms

            # Compute Similarity
            print("Computing similarity matrix...")
            sim_matrix = np.dot(embeddings, embeddings.T)

            # Threshold
            threshold = 0.75
            print(f"Filtering edges > {threshold}...")
            r_indices, c_indices = np.where(sim_matrix > threshold)

            edges_count = 0
            batch_edges = []

            for r, c in zip(r_indices, c_indices):
                if r < c:  # Unique pairs
                    batch_edges.append((ids[r], ids[c], float(sim_matrix[r, c])))
                    if len(batch_edges) >= 1000:
                        cur.executemany(
                            """
                            INSERT INTO concept_relations (source_id, target_id, cosine)
                            VALUES (%s, %s, %s)
                        """,
                            batch_edges,
                        )
                        edges_count += len(batch_edges)
                        batch_edges = []

            if batch_edges:
                cur.executemany(
                    """
                    INSERT INTO concept_relations (source_id, target_id, cosine)
                    VALUES (%s, %s, %s)
                """,
                    batch_edges,
                )
                edges_count += len(batch_edges)

            print(f"Generated {edges_count} edges.")

        conn.commit()
        print("Network regeneration complete.")


if __name__ == "__main__":
    regenerate_network()
