import json
import pathlib
import subprocess


def sh(cmd, env=None):
    return subprocess.check_output(cmd, shell=True, text=True, env=env)


def test_e56_atlas_index_summary_receipt():
    sh("make -s m12.proofs")
    p = pathlib.Path("share/atlas/index_summary.json")
    assert p.exists()
    data = json.loads(p.read_text())
    assert data["schema"]["id"] == "atlas.index_summary.v1"
    assert data["chips_total"] >= 0 and data["nodes_total"] >= 0


def test_e57_chip_coverage_consistency_across_pages():
    sh("make -s m12.proofs")
    v = json.loads(pathlib.Path("evidence/guard_m12_chip_coverage.verdict.json").read_text())
    assert v["ok"] is True and v["chip_count"] >= 0


def test_e58_trace_badge_presence_on_index():
    sh("make -s m12.proofs")
    b = json.loads(pathlib.Path("share/atlas/badges/trace.json").read_text())
    assert b["schema"]["id"] == "atlas.badge.trace.v1" and "present" in b


def test_e59_filter_apply_roundtrip_guard():
    sh("make -s m12.proofs")
    v = json.loads(
        pathlib.Path("evidence/guard_m12_filter_apply_roundtrip.verdict.json").read_text()
    )
    assert v["ok"] is True


def test_e60_share_manifest_linkage_receipt():
    sh("make -s m12.proofs")
    m = json.loads(pathlib.Path("share/manifest_linkage.json").read_text())
    assert m["schema"]["id"] == "share.manifest_linkage.v1"
    paths = {it["path"] for it in m["links"]}
    assert "share/atlas/sitemap.json" in paths and "share/atlas/index_summary.json" in paths
