from agentpm.biblescholar.contextual_fetch import ContextualFetch


class DummyRelationshipAdapter:
    def __init__(self, engine):
        self.engine = engine
        self.called_for_verse = None

    def get_proper_names_for_verse(self, verse_id):
        self.called_for_verse = verse_id
        return ["John"]

    def get_verse_word_links(self, verse_id):
        return [{"source": "John", "target": "wilderness"}]


class DummyLexiconAdapter:
    def __init__(self, engine):
        self.engine = engine
        self.lemmas_called_for = None

    def get_lemmas_for_verse(self, verse_id):
        self.lemmas_called_for = verse_id
        return ["lemma1", "lemma2"]

    def get_morph_tokens_for_verse(self, verse_id):
        return ["N-NSM", "V-PAI-3S"]

    def get_greek_words_for_verse(self, verse_id):
        return ["logos"]

    def get_cross_language_lemmas_for_verse(self, verse_id):
        return [{"greek_strongs": "G3056", "hebrew_strongs": "H1697"}]


class DummyBibleDbAdapter:
    def __init__(self, engine):
        self.engine = engine
        self.called_for_verse = None

    def get_verse_text(self, verse_id):
        self.called_for_verse = verse_id
        return "In the beginning..."


def test_contextual_fetch_basic_shape(monkeypatch):
    engine = object()

    # Patch adapters used inside ContextualFetch
    monkeypatch.setattr(
        "agentpm.biblescholar.contextual_fetch.RelationshipAdapter",
        lambda engine: DummyRelationshipAdapter(engine),
    )
    monkeypatch.setattr(
        "agentpm.biblescholar.contextual_fetch.LexiconAdapter",
        lambda engine: DummyLexiconAdapter(engine),
    )
    monkeypatch.setattr(
        "agentpm.biblescholar.contextual_fetch.BibleDbAdapter",
        lambda engine: DummyBibleDbAdapter(engine),
    )

    fetch = ContextualFetch(engine)
    result = fetch.fetch_for_verse(1)

    assert result["verse_id"] == 1
    assert result["verse_text"] == "In the beginning..."
    assert result["lemmas"] == ["lemma1", "lemma2"]
    assert result["morph_tokens"] == ["N-NSM", "V-PAI-3S"]
    assert result["proper_names"] == ["John"]
    assert result["verse_word_links"] == [{"source": "John", "target": "wilderness"}]
    assert result["greek_words"] == ["logos"]
    assert result["xlang_lemmas"] == [{"greek_strongs": "G3056", "hebrew_strongs": "H1697"}]


def test_contextual_fetch_none_semantics(monkeypatch):
    engine = object()

    class EmptyLexicon(DummyLexiconAdapter):
        def get_lemmas_for_verse(self, verse_id):
            return None

        def get_morph_tokens_for_verse(self, verse_id):
            return None

        def get_greek_words_for_verse(self, verse_id):
            return None

        def get_cross_language_lemmas_for_verse(self, verse_id):
            return None

    class EmptyRelationship(DummyRelationshipAdapter):
        def get_proper_names_for_verse(self, verse_id):
            return None

        def get_verse_word_links(self, verse_id):
            return None

    monkeypatch.setattr(
        "agentpm.biblescholar.contextual_fetch.RelationshipAdapter",
        lambda engine: EmptyRelationship(engine),
    )
    monkeypatch.setattr(
        "agentpm.biblescholar.contextual_fetch.LexiconAdapter",
        lambda engine: EmptyLexicon(engine),
    )
    monkeypatch.setattr(
        "agentpm.biblescholar.contextual_fetch.BibleDbAdapter",
        lambda engine: DummyBibleDbAdapter(engine),
    )

    fetch = ContextualFetch(engine)
    result = fetch.fetch_for_verse(2)

    assert result["verse_id"] == 2
    assert isinstance(result["lemmas"], list) and result["lemmas"] == []
    assert isinstance(result["morph_tokens"], list) and result["morph_tokens"] == []
    assert isinstance(result["proper_names"], list) and result["proper_names"] == []
    assert isinstance(result["verse_word_links"], list) and result["verse_word_links"] == []
    assert isinstance(result["greek_words"], list) and result["greek_words"] == []
    assert isinstance(result["xlang_lemmas"], list) and result["xlang_lemmas"] == []


def test_contextual_fetch_does_not_require_llm(monkeypatch):
    """
    Sanity check: contextual_fetch must not import or depend on any LLM adapters.
    This is a structural test; it ensures we don't accidentally wire in LLM calls.
    """
    import agentpm.biblescholar.contextual_fetch as cf_mod

    # The module should not expose any obvious LLM fields / adapters.
    forbidden_names = ["LLMAdapter", "TheologyAdapter", "RerankerAdapter"]
    for name in forbidden_names:
        assert not hasattr(cf_mod, name)
