from __future__ import annotations

"""Gematria / numerics verification helpers (skeleton)."""

from dataclasses import dataclass
from typing import Iterable


@dataclass
class VerificationResult:
    ok: bool
    message: str = ""


def verify_value(letters: Iterable[str], expected: int) -> VerificationResult:
    """Verify that the calculated value for letters matches the expected value.

    Stub implementation; eventually this will call into core.gematria_value and
    collect richer diagnostics.
    """
    raise NotImplementedError("verify_value is not yet implemented; see Gematria module plan.")
