import json, os, pathlib, subprocess


def sh(cmd, env=None):
    return subprocess.check_output(cmd, shell=True, text=True, env=env)


def test_e46_atlas_sitemap_receipt():
    sh("make -s m10.proofs")
    p = pathlib.Path("share/atlas/sitemap.json")
    assert p.exists(), "sitemap.json missing"
    data = json.loads(p.read_text())
    assert data["schema"]["id"] == "atlas.sitemap.v1"
    assert isinstance(data["entries"], list) and len(data["entries"]) >= 1


def test_e47_chip_multiquery_map_receipt():
    sh("make -s m10.proofs")
    p = pathlib.Path("share/atlas/filter_apply_multi.json")
    data = json.loads(p.read_text())
    assert data["schema"]["id"] == "atlas.filter_apply_multi.v1"
    assert isinstance(data["items"][0]["queries"], list) and len(data["items"][0]["queries"]) >= 2


def test_e48_trace_backlink_integrity():
    sh("make -s m10.proofs")
    v = json.loads(pathlib.Path("evidence/m10_trace_backlink.verdict.json").read_text())
    assert v["ok"] is True


def test_e49_node_drilldown_coverage_receipt():
    sh("make -s m10.proofs")
    p = pathlib.Path("share/atlas/nodes/node_001/coverage.json")
    data = json.loads(p.read_text())
    assert data["schema"]["id"] == "atlas.node_coverage.v1"
    assert data["counts"]["files_present"] >= 1


def test_e50_filter_apply_drift_guard_receipt():
    sh("make -s m10.proofs")
    fresh = json.loads(pathlib.Path("evidence/guard_m10_filter_apply_drift.verdict.json").read_text())
    assert fresh["ok"] is True
    # forced drift path
    env = dict(os.environ)
    env["M10_DRIFT_FORCE"] = "1"
    out = sh("python3 scripts/guards/guard_m10_filter_apply_drift.py", env=env)
    forced = json.loads(out)
    assert forced["ok"] is False and forced["forced"] is True
