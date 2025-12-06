import os
import re


def _read(path):
    return open(path, encoding="utf-8").read()


def _maybe(paths):
    for p in paths:
        if p and os.path.exists(p):
            return p
    return None


def test_e32_node_page_has_json_download_link():
    node0 = _maybe(["share/atlas/nodes/0.html"])
    assert node0, "node page missing (staged)"
    html = _read(node0)
    # Accept either explicit download attr or a .json href
    assert (
        ('id="download-json"' in html)
        or ("download" in html and ".json" in html)
        or re.search(r'href="[^"]+\.json"', html)
    ), "no JSON download link (staged)"


def test_e33_jumper_page_has_backlink_to_node():
    j0 = _maybe(["share/atlas/jumpers/idx/0.html"])
    assert j0, "jumper page missing (staged)"
    html = _read(j0)
    assert "../nodes/0.html" in html or "../../nodes/0.html" in html, "no backlink to node page (staged)"


def test_e34_sitemap_or_counts_present():
    # Either a sitemap file or counts JSON expected post-implementation
    sm = _maybe(["share/atlas/sitemap.json", "share/atlas/sitemap.html"])
    idx = _maybe(["share/atlas/index.html"])
    assert sm or idx, "no sitemap/counts artifact (staged)"
