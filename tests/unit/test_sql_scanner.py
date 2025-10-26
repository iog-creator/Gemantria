import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]  # repo root
SRC = ROOT / "src"

# Forbid f-strings in SQL .execute("...") calls.
PATTERN = re.compile(r"\.execute\(\s*f['\"]", re.I)


def test_no_fstrings_in_execute_calls():
    offenders = []
    for py in SRC.rglob("*.py"):
        text = py.read_text(encoding="utf-8")
        if PATTERN.search(text):
            offenders.append(str(py.relative_to(ROOT)))
    assert not offenders, f"F-strings found in DB execute calls: {offenders}"
