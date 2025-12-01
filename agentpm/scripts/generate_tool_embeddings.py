#!/usr/bin/env python3
"""
Generate embeddings for MCP tools to enable semantic tool discovery.

This script:
1. Fetches all tools from mcp.tools table
2. Generates embeddings using the configured embedding provider (Ollama BGE-M3)
3. Updates the embedding column in mcp.tools

Usage:
    python agentpm/scripts/generate_tool_embeddings.py

    # Or via pmagent CLI:
    pmagent mcp generate-embeddings
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import psycopg
from agentpm.adapters.lm_studio import embed
from scripts.config.env import get_rw_dsn
from src.infra.structured_logger import get_logger

LOG = get_logger("generate_tool_embeddings")


def generate_tool_embeddings(dry_run: bool = False) -> None:
    """Generate embeddings for all MCP tools.

    Args:
        dry_run: If True, only show what would be updated without making changes
    """
    # Test embedding generation first
    try:
        LOG.info("Testing embedding generation...")
        test_embeddings = embed(["test"], model_slot="embedding")
        if not test_embeddings or not test_embeddings[0]:
            LOG.error("Embedding test failed: empty result returned")
            LOG.error(
                "Check that EMBEDDING_PROVIDER=ollama and EMBEDDING_MODEL is set correctly in .env"
            )
            sys.exit(1)
        LOG.info(f"Embedding test successful (dimension: {len(test_embeddings[0])})")
    except Exception as e:
        LOG.error(f"Embedding test failed: {e}")
        LOG.error("Make sure Ollama is running and the embedding model is installed")
        LOG.error("Try: ollama list")
        sys.exit(1)

    dsn = get_rw_dsn()
    if not dsn:
        LOG.error("Database not available (get_rw_dsn returned None)")
        sys.exit(1)

    with psycopg.connect(dsn) as conn:
        # Check if embedding column exists
        with conn.cursor() as cur:
            cur.execute("""
                SELECT EXISTS(
                    SELECT 1 FROM information_schema.columns
                    WHERE table_schema = 'mcp' 
                      AND table_name = 'tools'
                      AND column_name = 'embedding'
                )
            """)
            has_embedding_column = cur.fetchone()[0]

            if not has_embedding_column:
                LOG.error("mcp.tools.embedding column does not exist. Run migration first.")
                sys.exit(1)

        # Fetch all tools that need embeddings
        with conn.cursor() as cur:
            cur.execute("""
                SELECT name, "desc", tags
                FROM mcp.tools
                WHERE embedding IS NULL OR embedding::text = '[0,0,0]'::text
                ORDER BY name
            """)
            tools = cur.fetchall()

        if not tools:
            LOG.info("No tools need embeddings. All tools are up to date.")
            return

        LOG.info(f"Found {len(tools)} tools that need embeddings")

        # Generate embeddings for each tool
        updated_count = 0
        failed_count = 0

        for name, description, tags in tools:
            # Combine name, description, and tags into a single text for embedding
            tags_str = ", ".join(tags) if tags else ""
            combined_text = f"{name}. {description or ''}. Tags: {tags_str}".strip()

            try:
                LOG.info(f"Generating embedding for tool: {name}")

                # Generate embedding using configured provider (Ollama BGE-M3)
                embeddings = embed([combined_text], model_slot="embedding")

                if not embeddings or not embeddings[0]:
                    LOG.warning(f"Empty embedding returned for tool: {name}")
                    failed_count += 1
                    continue

                embedding_vector = embeddings[0]

                if dry_run:
                    LOG.info(
                        f"[DRY RUN] Would update embedding for {name} (dimension: {len(embedding_vector)})"
                    )
                else:
                    # Update the tool with the embedding
                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            UPDATE mcp.tools
                            SET embedding = %s::vector
                            WHERE name = %s
                            """,
                            (str(embedding_vector), name),
                        )
                    conn.commit()
                    LOG.info(f"Updated embedding for {name} (dimension: {len(embedding_vector)})")

                updated_count += 1

            except Exception as e:
                LOG.error(f"Failed to generate embedding for {name}: {e}")
                failed_count += 1
                continue

        # Summary
        LOG.info("Embedding generation complete:")
        LOG.info(f"  - Updated: {updated_count}")
        LOG.info(f"  - Failed: {failed_count}")
        LOG.info(f"  - Dry run: {dry_run}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate embeddings for MCP tools")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be updated without making changes"
    )

    args = parser.parse_args()

    try:
        generate_tool_embeddings(dry_run=args.dry_run)
    except KeyboardInterrupt:
        LOG.info("Interrupted by user")
        sys.exit(130)
    except Exception as e:
        LOG.error(f"Fatal error: {e}")
        sys.exit(1)
