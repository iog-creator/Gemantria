"""Tests for BibleScholar reference slice (Phase-6P)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from agentpm.biblescholar.bible_db_adapter import VerseRecord
from agentpm.biblescholar.gematria_flow import VerseGematriaSummary
from agentpm.biblescholar.reference_slice import ReferenceAnswerResult, answer_reference_question
from agentpm.biblescholar.vector_flow import VerseSimilarityResult


class TestAnswerReferenceQuestion:
    """Test answer_reference_question function."""

    @patch("agentpm.biblescholar.reference_slice.guarded_lm_call")
    @patch("agentpm.biblescholar.reference_slice.similar_verses_for_reference")
    @patch("agentpm.biblescholar.reference_slice.compute_verse_gematria")
    @patch("agentpm.biblescholar.reference_slice.BibleDbAdapter")
    def test_happy_path_with_verse_ref(
        self,
        mock_adapter_class,
        mock_compute_gematria,
        mock_similar_verses,
        mock_guarded_lm,
    ):
        """Test happy path: DB reachable, LM call succeeds."""
        # Mock verse fetch via adapter
        mock_verse = VerseRecord(
            verse_id=1,
            book_name="Genesis",
            chapter_num=1,
            verse_num=1,
            text="בראשית ברא אלהים את השמים ואת הארץ",
            translation_source="KJV",
        )
        mock_adapter = MagicMock()
        mock_adapter.get_verse.return_value = mock_verse
        mock_adapter.db_status = "available"
        mock_adapter_class.return_value = mock_adapter

        # Mock Gematria
        mock_gematria_summary = MagicMock(spec=VerseGematriaSummary)
        mock_gematria_summary.systems = {
            "mispar_hechrachi": MagicMock(value=913),
            "mispar_gadol": MagicMock(value=1000),
        }
        mock_compute_gematria.return_value = mock_gematria_summary

        # Mock similar verses
        mock_similar = [
            VerseSimilarityResult(
                verse_id=2,
                book_name="Genesis",
                chapter_num=1,
                verse_num=2,
                text="And the earth was without form",
                translation_source="KJV",
                similarity_score=0.85,
            )
        ]
        mock_similar_verses.return_value = mock_similar

        # Mock LM call
        mock_guarded_lm.return_value = {
            "ok": True,
            "mode": "lm_on",
            "response": {
                "choices": [
                    {
                        "message": {
                            "content": "This verse describes the creation of the heavens and earth."
                        }
                    }
                ],
                "usage": {"total_tokens": 150},
                "latency_ms": 250,
            },
            "call_site": "biblescholar.reference_slice",
        }

        # Call function
        result = answer_reference_question("What does Genesis 1:1 mean?", "Genesis 1:1")

        # Verify result structure
        assert isinstance(result, ReferenceAnswerResult)
        assert "answer" in result.answer.lower() or "creation" in result.answer.lower()
        assert (
            len(result.trace) == 4
        )  # verse_context, gematria_patterns, vector_similarity, lm_synthesis
        assert "verse_refs" in result.context_used
        assert len(result.context_used["verse_refs"]) > 0
        assert result.lm_meta is not None
        assert result.lm_meta["mode"] == "lm_on"
        assert result.lm_meta["budget_status"] == "ok"

        # Verify trace structure
        verse_trace = result.trace[0]
        assert verse_trace["step"] == "verse_context"
        assert verse_trace["db_status"] in ["available", "unavailable", "db_off"]
        assert verse_trace["result"]["found"] is True

        gematria_trace = result.trace[1]
        assert gematria_trace["step"] == "gematria_patterns"
        assert gematria_trace["patterns_found"] is True

        similarity_trace = result.trace[2]
        assert similarity_trace["step"] == "vector_similarity"
        assert similarity_trace["snippets_count"] == 1

        lm_trace = result.trace[3]
        assert lm_trace["step"] == "lm_synthesis"
        assert lm_trace["provenance"] is not None

    @patch("agentpm.biblescholar.reference_slice.guarded_lm_call")
    @patch("agentpm.biblescholar.reference_slice.BibleDbAdapter")
    def test_db_off_scenario(self, mock_adapter_class, mock_guarded_lm):
        """Test db_off: DB unavailable, function returns result with trace entry."""
        # Mock adapter returning None (DB off)
        mock_adapter = MagicMock()
        mock_adapter.get_verse.return_value = None
        mock_adapter.db_status = "db_off"
        mock_adapter_class.return_value = mock_adapter

        # Mock LM call (should still work even if DB is off)
        mock_guarded_lm.return_value = {
            "ok": True,
            "mode": "lm_on",
            "response": {
                "choices": [
                    {
                        "message": {
                            "content": "I cannot access the verse text, but I can provide general information."
                        }
                    }
                ],
                "usage": {"total_tokens": 100},
                "latency_ms": 200,
            },
            "call_site": "biblescholar.reference_slice",
        }

        # Call function
        result = answer_reference_question("What does Genesis 1:1 mean?", "Genesis 1:1")

        # Verify result structure (should still return valid result)
        assert isinstance(result, ReferenceAnswerResult)
        assert len(result.answer) > 0
        assert len(result.trace) >= 2  # verse_context (with db_off), lm_synthesis

        # Verify trace shows db_off
        verse_trace = result.trace[0]
        assert verse_trace["step"] == "verse_context"
        assert verse_trace["result"]["found"] is False

        # Verify LM was still called (graceful degradation)
        lm_trace = result.trace[-1]
        assert lm_trace["step"] == "lm_synthesis"

    @patch("agentpm.biblescholar.reference_slice.guarded_lm_call")
    @patch("agentpm.biblescholar.reference_slice.similar_verses_for_reference")
    @patch("agentpm.biblescholar.reference_slice.compute_verse_gematria")
    @patch("agentpm.biblescholar.reference_slice.BibleDbAdapter")
    def test_budget_exceeded(
        self,
        mock_adapter_class,
        mock_compute_gematria,
        mock_similar_verses,
        mock_guarded_lm,
    ):
        """Test budget_exceeded: LM call mocked to exceed budget."""
        # Mock verse fetch via adapter
        mock_verse = VerseRecord(
            verse_id=1,
            book_name="Genesis",
            chapter_num=1,
            verse_num=1,
            text="In the beginning",
            translation_source="KJV",
        )
        mock_adapter = MagicMock()
        mock_adapter.get_verse.return_value = mock_verse
        mock_adapter.db_status = "available"
        mock_adapter_class.return_value = mock_adapter

        # Mock Gematria (no Hebrew, so no patterns)
        mock_compute_gematria.return_value = None

        # Mock similar verses (empty)
        mock_similar_verses.return_value = []

        # Mock LM call returning budget_exceeded
        mock_guarded_lm.return_value = {
            "ok": False,
            "mode": "budget_exceeded",
            "reason": "budget_exceeded",
            "response": None,
            "call_site": "biblescholar.reference_slice",
        }

        # Call function
        result = answer_reference_question("What does Genesis 1:1 mean?", "Genesis 1:1")

        # Verify result contains budget_exceeded marker
        assert isinstance(result, ReferenceAnswerResult)
        assert "budget" in result.answer.lower() or "unable" in result.answer.lower()
        assert result.lm_meta is not None
        assert result.lm_meta["mode"] == "budget_exceeded"
        assert result.lm_meta["budget_status"] == "budget_exceeded"

        # Verify trace shows budget_exceeded
        lm_trace = result.trace[-1]
        assert lm_trace["step"] == "lm_synthesis"
        assert lm_trace["result"]["mode"] == "budget_exceeded"

    @patch("agentpm.biblescholar.reference_slice.guarded_lm_call")
    def test_question_only_no_verse_ref(self, mock_guarded_lm):
        """Test minimal input: question only (no verse_ref)."""
        # Mock LM call
        mock_guarded_lm.return_value = {
            "ok": True,
            "mode": "lm_on",
            "response": {
                "choices": [{"message": {"content": "I can answer general Bible questions."}}],
                "usage": {"total_tokens": 80},
                "latency_ms": 150,
            },
            "call_site": "biblescholar.reference_slice",
        }

        # Call function without verse_ref
        result = answer_reference_question("What is the meaning of creation?")

        # Verify result structure
        assert isinstance(result, ReferenceAnswerResult)
        assert len(result.answer) > 0
        assert len(result.trace) >= 1  # At least lm_synthesis

        # Verify no verse context was attempted
        verse_traces = [t for t in result.trace if t["step"] == "verse_context"]
        assert len(verse_traces) == 0

        # Verify context_used has empty verse_refs
        assert result.context_used["verse_refs"] == []

    @patch("agentpm.biblescholar.reference_slice.guarded_lm_call")
    @patch("agentpm.biblescholar.reference_slice.similar_verses_for_reference")
    @patch("agentpm.biblescholar.reference_slice.compute_verse_gematria")
    @patch("agentpm.biblescholar.reference_slice.BibleDbAdapter")
    def test_verse_without_hebrew_no_gematria(
        self,
        mock_adapter_class,
        mock_compute_gematria,
        mock_similar_verses,
        mock_guarded_lm,
    ):
        """Test verse without Hebrew text (no Gematria patterns)."""
        # Mock verse fetch via adapter (English text, no Hebrew)
        mock_verse = VerseRecord(
            verse_id=1,
            book_name="John",
            chapter_num=3,
            verse_num=16,
            text="For God so loved the world",
            translation_source="KJV",
        )
        mock_adapter = MagicMock()
        mock_adapter.get_verse.return_value = mock_verse
        mock_adapter.db_status = "available"
        mock_adapter_class.return_value = mock_adapter

        # Mock similar verses
        mock_similar_verses.return_value = []

        # Mock LM call
        mock_guarded_lm.return_value = {
            "ok": True,
            "mode": "lm_on",
            "response": {
                "choices": [
                    {"message": {"content": "This is a well-known verse about God's love."}}
                ],
                "usage": {"total_tokens": 120},
                "latency_ms": 180,
            },
            "call_site": "biblescholar.reference_slice",
        }

        # Call function
        result = answer_reference_question("What does John 3:16 mean?", "John 3:16")

        # Verify result structure
        assert isinstance(result, ReferenceAnswerResult)
        assert len(result.answer) > 0

        # Verify Gematria trace shows no patterns (no Hebrew)
        gematria_traces = [t for t in result.trace if t["step"] == "gematria_patterns"]
        if gematria_traces:
            gematria_trace = gematria_traces[0]
            assert gematria_trace["patterns_found"] is False

        # Verify context_used has no gematria values
        assert result.context_used["gematria_values"] == []
