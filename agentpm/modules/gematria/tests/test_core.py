from __future__ import annotations

import pytest

from agentpm.modules.gematria import core


def test_system_names_includes_default() -> None:
    assert "mispar_hechrachi" in core.system_names()


def test_gematria_value_not_implemented() -> None:
    with pytest.raises(NotImplementedError) as exc:
        core.gematria_value(["א"])
    assert "not yet implemented" in str(exc.value)
