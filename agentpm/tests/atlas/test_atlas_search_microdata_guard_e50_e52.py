import json, re, pathlib, pytest


xfail_reason = "Staged TVs for E50–E52 (implementation pending)"
pytestmark = pytest.mark.xfail(reason=xfail_reason, strict=False)


ROOT = pathlib.Path("share/atlas")


def _read(p: pathlib.Path) -> str:
    return p.read_text(encoding="utf-8")


def test_e50_index_has_search_filter_wiring():
    """Search box & filter wiring smoke: quick-filters + behavior hook present."""
    idx = _read(ROOT / "index.html")
    assert 'id="quick-filters"' in idx
    assert 'data-behavior="toggle-filters"' in idx
    assert 'role="search"' in idx


def test_e51_breadcrumb_has_microdata_schema():
    """Breadcrumb exposes schema.org microdata (BreadcrumbList/ListItem)."""
    n0 = _read(ROOT / "nodes" / "0.html")
    assert 'itemscope' in n0 and 'itemtype="https://schema.org/BreadcrumbList"' in n0
    assert 'itemprop="itemListElement"' in n0


def test_e52_sitemap_has_crosscheck_guard_data():
    """sitemap.json exposes anchors we can cross-check later against page ids."""
    data = json.loads((ROOT / "sitemap.json").read_text(encoding="utf-8"))
    anchors = data.get("anchors", [])
    assert isinstance(anchors, list) and anchors, "anchors list should be non-empty"

