import json, os, pathlib, subprocess


def run(cmd: str):
    return subprocess.check_output(cmd, shell=True, text=True).strip()


def test_e41_filter_chip_click_to_query():
    run("make -s m9.proofs")
    p = pathlib.Path("share/atlas/filter_apply.json")
    assert p.exists(), "filter_apply.json missing"
    data = json.loads(p.read_text())
    assert data["schema"]["id"] == "atlas.filter_apply.v1"
    item = data["items"][0]
    assert item["chip_id"] and item["query"]["kind"] == "sql" and "SELECT" in item["query"]["text"]


def test_e42_rollup_panel_consistency():
    run("make -s m9.proofs")
    chips = json.loads(pathlib.Path("share/atlas/filter_chips.json").read_text())
    roll = json.loads(pathlib.Path("share/atlas/nodes/node_001/provenance.json").read_text())
    assert roll["counts"]["chips"] == len(chips["items"])
    assert set(roll["filter_chip_ids"]).issuperset({it["id"] for it in chips["items"]})


def test_e43_node_page_backlinks_index():
    run("make -s m9.proofs")
    roll = json.loads(pathlib.Path("share/atlas/nodes/node_001/provenance.json").read_text())
    links = {(it.get("rel"), it.get("href")) for it in roll.get("backlinks", [])}
    assert ("index", "../../index.html") in links


def test_e44_db_probe_latency_badge_threshold():
    run("make -s m9.proofs")
    p = pathlib.Path("share/atlas/badges/latency.json")
    data = json.loads(p.read_text())
    assert data["schema"]["id"] == "atlas.badge.latency.v1"
    assert data["measured_ms"] <= data["threshold_ms"]
    # Force fail path: threshold = 0
    env = dict(os.environ)
    env["M9_LATENCY_THRESHOLD_MS"] = "0"
    out = subprocess.check_output("python3 scripts/mcp/probe_db_latency.py", shell=True, text=True, env=env)
    forced = json.loads(out)
    assert forced["ok"] is False and forced["threshold_ms"] == 0


def test_e45_guard_rollup_staleness_window():
    run("make -s m9.proofs")
    fresh = json.loads(pathlib.Path("evidence/guard_m9_rollup_stale.verdict.json").read_text())
    assert fresh["ok"] is True
    # Force stale
    env = dict(os.environ)
    env["M9_ROLLUP_STALE_THRESHOLD_SECONDS"] = "0"
    out = subprocess.check_output("python3 scripts/guards/guard_m9_rollup_stale.py", shell=True, text=True, env=env)
    forced = json.loads(out)
    assert forced["stale"] is True and forced["ok"] is False
