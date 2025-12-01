import os, re


def _maybe(paths):
    for p in paths:
        if p and os.path.exists(p):
            return p
    return None


def test_e29_node_page_embeds_audit_json_script_tag():
    node0 = _maybe(["share/atlas/nodes/0.html"])
    assert node0, "node page missing (staged)"
    html = open(node0, encoding="utf-8").read()
    assert re.search(r'<script[^>]+id="audit-json"[^>]+type="application/json"', html) or re.search(
        r'<script[^>]+type="application/json"[^>]+id="audit-json"', html
    ), "no audit JSON embed (staged)"


def test_e30_node_page_has_cross_batch_jump_links():
    node0 = _maybe(["share/atlas/nodes/0.html"])
    assert node0, "node page missing (staged)"
    html = open(node0, encoding="utf-8").read()
    # Expect link(s) to other batches/graphs, e.g., href="../jumpers/idx/0.html" or data-jump="..."
    assert ("jumpers" in html) or re.search(
        r'href="..\/jumpers\/', html
    ), "no cross-batch jumper link (staged)"


def test_e31_jumper_index_exists_when_exports_present():
    idx = _maybe(["share/atlas/jumpers/index.html"])
    assert idx, "jumper index missing (staged)"
