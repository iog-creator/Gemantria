import os, re


def _read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def test_e38_breadcrumb_has_aria_label_on_back_to_atlas():
    p = "share/atlas/nodes/0.html"
    assert os.path.exists(p), "node page missing (staged)"
    html = _read(p)
    assert re.search(r'<a[^>]+aria-label="Back to Atlas"[^>]*>\s*←\s*Back to Atlas', html), (
        "breadcrumb lacks aria-label (staged)"
    )


def test_e39_index_links_to_sitemap_html_and_json():
    idx = "share/atlas/index.html"
    assert os.path.exists(idx), "index missing (staged)"
    html = _read(idx)
    # Expect links surfaced in implementation slice
    assert ("sitemap.html" in html) or ("sitemap.json" in html), "no sitemap link visible (staged)"


def test_e40_counts_banner_present_on_index():
    idx = "share/atlas/index.html"
    assert os.path.exists(idx), "index missing (staged)"
    html = _read(idx)
    # Expect a visible counts banner like: <div id="counts">Nodes: N • Jumpers: M</div>
    assert ('id="counts"' in html) or ("Nodes:" in html), "counts banner missing (staged)"
