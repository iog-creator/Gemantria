from agentpm.biblescholar.contextual_chunks import ContextualChunkBuilder


def test_contextual_chunk_builder_structure():
    builder = ContextualChunkBuilder()
    chunk = builder.build_chunk(1)
    assert chunk["verse_id"] == 1
    assert "text" in chunk
    assert "lemmas" in chunk
    assert "morph_tokens" in chunk
    assert "proper_names" in chunk
    assert "entities" in chunk
    assert "verse_links" in chunk
    assert "gematria" in chunk
