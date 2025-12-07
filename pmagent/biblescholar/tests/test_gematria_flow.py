from __future__ import annotations

"""Tests for BibleScholar Gematria flow.

Tests cover:
- Supported systems list
- Single system computation
- Multi-system computation
- Default behavior (all systems)
- Canonical examples (אדם=45, הבל=37)
"""

from pmagent.biblescholar.gematria_flow import (
    VerseGematriaSummary,
    compute_verse_gematria,
    supported_gematria_systems,
)


def test_supported_gematria_systems_includes_known_systems() -> None:
    """Test that supported systems include mispar_hechrachi and mispar_gadol."""
    systems = supported_gematria_systems()
    assert "mispar_hechrachi" in systems
    assert "mispar_gadol" in systems
    assert len(systems) >= 2


def test_compute_verse_gematria_basic_hechrachi() -> None:
    """Test canonical example: אדם (Adam) = 45 in Mispar Hechrachi."""
    summary = compute_verse_gematria(
        text="אדם",
        osis_ref="Gen.2.7",
        systems=["mispar_hechrachi"],
    )

    assert isinstance(summary, VerseGematriaSummary)
    assert summary.osis_ref == "Gen.2.7"
    assert summary.text == "אדם"
    assert "mispar_hechrachi" in summary.systems

    hechrachi = summary.systems["mispar_hechrachi"]
    assert hechrachi.value == 45
    assert hechrachi.osis_ref == "Gen.2.7"
    assert hechrachi.system == "mispar_hechrachi"


def test_compute_verse_gematria_basic_hevel_hechrachi() -> None:
    """Test canonical example: הבל (Hevel/Abel) = 37 in Mispar Hechrachi."""
    summary = compute_verse_gematria(
        text="הבל",
        osis_ref="Gen.4.2",
        systems=["mispar_hechrachi"],
    )

    assert summary.osis_ref == "Gen.4.2"
    assert summary.text == "הבל"
    hechrachi = summary.systems["mispar_hechrachi"]
    assert hechrachi.value == 37


def test_compute_verse_gematria_multi_system() -> None:
    """Test multi-system computation with both mispar_hechrachi and mispar_gadol."""
    systems = ["mispar_hechrachi", "mispar_gadol"]
    summary = compute_verse_gematria(
        text="הבל",
        osis_ref="Gen.4.2",
        systems=systems,
    )

    assert set(summary.systems.keys()) == set(systems)

    hechrachi = summary.systems["mispar_hechrachi"]
    gadol = summary.systems["mispar_gadol"]

    assert hechrachi.value == 37
    assert hechrachi.osis_ref == "Gen.4.2"
    assert hechrachi.system == "mispar_hechrachi"

    assert gadol.system == "mispar_gadol"
    assert gadol.osis_ref == "Gen.4.2"
    # Gadol value should be different from Hechrachi (no final forms in הבל, so same)
    assert gadol.value == 37  # ה=5, ב=2, ל=30 in both systems


def test_compute_verse_gematria_multi_system_with_final() -> None:
    """Test multi-system computation with final form (ם) that differs between systems."""
    systems = ["mispar_hechrachi", "mispar_gadol"]
    summary = compute_verse_gematria(
        text="אדם",
        osis_ref="Gen.2.7",
        systems=systems,
    )

    hechrachi = summary.systems["mispar_hechrachi"]
    gadol = summary.systems["mispar_gadol"]

    # אדם: א=1, ד=4, ם=40 (Hechrachi) or 600 (Gadol)
    assert hechrachi.value == 45  # 1 + 4 + 40
    assert gadol.value == 605  # 1 + 4 + 600


def test_compute_verse_gematria_defaults_to_all_systems() -> None:
    """Test that systems=None uses all supported systems."""
    summary = compute_verse_gematria(
        text="אדם",
        osis_ref="Gen.2.7",
        systems=None,
    )

    systems = supported_gematria_systems()
    assert set(summary.systems.keys()) == set(systems)
    assert "mispar_hechrachi" in summary.systems
    assert "mispar_gadol" in summary.systems


def test_compute_verse_gematria_empty_systems_list() -> None:
    """Test that empty systems list returns empty summary."""
    summary = compute_verse_gematria(
        text="אדם",
        osis_ref="Gen.2.7",
        systems=[],
    )

    assert summary.osis_ref == "Gen.2.7"
    assert summary.text == "אדם"
    assert len(summary.systems) == 0


def test_verse_gematria_summary_dataclass() -> None:
    """Test that VerseGematriaSummary dataclass works correctly."""
    from pmagent.biblescholar.gematria_adapter import GematriaPhraseResult

    result = GematriaPhraseResult(
        text="אדם",
        normalized="אדם",
        letters=["א", "ד", "ם"],
        system="mispar_hechrachi",
        value=45,
        osis_ref="Gen.2.7",
    )

    summary = VerseGematriaSummary(
        osis_ref="Gen.2.7",
        text="אדם",
        systems={"mispar_hechrachi": result},
    )

    assert summary.osis_ref == "Gen.2.7"
    assert summary.text == "אדם"
    assert "mispar_hechrachi" in summary.systems
    assert summary.systems["mispar_hechrachi"].value == 45
