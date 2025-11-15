from __future__ import annotations

"""Hebrew text normalization and mapping utilities (skeleton)."""

from typing import Iterable


def normalize_hebrew(text: str) -> str:
    """Normalize a raw Hebrew string into the canonical form used for numerics.

    Placeholder stub; real behavior will follow the SSOT normalization rules
    (NFKD -> strip combining marks and punctuation -> NFC).
    """
    raise NotImplementedError("normalize_hebrew is not yet implemented; see Gematria module plan.")


def letters_from_text(text: str) -> list[str]:
    """Extract normalized Hebrew letters from the input text.

    Skeleton stub for future extraction logic.
    """
    raise NotImplementedError("letters_from_text is not yet implemented; see Gematria module plan.")


def letters_to_value(letters: Iterable[str]) -> int:
    """Helper that delegates to core.gematria_value.

    Kept thin so math logic stays in core.
    """
    from . import core

    return core.gematria_value(list(letters))
