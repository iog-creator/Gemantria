#!/usr/bin/env python3
"""
Backfill BGE-M3 embeddings for existing concept network nodes.

This script reads existing concepts with Qwen3 embeddings and generates
corresponding BGE-M3 embeddings, storing them in the embedding_bge_m3 column.
"""

import os
import sys
from pathlib import Path

# Add src to path
script_dir = Path(__file__).parent
project_root = script_dir.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

import psycopg
from pgvector.psycopg import register_vector

from src.infra.env_loader import ensure_env_loaded
from src.services.lmstudio_client import get_lmstudio_client

# Load environment
ensure_env_loaded()


def backfill_bge_embeddings():
    """Backfill BGE-M3 embeddings for nodes that have Qwen3 embeddings."""

    dsn = os.getenv("GEMATRIA_DSN")
    if not dsn:
        raise RuntimeError("GEMATRIA_DSN not set")

    # Use direct psycopg connection like the network aggregator
    with psycopg.connect(dsn) as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            # Find nodes with Qwen3 embeddings but no BGE-M3 embeddings
            cur.execute(
                """
                SELECT cn.id, 'Concept_' || cn.id::text, 'hebrew_placeholder', 'reference_placeholder', 1
                FROM concept_network cn
                WHERE cn.embedding IS NOT NULL
                AND cn.embedding_bge_m3 IS NULL
                ORDER BY cn.created_at DESC
            """
            )
            rows = cur.fetchall()

            if not rows:
                print("No nodes found that need BGE-M3 backfilling.")
                return

            print(f"Found {len(rows)} nodes to backfill with BGE-M3 embeddings.")

            # Get LM Studio client for BGE-M3 embeddings
            client = get_lmstudio_client()

            # Process in batches
            batch_size = 8
            total_processed = 0

            for i in range(0, len(rows), batch_size):
                batch = rows[i : i + batch_size]
                print(f"Processing batch {i // batch_size + 1}/{(len(rows) + batch_size - 1) // batch_size}...")

                # Prepare documents for embedding
                documents = []
                network_ids = []

                for row in batch:
                    (
                        network_id,
                        name,
                        hebrew_text,
                        primary_verse,
                        verse_occurrence_count,
                    ) = row

                    # Build document string (same format as used for Qwen3)
                    doc = f"""Concept: {name}
Hebrew: {hebrew_text}
Reference: {primary_verse}
Frequency: {verse_occurrence_count} occurrences"""

                    documents.append(doc)
                    network_ids.append(network_id)

                # Generate BGE-M3 embeddings
                try:
                    bge_embeddings = client.get_embeddings(documents, model="text-embedding-bge-m3")
                    print(f"Generated {len(bge_embeddings)} BGE-M3 embeddings")

                    # Update database
                    for network_id, bge_embedding in zip(network_ids, bge_embeddings, strict=False):
                        # BGE embeddings are already lists
                        embedding_list = bge_embedding

                        cur.execute(
                            """
                            UPDATE concept_network
                            SET embedding_bge_m3 = %s
                            WHERE id = %s
                        """,
                            (embedding_list, network_id),
                        )

                    total_processed += len(batch)
                    print(f"Updated {total_processed}/{len(rows)} nodes with BGE-M3 embeddings")

                    # Immediate verification for this batch
                    cur.execute(
                        """
                        SELECT COUNT(*) FROM concept_network
                        WHERE embedding_bge_m3 IS NOT NULL
                    """
                    )
                    batch_check = cur.fetchone()[0]
                    print(f"Current BGE embeddings in DB: {batch_check}")

                except Exception as e:
                    print(f"Error processing batch: {e}")
                    continue

            print("BGE-M3 backfill completed!")
            print(f"Total nodes processed: {total_processed}")

            # Final verification
            cur.execute(
                """
                SELECT COUNT(*) FROM concept_network
                WHERE embedding IS NOT NULL AND embedding_bge_m3 IS NOT NULL
            """
            )
            final_count = cur.fetchone()[0]

            print(f"Nodes with both embeddings: {final_count}")

        # Transaction commits here when connection context exits


if __name__ == "__main__":
    backfill_bge_embeddings()
