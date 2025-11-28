"""Tests for AI Noun Discovery LOUD FAIL enforcement (Phase 14 PR 14.2)."""

import os

import pytest

from src.nodes.ai_noun_discovery import AINounDiscovery


class TestLoudFailEnforcement:
    """Test LOUD FAIL (Rule 046) enforcement for missing DB seed source."""

    def test_loud_fail_missing_db_seed(self, tmp_path):
        """Test LOUD FAIL when DB seed file missing (Rule 046)."""
        discoverer = AINounDiscovery()

        # Temporarily change working directory to ensure seed file doesn't exist
        original_cwd = os.getcwd()
        temp_dir = tmp_path / "test_env"
        temp_dir.mkdir()

        try:
            os.chdir(temp_dir)

            # Attempt to get DB seeds (should raise RuntimeError with LOUD FAIL)
            with pytest.raises(RuntimeError) as exc_info:
                discoverer._get_db_seed_nouns()

            error_msg = str(exc_info.value)

            # Verify LOUD FAIL message contains required elements
            assert "LOUD FAIL (Rule 046)" in error_msg
            assert "DB seed source unavailable" in error_msg
            assert "exports/ai_nouns.db_morph.json" in error_msg
            assert "Code > DB > LLM" in error_msg
            assert "python scripts/ingest_bible_db_morphology.py" in error_msg

        finally:
            os.chdir(original_cwd)

    def test_loud_fail_corrupt_db_seed(self, tmp_path):
        """Test LOUD FAIL when DB seed file is corrupt."""
        discoverer = AINounDiscovery()

        # Create corrupt JSON file
        seed_file = tmp_path / "exports" / "ai_nouns.db_morph.json"
        seed_file.parent.mkdir(parents=True)
        seed_file.write_text("{ invalid json")

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            with pytest.raises(RuntimeError) as exc_info:
                discoverer._get_db_seed_nouns()

            error_msg = str(exc_info.value)
            assert "LOUD FAIL (Rule 046)" in error_msg
            assert "corrupt or invalid" in error_msg

        finally:
            os.chdir(original_cwd)

    def test_db_seeds_loaded_successfully(self, tmp_path):
        """Test successful DB seeds loading."""
        discoverer = AINounDiscovery()

        # Create valid seed file
        seed_file = tmp_path / "exports" / "ai_nouns.db_morph.json"
        seed_file.parent.mkdir(parents=True)
        seed_file.write_text(
            """{
            "schema": "gemantria/ai-nouns.v1",
            "source": "bible_db.v_morph_tokens",
            "nodes": [
                {
                    "surface": "אֱלֹהִים",
                    "class": "person",
                    "analysis": {"lemma": "אֱלֹהִים"}
                },
                {
                    "surface": "אָדָם",
                    "class": "person",
                    "analysis": {"lemma": "אָדָם"}
                }
            ]
        }"""
        )

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            seeds = discoverer._get_db_seed_nouns()

            # Verify seeds loaded
            assert len(seeds) == 2
            # Verify db_seed flag added
            assert all(seed.get("db_seed") is True for seed in seeds)
            # Verify surface forms preserved
            assert seeds[0]["surface"] == "אֱלֹהִים"
            assert seeds[1]["surface"] == "אָדָם"

        finally:
            os.chdir(original_cwd)


class TestDbSeedPriority:
    """Test DB seed priority enforcement (no LLM override)."""

    def test_db_seeds_not_overridden_by_llm(self):
        """Test that DB seeds cannot be overridden by LLM output.

        Note: This is a placeholder for integration testing.
        Full implementation requires mocking LLM responses and validating
        that DB seeds appear unchanged in final output.
        """
        # TODO: Implement once LLM integration is stable
        pass
