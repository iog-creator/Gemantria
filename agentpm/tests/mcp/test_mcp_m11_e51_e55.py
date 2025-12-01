import json
import os
import pathlib
import subprocess


def sh(cmd, env=None):
    return subprocess.check_output(cmd, shell=True, text=True, env=env)


def test_e51_atlas_breadcrumbs_receipt():
    sh("make -s m11.proofs")
    p = pathlib.Path("share/atlas/breadcrumbs.json")
    assert p.exists(), "breadcrumbs.json missing"
    data = json.loads(p.read_text())
    assert data["schema"]["id"] == "atlas.breadcrumbs.v1"
    assert any(c["href"] == "index.html" for c in data["breadcrumbs"])


def test_e52_sitemap_index_presence_receipt():
    sh("make -s m11.proofs")
    s = json.loads(pathlib.Path("share/atlas/sitemap.json").read_text())
    assert any(e["href"] == "index.html" and e.get("kind") == "index" for e in s["entries"])


def test_e53_trace_links_integrity_across_nodes():
    sh("make -s m11.proofs")
    v = json.loads(pathlib.Path("evidence/m11_trace_across_nodes.verdict.json").read_text())
    assert v["ok"] is True


def test_e54_node_rollup_totals_consistency():
    sh("make -s m11.proofs")
    r = json.loads(pathlib.Path("evidence/m11_rollup_totals.receipt.json").read_text())
    assert r["ok"] is True


def test_e55_filter_apply_multi_schema_guard():
    sh("make -s m11.proofs")
    fresh = json.loads(
        pathlib.Path("evidence/guard_m11_apply_multi_schema.verdict.json").read_text()
    )
    assert fresh["ok"] is True and fresh["items"] >= 1
    # Force fail by requiring too many queries
    env = dict(os.environ)
    env["M11_APPLY_MULTI_MIN_QUERIES"] = "99"
    out = sh("python3 scripts/guards/guard_m11_filter_apply_multi_schema.py", env=env)
    forced = json.loads(out)
    assert forced["ok"] is False and forced["min_queries"] == 99
