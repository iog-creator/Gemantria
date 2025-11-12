import pytest, pathlib


xfail_reason = "Staged TVs for E41-E43 (search box, title suffixes, ARIA landmarks)"

pytestmark = pytest.mark.xfail(reason=xfail_reason, strict=False)


def _read(path):
    return pathlib.Path(path).read_text(encoding="utf-8")


def test_e41_index_has_search_box():
    html = _read("share/atlas/index.html")
    assert ("<input" in html and 'id="search"' in html) or ('role="search"' in html)


def test_e42_pages_have_title_suffix():
    idx = _read("share/atlas/index.html")
    assert "Atlas — Index" in idx or "— Atlas" in idx


def test_e43_pages_have_aria_landmarks():
    idx = _read("share/atlas/index.html")
    assert ('role="main"' in idx) or ("<main" in idx)
