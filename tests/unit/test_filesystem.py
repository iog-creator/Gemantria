from pathlib import Path

import pytest

from src.infra import read_text


def test_read_text(tmp_path: Path) -> None:
    file_path = tmp_path / "sample.txt"
    file_path.write_text("hello", encoding="utf-8")

    assert read_text(file_path) == "hello"


def test_read_text_empty_file(tmp_path: Path) -> None:
    file_path = tmp_path / "sample.txt"
    file_path.write_text("   \n", encoding="utf-8")

    with pytest.raises(ValueError):
        read_text(file_path)
