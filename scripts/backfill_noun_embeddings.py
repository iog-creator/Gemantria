# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
"""
Backfill embeddings for gematria.nouns table using LM Studio.

Usage:
    python3 scripts/backfill_noun_embeddings.py \
      --dsn "$GEMATRIA_DSN" \
      --lmstudio "$LMSTUDIO_BASE" \
      --model "$EMB_MODEL_NAME" \
      --dim 1024 \
      --batch 512

This creates gematria.noun_embeddings table and populates it with vectors.
"""

# All imports must be at the very top
import os
import sys
import time
import argparse
from pathlib import Path

import psycopg
from pgvector.psycopg import register_vector

from src.infra.env_loader import ensure_env_loaded
from src.services.lmstudio_client import get_lmstudio_client

# Add src to path after all imports
script_dir = Path(__file__).parent
project_root = script_dir.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))


def backfill_noun_embeddings(
    dsn: str,
    lmstudio_base: str,
    model_name: str,
    dim: int,
    batch_size: int,
    sleep_sec: float,
    where_clause: str = "",
):
    """Backfill embeddings for nouns that don't have them yet."""

    # Ensure env loaded for LM Studio client
    ensure_env_loaded()

    # Override LM Studio base URL if provided
    if lmstudio_base:
        os.environ["LM_STUDIO_HOST"] = lmstudio_base

    with psycopg.connect(dsn) as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            # Create embeddings table if it doesn't exist
            cur.execute(f"""
                CREATE SCHEMA IF NOT EXISTS gematria;

                CREATE TABLE IF NOT EXISTS gematria.noun_embeddings (
                    noun_id       BIGINT PRIMARY KEY REFERENCES gematria.nouns(id) ON DELETE CASCADE,
                    embedding     vector({dim}) NOT NULL,
                    model         TEXT NOT NULL,
                    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
                );
            """)

            # Create vector index
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_noun_embeddings_vec
                    ON gematria.noun_embeddings USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);
            """)

            # Find nouns without embeddings
            query = """
                SELECT n.id, n.lemma, n.surface, n.book, n.chapter, n.verse
                FROM gematria.nouns n
                LEFT JOIN gematria.noun_embeddings ne ON n.id = ne.noun_id
                WHERE ne.noun_id IS NULL
            """
            if where_clause:
                query += f" AND ({where_clause})"

            query += " ORDER BY n.id"

            cur.execute(query)
            rows = cur.fetchall()

            if not rows:
                print("No nouns found that need embeddings.")
                return

            print(f"Found {len(rows)} nouns to embed with model '{model_name}' (dim={dim})")

            # Get LM Studio client
            client = get_lmstudio_client()

            # Process in batches
            total_processed = 0
            total_batches = (len(rows) + batch_size - 1) // batch_size

            for i in range(0, len(rows), batch_size):
                batch = rows[i : i + batch_size]
                batch_num = i // batch_size + 1
                print(f"Processing batch {batch_num}/{total_batches} ({len(batch)} nouns)...")

                # Prepare documents for embedding
                documents = []
                noun_ids = []

                for row in batch:
                    noun_id, lemma, surface, book, chapter, verse = row

                    # Build document string for embedding
                    doc = f"Lemma: {lemma} | Surface: {surface} | Reference: {book} {chapter}:{verse}"
                    documents.append(doc)
                    noun_ids.append(noun_id)

                # Generate embeddings
                try:
                    embeddings = client.get_embeddings(documents, model=model_name)

                    if len(embeddings) != len(documents):
                        print(f"Warning: Got {len(embeddings)} embeddings for {len(documents)} documents")
                        continue

                    # Store embeddings
                    for noun_id, embedding in zip(noun_ids, embeddings, strict=True):
                        # Ensure embedding is a list
                        if hasattr(embedding, "tolist"):
                            embedding_list = embedding.tolist()
                        else:
                            embedding_list = list(embedding)

                        cur.execute(
                            """
                            INSERT INTO gematria.noun_embeddings (noun_id, embedding, model)
                            VALUES (%s, %s, %s)
                            ON CONFLICT (noun_id) DO UPDATE SET
                                embedding = EXCLUDED.embedding,
                                model = EXCLUDED.model
                        """,
                            (noun_id, embedding_list, model_name),
                        )

                    total_processed += len(batch)
                    print(f"Stored {len(batch)} embeddings (total: {total_processed}/{len(rows)})")

                    # Optional sleep between batches
                    if sleep_sec > 0 and batch_num < total_batches:
                        time.sleep(sleep_sec)

                except Exception as e:
                    print(f"Error processing batch {batch_num}: {e}")
                    continue

            print("Embedding backfill completed!")
            print(f"Total nouns processed: {total_processed}")

            # Final verification
            cur.execute("""
                SELECT COUNT(*) FROM gematria.nouns n
                JOIN gematria.noun_embeddings ne ON n.id = ne.noun_id
            """)
            embedded_count = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM gematria.nouns")
            total_nouns = cur.fetchone()[0]

            print(f"Nouns with embeddings: {embedded_count}/{total_nouns}")


def main():
    ap = argparse.ArgumentParser(description="Backfill embeddings for gematria.nouns")
    ap.add_argument("--dsn", required=True, help="GEMATRIA_DSN connection string")
    ap.add_argument("--lmstudio", help="LM Studio base URL (default: from env)")
    ap.add_argument("--model", required=True, help="Embedding model name")
    ap.add_argument("--dim", type=int, required=True, help="Embedding dimension")
    ap.add_argument("--batch", type=int, default=512, help="Batch size")
    ap.add_argument("--sleep", type=float, default=0.0, help="Sleep seconds between batches")
    ap.add_argument("--where", default="", help="Additional WHERE clause for noun selection")
    args = ap.parse_args()

    backfill_noun_embeddings(
        dsn=args.dsn,
        lmstudio_base=args.lmstudio,
        model_name=args.model,
        dim=args.dim,
        batch_size=args.batch,
        sleep_sec=args.sleep,
        where_clause=args.where,
    )


if __name__ == "__main__":
    main()
