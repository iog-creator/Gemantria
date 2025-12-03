from __future__ import annotations

"""BibleScholar Gematria flow (read-only).

This module defines a small, testable pipeline hook that BibleScholar can use
to compute Gematria values for Bible verses or phrases using the underlying
AgentPM Gematria module.

It is intentionally:
- read-only (no DB or control-plane writes),
- synchronous and deterministic,
- narrow in scope (Gematria only).

See:
- docs/SSOT/BIBLESCHOLAR_INTAKE.md
- docs/SSOT/AGENTPM_GEMATRIA_MODULE_PLAN.md
- pmagent/biblescholar/AGENTS.md
"""

from dataclasses import dataclass
from typing import Iterable, Mapping

from pmagent.biblescholar.gematria_adapter import (
    GematriaPhraseResult,
    compute_phrase_gematria,
)
from pmagent.modules.gematria import core


@dataclass
class VerseGematriaSummary:
    """Summary of Gematria values for a verse across one or more systems.

    Attributes:
        osis_ref: OSIS reference for the verse (e.g., "Gen.2.7").
        text: Original verse text.
        systems: Mapping from system name to GematriaPhraseResult for that system.
    """

    osis_ref: str
    text: str
    systems: Mapping[str, GematriaPhraseResult]


def supported_gematria_systems() -> list[str]:
    """Return the list of Gematria systems that this flow will compute.

    Returns:
        List of supported system names (e.g., ["mispar_hechrachi", "mispar_gadol"]).

    Examples:
        >>> systems = supported_gematria_systems()
        >>> "mispar_hechrachi" in systems
        True
        >>> "mispar_gadol" in systems
        True
    """
    return core.system_names()


def compute_verse_gematria(
    text: str,
    osis_ref: str,
    systems: Iterable[str] | None = None,
) -> VerseGematriaSummary:
    """Compute Gematria for a verse across one or more numerics systems.

    This is a pure, read-only function: it only calls Gematria helpers and
    returns a dataclass summary. No database writes, no control-plane mutations,
    no LM calls.

    Args:
        text: Hebrew verse text (may contain diacritics, punctuation, mixed scripts).
        osis_ref: OSIS reference for the verse (e.g., "Gen.2.7").
        systems: Optional list of system names to compute. If None, uses all
                 supported systems from `supported_gematria_systems()`.

    Returns:
        VerseGematriaSummary with computed Gematria values for each requested system.

    Raises:
        ValueError: If any system name in `systems` is not supported (propagated
                    from `compute_phrase_gematria`).

    Examples:
        >>> summary = compute_verse_gematria("אדם", "Gen.2.7", ["mispar_hechrachi"])
        >>> summary.osis_ref
        'Gen.2.7'
        >>> summary.systems["mispar_hechrachi"].value
        45

        >>> summary = compute_verse_gematria("הבל", "Gen.4.2")
        >>> # Uses all supported systems by default
        >>> "mispar_hechrachi" in summary.systems
        True
        >>> "mispar_gadol" in summary.systems
        True
    """
    if systems is None:
        systems = supported_gematria_systems()

    results: dict[str, GematriaPhraseResult] = {}
    for system in systems:
        phrase_result = compute_phrase_gematria(
            text=text,
            system=system,
            osis_ref=osis_ref,
        )
        results[system] = phrase_result

    return VerseGematriaSummary(
        osis_ref=osis_ref,
        text=text,
        systems=results,
    )
