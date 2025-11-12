import json, os, re, subprocess, pathlib


def run(cmd):
    return subprocess.check_output(cmd, shell=True, text=True).strip()


def test_e36_db_filter_ui_chips_receipt():
    run("make -s m8.proofs")
    p = pathlib.Path("share/atlas/filter_chips.json")
    assert p.exists(), "filter_chips.json missing"
    data = json.loads(p.read_text())
    assert data["schema"]["id"] == "atlas.filter_chips.v1"
    assert re.match(r"^\d{4}-\d{2}-\d{2}T", data["generated_at"])
    assert isinstance(data["items"], list) and len(data["items"]) >= 1
    assert {"id", "label", "type"}.issubset(data["items"][0].keys())


def test_e37_per_node_provenance_rollups():
    run("make -s m8.proofs")
    p = pathlib.Path("share/atlas/nodes/node_001/provenance.json")
    assert p.exists(), "provenance.json missing"
    data = json.loads(p.read_text())
    assert data["schema"]["id"] == "atlas.node_provenance.v1"
    assert data["node_id"] == "node_001"
    assert "filter_chip_ids" in data and len(data["filter_chip_ids"]) >= 1


def test_e38_cross_page_chip_propagation():
    run("make -s m8.proofs")
    chips = json.loads(pathlib.Path("share/atlas/filter_chips.json").read_text())
    roll = json.loads(pathlib.Path("share/atlas/nodes/node_001/provenance.json").read_text())
    chip_ids = {it["id"] for it in chips["items"]}
    assert any(cid in chip_ids for cid in roll["filter_chip_ids"]), "chip IDs must propagate index↔node"


def test_e39_db_filter_query_smoke_receipt():
    run("make -s m8.proofs")
    r = json.loads(pathlib.Path("evidence/m8_db_probe.receipt.json").read_text())
    assert r["ok"] is True
    assert r["mode"] in {"HINT", "STRICT"}
    assert "dsn_present" in r


def test_e40_stale_evidence_guard_receipt():
    run("make -s m8.proofs")
    fresh = json.loads(pathlib.Path("evidence/guard_m8_stale.verdict.json").read_text())
    assert fresh["ok"] is True, f"expected fresh evidence (threshold default), got: {fresh}"
    # Force stale verdict by setting threshold to 0 for a rerun
    env = dict(os.environ)
    env["M8_STALE_THRESHOLD_SECONDS"] = "0"
    out = subprocess.check_output("python3 scripts/guards/guard_m8_stale.py", shell=True, text=True, env=env)
    forced = json.loads(out)
    assert forced["stale"] is True and forced["ok"] is False
