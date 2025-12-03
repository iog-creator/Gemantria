"""Live integration tests for Phase 15 Wave-2 RAG retrieval engine.

These tests run against REAL infrastructure:
- PostgreSQL with 116K verses with 1024-D embeddings
- Ollama with granite-embedding model

Mark tests with @pytest.mark.live to skip in CI.

See: docs/SSOT/PHASE15_WAVE2_SPEC.md
"""

import pytest

from pmagent.biblescholar.embedding_adapter import EmbeddingAdapter
from pmagent.biblescholar.rag_retrieval import RAGRetriever


@pytest.mark.live
class TestRAGLiveIntegration:
    """Live integration tests with real DB and LM."""

    def test_live_embedding_retrieval(self):
        """Verify we can retrieve real 1024-D embeddings from DB."""
        adapter = EmbeddingAdapter()

        # Check DB is available
        assert adapter.db_status in ["available", "ready"]

        # Get a valid verse_id (actual range: 42,358 to 323,425)
        # Use a known verse_id that exists in the database
        from sqlalchemy import text
        from pmagent.db.loader import get_bible_engine
        
        engine = get_bible_engine()
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT verse_id 
                FROM bible.verse_embeddings 
                WHERE embedding IS NOT NULL 
                ORDER BY verse_id 
                LIMIT 1
            """))
            valid_verse_id = result.scalar()
            assert valid_verse_id is not None, "No verses with embeddings found"
            assert valid_verse_id >= 42358, f"Expected verse_id >= 42358, got {valid_verse_id}"

        # Get embedding for a valid verse
        embedding = adapter.get_embedding_for_verse(valid_verse_id)

        # Verify we got a real embedding
        assert embedding is not None
        assert len(embedding) == 1024, f"Expected 1024-D, got {len(embedding)}-D"

        # Verify it's not all zeros
        assert embedding.sum() != 0, "Embedding should not be all zeros"

    def test_live_vector_search(self):
        """Verify vector search works with real pgvector data."""
        adapter = EmbeddingAdapter()

        # Get a valid verse_id (actual range: 42,358 to 323,425)
        from sqlalchemy import text
        from pmagent.db.loader import get_bible_engine
        
        engine = get_bible_engine()
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT verse_id 
                FROM bible.verse_embeddings 
                WHERE embedding IS NOT NULL 
                ORDER BY verse_id 
                LIMIT 1
            """))
            valid_verse_id = result.scalar()
            assert valid_verse_id is not None, "No verses with embeddings found"

        # Get a real embedding to use as query
        query_embedding = adapter.get_embedding_for_verse(valid_verse_id)
        assert query_embedding is not None

        # Search for similar verses
        results = adapter.vector_search(query_embedding, top_k=5)

        # Verify results
        assert len(results) > 0, "Should find similar verses"
        assert len(results) <= 5, "Should respect top_k limit"

        # Results should be (verse_id, similarity_score) tuples
        for verse_id, score in results:
            assert isinstance(verse_id, int)
            assert verse_id >= 42358, f"Expected verse_id >= 42358, got {verse_id}"
            assert 0.0 <= score <= 1.0, f"Similarity score {score} out of range"

        # First result should be the query verse itself with high similarity
        first_verse_id, first_score = results[0]
        assert first_verse_id == valid_verse_id, f"First result should be query verse {valid_verse_id}, got {first_verse_id}"
        assert first_score > 0.99, f"Self-similarity should be ~1.0, got {first_score}"

    def test_live_rag_retrieval_end_to_end(self):
        """Test complete RAG pipeline with real data."""
        retriever = RAGRetriever()

        # Use a real biblical query
        query = "In the beginning God created"
        results = retriever.retrieve_contextual_chunks(query, top_k=3)

        # Verify we got results
        assert len(results) > 0, "Should retrieve chunks for biblical query"
        assert len(results) <= 3, "Should respect top_k limit"

        # Verify chunk structure
        for chunk in results:
            assert "verse_id" in chunk
            assert "cosine" in chunk  # SSOT field name (Rule 045)
            assert "relevance_score" in chunk
            assert "context_window" in chunk
            assert "enriched_metadata" in chunk

            # Verify scores are valid
            assert 0.0 <= chunk["cosine"] <= 1.0
            assert 0.0 <= chunk["relevance_score"] <= 1.0

    def test_live_embedding_dimensions_verification(self):
        """Verify all embeddings in DB are 1024-D (BGE-M3 compatible)."""
        from sqlalchemy import text
        from pmagent.db.loader import get_bible_engine

        engine = get_bible_engine()
        with engine.connect() as conn:
            # Check a sample of embeddings
            result = conn.execute(
                text("""
                SELECT verse_id, vector_dims(embedding) as dims 
                FROM bible.verse_embeddings 
                WHERE embedding IS NOT NULL 
                LIMIT 100
            """)
            )

            for row in result:
                verse_id, dims = row[0], row[1]
                assert dims == 1024, f"Verse {verse_id} has {dims}-D embedding, expected 1024-D"

    def test_live_db_connection_pool(self):
        """Verify DB connection pooling works under load."""
        adapter = EmbeddingAdapter()

        # Make multiple requests to test connection pooling
        for i in range(1, 11):
            embedding = adapter.get_embedding_for_verse(i)
            assert embedding is not None
            assert len(embedding) == 1024

    @pytest.mark.skip("Reranker integration pending Wave-3")
    def test_live_reranker_with_ollama(self):
        """Test reranker with actual Ollama granite-embedding model."""
        # This will be implemented in Wave-3 when reranker is wired up
        pass


@pytest.mark.live
def test_live_infrastructure_readiness():
    """Verify live infrastructure is ready for RAG testing."""
    from sqlalchemy import text
    from pmagent.db.loader import get_bible_engine

    # Check DB
    engine = get_bible_engine()
    with engine.connect() as conn:
        # Count embeddings
        result = conn.execute(text("SELECT COUNT(*) FROM bible.verse_embeddings WHERE embedding IS NOT NULL"))
        count = result.scalar()
        assert count > 100000, f"Expected >100K embeddings, found {count:,}"

        # Check dimensions
        result = conn.execute(
            text("SELECT vector_dims(embedding) FROM bible.verse_embeddings WHERE embedding IS NOT NULL LIMIT 1")
        )
        dims = result.scalar()
        assert dims == 1024, f"Expected 1024-D embeddings, found {dims}-D"

    print(f"✅ Live infrastructure ready: {count:,} verses with {dims}-D embeddings")
