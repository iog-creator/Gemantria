"""
Tests for Ketiv-primary policy enforcement (Phase 2).

Validates that gematria calculations use Ketiv (written form) as primary,
per ADR-002. Qere (read form) must be recorded as variant.
"""

from src.core.hebrew_utils import calculate_gematria, get_ketiv_for_gematria
from src.ssot.noun_adapter import adapt_ai_noun
from scripts.guards.guard_ketiv_primary import validate_ketiv_primary


class TestKetivPrimaryPolicy:
    """Test Ketiv-primary policy enforcement."""

    def test_ketiv_in_surface(self):
        """Test that Ketiv is stored in surface field."""
        noun = {
            "hebrew": "כתיב",  # Ketiv (written form)
            "variant_type": "ketiv",
            "variant_surface": "קרי",  # Qere (read form)
        }
        adapted = adapt_ai_noun(noun)
        assert adapted["surface"] == "כתיב"  # Ketiv in surface
        assert adapted["variant_surface"] == "קרי"  # Qere in variant
        assert adapted["is_ketiv"] is True

    def test_qere_swapped_to_ketiv(self):
        """Test that Qere provided as primary is swapped to make Ketiv primary."""
        noun = {
            "hebrew": "קרי",  # Qere provided as primary
            "variant_type": "qere",
            "variant_surface": "כתיב",  # Ketiv in variant
        }
        adapted = adapt_ai_noun(noun)
        # Should swap: Ketiv in surface, Qere in variant
        assert adapted["surface"] == "כתיב"  # Ketiv now in surface
        assert adapted["variant_surface"] == "קרי"  # Qere in variant
        assert adapted["is_ketiv"] is True

    def test_gematria_uses_ketiv(self):
        """Test that gematria calculation uses Ketiv, not Qere."""
        noun = {
            "surface": "כתיב",  # Ketiv
            "variant_surface": "קרי",  # Qere
            "is_ketiv": True,
        }
        ketiv = get_ketiv_for_gematria(noun)
        assert ketiv == "כתיב"  # Should use Ketiv
        assert ketiv != "קרי"  # Should not use Qere

        # Calculate gematria from Ketiv
        gematria_ketiv = calculate_gematria(ketiv)
        # Calculate gematria from Qere (should be different)
        gematria_qere = calculate_gematria("קרי")
        # They should be different (different words)
        assert gematria_ketiv != gematria_qere

    def test_no_variant_defaults_to_ketiv(self):
        """Test that nouns without variants default to Ketiv."""
        noun = {
            "hebrew": "אדם",
        }
        adapted = adapt_ai_noun(noun)
        assert adapted["surface"] == "אדם"
        assert adapted["is_ketiv"] is True
        assert adapted["variant_surface"] is None

    def test_validate_ketiv_primary_pass(self):
        """Test validation passes for correct Ketiv-primary nouns."""
        noun = {
            "noun_id": "test-1",
            "surface": "כתיב",  # Ketiv
            "variant_surface": "קרי",  # Qere
            "is_ketiv": True,
            "variant_type": "ketiv",
        }
        errors = validate_ketiv_primary(noun)
        assert len(errors) == 0

    def test_validate_ketiv_primary_fail_qere_in_surface(self):
        """Test validation fails when Qere is in surface instead of Ketiv."""
        noun = {
            "noun_id": "test-2",
            "surface": "קרי",  # Qere (wrong - should be Ketiv)
            "variant_surface": "כתיב",  # Ketiv (wrong - should be Qere)
            "is_ketiv": False,  # Marked as Qere
            "variant_type": "qere",
        }
        errors = validate_ketiv_primary(noun)
        assert len(errors) > 0
        assert any("should be Ketiv" in e for e in errors)

    def test_validate_invalid_variant_type(self):
        """Test validation fails for invalid variant_type."""
        noun = {
            "noun_id": "test-3",
            "surface": "כתיב",
            "variant_type": "invalid_type",
        }
        errors = validate_ketiv_primary(noun)
        assert len(errors) > 0
        assert any("invalid variant_type" in e for e in errors)

    def test_gematria_calculation_consistency(self):
        """Test that gematria calculations are consistent for same Ketiv."""
        # Same Ketiv should produce same gematria
        ketiv1 = "אדם"
        ketiv2 = "אדם"
        assert calculate_gematria(ketiv1) == calculate_gematria(ketiv2)

        # Different Ketiv should produce different gematria
        ketiv3 = "הבל"
        assert calculate_gematria(ketiv1) != calculate_gematria(ketiv3)

    def test_span_tracking(self):
        """Test that span_start and span_end are preserved."""
        noun = {
            "hebrew": "כתיב",
            "variant_type": "ketiv",
            "variant_surface": "קרי",
            "span_start": 10,
            "span_end": 15,
        }
        adapted = adapt_ai_noun(noun)
        assert adapted["span_start"] == 10
        assert adapted["span_end"] == 15
