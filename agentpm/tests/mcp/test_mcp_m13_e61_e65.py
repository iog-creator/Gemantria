import json
import os
import pathlib
import subprocess


def sh(cmd, env=None):
    return subprocess.check_output(cmd, shell=True, text=True, env=env)


def test_e61_index_badge_rollup_receipt():
    sh("make -s m13.proofs")
    p = pathlib.Path("share/atlas/badges/index_rollup.json")
    data = json.loads(p.read_text())
    assert data["schema"]["id"] == "atlas.badges.rollup.v1"
    assert data["ok"] is True


def test_e62_chip_id_uniqueness_guard():
    sh("make -s m13.proofs")
    v = json.loads(pathlib.Path("evidence/guard_m13_chip_id_uniqueness.verdict.json").read_text())
    assert v["ok"] is True and v["duplicates_count"] == 0 and v["unknown_in_apply_count"] == 0


def test_e63_sitemap_linkcount_minimum():
    sh("make -s m13.proofs")
    v = json.loads(pathlib.Path("evidence/guard_m13_sitemap_min.verdict.json").read_text())
    assert v["ok"] is True and v["count"] >= v["min_required"]
    # forced-fail path
    env = dict(os.environ)
    env["M13_SITEMAP_MIN"] = "999"
    out = sh("python3 scripts/guards/guard_m13_sitemap_min.py", env=env)
    forced = json.loads(out)
    assert forced["ok"] is False and forced["min_required"] == 999


def test_e64_manifest_linkage_consistency():
    sh("make -s m13.proofs")
    v = json.loads(pathlib.Path("evidence/guard_m13_manifest_consistency.verdict.json").read_text())
    assert v["ok"] is True


def test_e65_global_stale_proofs_sweep_guard():
    sh("make -s m13.proofs")
    fresh = json.loads(pathlib.Path("evidence/guard_m13_stale_sweep.verdict.json").read_text())
    assert fresh["ok"] is True
    # forced-fail path
    env = dict(os.environ)
    env["M13_STALE_FORCE"] = "1"
    out = sh("python3 scripts/guards/guard_m13_stale_sweep.py", env=env)
    forced = json.loads(out)
    assert forced["ok"] is False and forced["forced"] is True
