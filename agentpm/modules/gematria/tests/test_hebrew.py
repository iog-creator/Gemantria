from __future__ import annotations

import pytest

from agentpm.modules.gematria import hebrew


def test_normalize_hebrew_not_implemented() -> None:
    with pytest.raises(NotImplementedError):
        hebrew.normalize_hebrew("בראשית")


def test_letters_from_text_not_implemented() -> None:
    with pytest.raises(NotImplementedError):
        hebrew.letters_from_text("בראשית")
