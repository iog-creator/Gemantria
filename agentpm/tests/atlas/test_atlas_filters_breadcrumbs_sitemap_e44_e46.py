import json, pytest, pathlib


@pytest.mark.xfail(reason="staged (expected fail)", strict=True)
def test_e44_index_has_quick_filters():
    html = pathlib.Path("share/atlas/index.html").read_text(encoding="utf-8")
    assert ('id="quick-filters"' in html) or ("data-quick-filters" in html)


@pytest.mark.xfail(reason="staged (expected fail)", strict=True)
def test_e45_node_breadcrumb_has_aria_current():
    html = pathlib.Path("share/atlas/nodes/0.html").read_text(encoding="utf-8")
    assert 'aria-current="page"' in html


def test_e46_sitemap_json_schema():
    data = json.loads(pathlib.Path("share/atlas/sitemap.json").read_text(encoding="utf-8"))
    assert isinstance(data.get("nodes_count"), int)
    assert isinstance(data.get("jumpers_count"), int)
    files = data.get("files") or {}
    assert "index" in files and "graph" in files and "nodes_dir" in files
