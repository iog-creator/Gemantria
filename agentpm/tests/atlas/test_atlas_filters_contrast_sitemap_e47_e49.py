import json, pathlib

ROOT = pathlib.Path("share/atlas")


def _html(p):
    return ROOT.joinpath(p).read_text(encoding="utf-8")


def test_e47_index_filters_behavior_smoke():
    # Expect a behavior hook to exist before enabling (to avoid flaky XPASS)
    html = _html("index.html")
    assert 'data-behavior="toggle-filters"' in html


def test_e48_breadcrumb_aria_current_contrast():
    # Expect a 'current' class to be present on aria-current chip for contrast styling
    html = _html("nodes/0.html")
    assert '<span aria-current="page" class="current">' in html


def test_e49_sitemap_anchors_audit():
    # Expect anchors list in sitemap.json (not present yet in hermetic slice)
    data = json.loads(ROOT.joinpath("sitemap.json").read_text(encoding="utf-8"))
    assert isinstance(data.get("anchors"), list) and data["anchors"], "anchors list required"
