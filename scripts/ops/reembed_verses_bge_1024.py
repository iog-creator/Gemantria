#!/usr/bin/env python3
"""Re-embed bible.verses corpus with BGE-M3 (1024-D).

This script performs a full corpus re-embedding of bible.verses using BGE-M3,
updating the embedding column to 1024-dimensional vectors.

PREREQUISITES:
- DDL migration must have been executed (embedding column = vector(1024))
- Bible DB must be accessible
- BGE-M3 model must be available via LM Studio or sentence-transformers

Usage:
    python scripts/ops/reembed_verses_bge_1024.py --batch-size 500 --resume

Governance: Rules 050/051/052, 062 (Environment Validation), 069 (DB-First)
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

import psycopg
from pgvector.psycopg import register_vector
from tqdm import tqdm

from scripts.config.env import get_rw_dsn
from src.infra.env_loader import ensure_env_loaded
from src.services.lmstudio_client import get_lmstudio_client

# Load environment
ensure_env_loaded()


def verify_schema_dimension(conn):
    """Verify bible.verses.embedding is vector(1024)."""  
    with conn.cursor() as cur:
        cur.execute("""
            SELECT atttypmod as dimension
            FROM pg_attribute
            WHERE attrelid = 'bible.verses'::regclass
              AND attname = 'embedding'
        """)
        result = cur.fetchone()
        if not result:
            raise RuntimeError("embedding column not found in bible.verses")
        
        dimension = result[0]
        if dimension != 1024:
            raise RuntimeError(
                f"Schema dimension mismatch: expected 1024, found {dimension}. "
                "Run DDL migration first: scripts/ops/phase13_ddl_migration_1024.sql"
            )
        print(f"✓ Schema verified: embedding is vector({dimension})")


def get_embedding_stats(conn):
    """Get current embedding statistics."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT 
                COUNT(*) as total_verses,
                COUNT(embedding) as embedded_verses,
                COUNT(*) - COUNT(embedding) as pending_verses
            FROM bible.verses
        """)
        return cur.fetchone()


def reembed_batch(client, conn, batch_size=500, resume=False):
    """Re-embed verses in batches."""
    register_vector(conn)
    
    # Get statistics
    total, embedded, pending = get_embedding_stats(conn)
    print(f"\nCurrent status:")
    print(f"  Total verses: {total:,}")
    print(f"  Embedded: {embedded:,}")
    print(f"  Pending: {pending:,}")
    
    if resume and pending == 0:
        print("\n✓ All verses already embedded. No work needed.")
        return
    
    # Build query based on resume mode
    if resume:
        # Only re-embed verses with NULL embeddings
        query = """
            SELECT verse_id, text 
            FROM bible.verses 
            WHERE embedding IS NULL
            ORDER BY verse_id 
            LIMIT %s OFFSET %s
        """
        total_to_process = pending
    else:
        # Re-embed all verses
        query = """
            SELECT verse_id, text 
            FROM bible.verses 
            ORDER BY verse_id 
            LIMIT %s OFFSET %s
        """
        total_to_process = total
    
    print(f"\nProcessing {total_to_process:,} verses in batches of {batch_size}...")
    
    processed = 0
    errors = 0
    start_time = time.time()
    
    with tqdm(total=total_to_process, desc="Re-embedding") as pbar:
        offset = 0
        while True:
            # Fetch batch
            with conn.cursor() as cur:
                cur.execute(query, (batch_size, offset))
                rows = cur.fetchall()
            
            if not rows:
                break  # No more rows
            
            # Extract texts and IDs
            verse_ids = [row[0] for row in rows]
            texts = [row[1] for row in rows]
            
            try:
                # Generate embeddings using BGE-M3
                embeddings = client.get_embeddings(
                    texts, 
                    model="text-embedding-bge-m3"
                )
                
                # Verify dimension
                if embeddings and len(embeddings[0]) != 1024:
                    raise RuntimeError(
                        f"Embedding dimension mismatch: expected 1024, got {len(embeddings[0])}"
                    )
                
                # Update batch
                with conn.cursor() as cur:
                    for verse_id, embedding in zip(verse_ids, embeddings):
                        cur.execute("""
                            UPDATE bible.verses 
                            SET embedding = %s 
                            WHERE verse_id = %s
                        """, (embedding, verse_id))
                conn.commit()
                
                processed += len(rows)
                pbar.update(len(rows))
                
            except Exception as e:
                print(f"\n❌ Error processing batch at offset {offset}: {e}")
                errors += 1
                if errors > 10:
                    print("Too many errors, aborting.")
                    break
            
            offset += batch_size
    
    elapsed = time.time() - start_time
    print(f"\n✓ Re-embedding complete!")
    print(f"  Processed: {processed:,} verses")
    print(f"  Errors: {errors}")
    print(f"  Time: {elapsed/60:.1f} minutes")
    print(f"  Rate: {processed/elapsed:.1f} verses/second")
    
    # Final verification
    total, embedded, pending = get_embedding_stats(conn)
    print(f"\nFinal status:")
    print(f"  Total verses: {total:,}")
    print(f"  Embedded: {embedded:,}")
    print(f"  Pending: {pending:,}")


def main():
    parser = argparse.ArgumentParser(description="Re-embed bible.verses with BGE-M3 (1024-D)")
    parser.add_argument(
        "--batch-size",
        type=int,
        default=500,
        help="Number of verses per batch (default: 500)"
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume mode: only re-embed NULL embeddings"
    )
    args = parser.parse_args()
    
    print("=" * 80)
    print("Bible Verses BGE-M3 Re-embedding (1024-D)")
    print("=" * 80)
    
    # Get DSN - explicitly use bible_db for vector unification
    dsn = os.getenv("BIBLE_DB_DSN") or "dbname=bible_db"
    print(f"\nConnecting to: {dsn.split('@')[0]}...")  # Hide password if present
    
    # Get LM Studio client
    print("\n1. Initializing BGE-M3 model...")
    client = get_lmstudio_client()
    
    # Connect to DB
    print("2. Connecting to bible_db...")
    with psycopg.connect(dsn) as conn:
        # Verify schema
        print("3. Verifying schema...")
        verify_schema_dimension(conn)
        
        # Re-embed
        print("4. Re-embedding corpus...")
        reembed_batch(
            client=client,
            conn=conn,
            batch_size=args.batch_size,
            resume=args.resume
        )
    
    print("\n✓ All operations complete.")


if __name__ == "__main__":
    main()
