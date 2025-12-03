from __future__ import annotations

"""BibleScholar Gematria adapter (read-only).

This module provides a small, typed API for BibleScholar flows to call into
the AgentPM Gematria module without touching databases or the control-plane.

See:
- docs/SSOT/BIBLESCHOLAR_INTAKE.md
- docs/SSOT/AGENTPM_GEMATRIA_MODULE_PLAN.md
- pmagent/biblescholar/AGENTS.md
"""

from dataclasses import dataclass

from pmagent.modules.gematria import core, hebrew


@dataclass
class GematriaPhraseResult:
    """Result of a gematria computation for a phrase (optionally a verse).

    Attributes:
        text: Original input text (preserved as-is).
        normalized: Normalized Hebrew text (diacritics/punctuation removed).
        letters: List of extracted Hebrew letter characters.
        system: Numerics system name used for calculation.
        value: Computed gematria value (0 if no Hebrew letters found).
        osis_ref: Optional OSIS reference (e.g., "Gen.4.2").
    """

    text: str
    normalized: str
    letters: list[str]
    system: str
    value: int
    osis_ref: str | None = None


def compute_phrase_gematria(
    text: str,
    system: str = core.DEFAULT_SYSTEM_NAME,
    osis_ref: str | None = None,
) -> GematriaPhraseResult:
    """Compute gematria for a phrase in a BibleScholar-friendly shape.

    This function is intentionally read-only and pure: it only calls
    Gematria helpers and returns a dataclass result. No database writes,
    no control-plane mutations.

    Args:
        text: Hebrew text (may contain diacritics, punctuation, mixed scripts).
              Handles empty strings and None gracefully (returns value=0).
        system: Numerics system name. Must be one of: "mispar_hechrachi",
                "mispar_gadol". Defaults to "mispar_hechrachi".
        osis_ref: Optional OSIS reference (e.g., "Gen.4.2") to attach to result.

    Returns:
        GematriaPhraseResult with computed gematria value and metadata.

    Raises:
        ValueError: If system name is not in the list of supported systems.

    Examples:
        >>> result = compute_phrase_gematria("אדם")
        >>> result.value
        45
        >>> result.normalized
        'אדם'
        >>> result.letters
        ['א', 'ד', 'ם']

        >>> result = compute_phrase_gematria("הבל", osis_ref="Gen.4.2")
        >>> result.value
        37
        >>> result.osis_ref
        'Gen.4.2'

        >>> result = compute_phrase_gematria("אדם", system="mispar_gadol")
        >>> result.value  # Final mem (ם) = 600 in Gadol
        605

        >>> result = compute_phrase_gematria("")  # Empty string
        >>> result.value
        0
        >>> result.normalized
        ''
        >>> result.letters
        []
    """
    # Validate system name
    valid_systems = core.system_names()
    if system not in valid_systems:
        raise ValueError(f"Invalid system '{system}'. Must be one of: {', '.join(valid_systems)}")

    # Handle edge cases: None or empty text
    if not text:
        return GematriaPhraseResult(
            text=text or "",
            normalized="",
            letters=[],
            system=system,
            value=0,
            osis_ref=osis_ref,
        )

    # Normalize Hebrew text (handles mixed scripts, diacritics, punctuation)
    normalized = hebrew.normalize_hebrew(text)

    # Extract Hebrew letters
    letters = hebrew.letters_from_text(normalized)

    # Compute gematria value using specified system
    value = core.gematria_value(letters, system=system)

    return GematriaPhraseResult(
        text=text,
        normalized=normalized,
        letters=list(letters),
        system=system,
        value=value,
        osis_ref=osis_ref,
    )
