"""Tests for Greek Isopsephy (gematria) calculation and normalization.

Tests Rule G-001 compliance and 27-letter Isopsephy system.
"""

from __future__ import annotations

import pytest

from agentpm.modules.gematria import greek


class TestGreekNormalization:
    """Tests for Rule G-001 (Greek Normalization Contract)."""

    def test_normalize_removes_polytonic_accents(self):
        """Polytonic accents should be stripped per Rule G-001."""
        assert greek.normalize_greek("Ἰησοῦς") == "ιησους"  # Jesus with polytonic
        assert greek.normalize_greek("Χριστός") == "χριστος"  # Christ with accent
        assert greek.normalize_greek("ἀγάπη") == "αγαπη"  # Love with accents

    def test_normalize_removes_breathing_marks(self):
        """Breathing marks should be stripped per Rule G-001."""
        assert greek.normalize_greek("ἁγιος") == "αγιος"  # Holy with rough breathing
        assert greek.normalize_greek("ὑπό") == "υπο"  # Under with breathing

    def test_normalize_removes_punctuation(self):
        """Punctuation should be stripped per Rule G-001."""
        assert greek.normalize_greek("Ἰησοῦς.") == "ιησους"
        assert greek.normalize_greek("Χριστός!") == "χριστος"
        assert greek.normalize_greek("α, β, γ") == "αβγ"

    def test_normalize_removes_spaces(self):
        """Spaces should be stripped per Rule G-001."""
        assert greek.normalize_greek("Ἰησοῦς Χριστός") == "ιησουςχριστος"
        assert greek.normalize_greek("α β γ") == "αβγ"

    def test_normalize_preserves_final_sigma(self):
        """Final sigma (ς) should be eq to regular sigma (σ) for calculations."""
        assert greek.normalize_greek("Ιησους") == "ιησους"  # Lowercase canonical
        assert greek.calculate_gematria("ς") == greek.calculate_gematria("σ")  # Both = 200

    def test_normalize_empty_input(self):
        """Empty input should return empty string."""
        assert greek.normalize_greek("") == ""
        assert greek.normalize_greek(None) == ""

    def test_normalize_non_greek_text(self):
        """Non-Greek text should return empty string."""
        assert greek.normalize_greek("Hello World") == ""
        assert greek.normalize_greek("123 456") == ""

    def test_normalize_mixed_script(self):
        """Only Greek letters should be preserved."""
        assert greek.normalize_greek("Hello α World β") == "αβ"
        assert greek.normalize_greek("123 Ιησους 456") == "ιησους"


class TestGreekIsopsephy:
    """Tests for 27-letter Isopsephy system."""

    def test_jesus_equals_888(self):
        """Critical test: Ιησους (Jesus) = 888 per classical Isopsephy."""
        # Ι(10) + η(8) + σ(200) + ο(70) + υ(400) + ς(200) = 888
        assert greek.calculate_gematria("Ιησους") == 888

    def test_christ_equals_1480(self):
        """Χριστος (Christ) = 1480."""
        # Χ(600) + ρ(100) + ι(10) + σ(200) + τ(300) + ο(70) + ς(200) = 1480
        assert greek.calculate_gematria("Χριστος") == 1480

    def test_units_mapping(self):
        """Test units (1-9) mapping."""
        assert greek.calculate_gematria("α") == 1
        assert greek.calculate_gematria("β") == 2
        assert greek.calculate_gematria("γ") == 3
        assert greek.calculate_gematria("δ") == 4
        assert greek.calculate_gematria("ε") == 5
        assert greek.calculate_gematria("ϝ") == 6  # Digamma (archaic)
        assert greek.calculate_gematria("ζ") == 7
        assert greek.calculate_gematria("η") == 8
        assert greek.calculate_gematria("θ") == 9

    def test_tens_mapping(self):
        """Test tens (10-90) mapping."""
        assert greek.calculate_gematria("ι") == 10
        assert greek.calculate_gematria("κ") == 20
        assert greek.calculate_gematria("λ") == 30
        assert greek.calculate_gematria("μ") == 40
        assert greek.calculate_gematria("ν") == 50
        assert greek.calculate_gematria("ξ") == 60
        assert greek.calculate_gematria("ο") == 70
        assert greek.calculate_gematria("π") == 80
        assert greek.calculate_gematria("ϙ") == 90  # Koppa (archaic)

    def test_hundreds_mapping(self):
        """Test hundreds (100-900) mapping."""
        assert greek.calculate_gematria("ρ") == 100
        assert greek.calculate_gematria("σ") == 200
        assert greek.calculate_gematria("ς") == 200  # Final sigma = Same as sigma
        assert greek.calculate_gematria("τ") == 300
        assert greek.calculate_gematria("υ") == 400
        assert greek.calculate_gematria("φ") == 500
        assert greek.calculate_gematria("χ") == 600
        assert greek.calculate_gematria("ψ") == 700
        assert greek.calculate_gematria("ω") == 800
        assert greek.calculate_gematria("ϡ") == 900  # Sampi (archaic)

    def test_final_sigma_equals_sigma(self):
        """Final sigma (ς) should equal regular sigma (σ) = 200."""
        assert greek.calculate_gematria("ς") == 200
        assert greek.calculate_gematria("σ") == 200
        assert greek.calculate_gematria("ς") == greek.calculate_gematria("σ")

    def test_empty_input(self):
        """Empty input should return 0."""
        assert greek.calculate_gematria("") == 0
        assert greek.calculate_gematria(None) == 0

    def test_unknown_characters_ignored(self):
        """Unknown characters should contribute 0 to the sum."""
        assert greek.calculate_gematria("α123β") == 3  # α(1) + β(2) = 3
        assert greek.calculate_gematria("XYZαβγ") == 6  # α(1) + β(2) + γ(3) = 6


class TestLettersFromText:
    """Tests for letters_from_text function."""

    def test_extract_normalized_letters(self):
        """Should extract and normalize Greek letters."""
        assert greek.letters_from_text("Ἰησοῦς") == ["ι", "η", "σ", "ο", "υ", "ς"]
        assert greek.letters_from_text("Χριστός") == ["χ", "ρ", "ι", "σ", "τ", "ο", "ς"]

    def test_empty_input(self):
        """Empty input should return empty list."""
        assert greek.letters_from_text("") == []
        assert greek.letters_from_text(None) == []

    def test_non_greek_text(self):
        """Non-Greek text should return empty list."""
        assert greek.letters_from_text("Hello World") == []
        assert greek.letters_from_text("123 456") == []


class TestCalcString:
    """Tests for calc_string function (human-readable output)."""

    def test_jesus_calculation_string(self):
        """Should show calculation breakdown for Jesus."""
        result = greek.calc_string("Ιησους")
        assert "ι(10)" in result
        assert "η(8)" in result
        assert "σ(200)" in result
        assert "ο(70)" in result
        assert "υ(400)" in result
        assert "ς(200)" in result
        assert "= 888" in result

    def test_empty_input(self):
        """Empty input should show = 0."""
        assert "= 0" in greek.calc_string("")
