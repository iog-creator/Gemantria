from __future__ import annotations

import json, os, subprocess, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts" / "guards" / "guard_exports_json.py"
EVIDENCE = ROOT / "evidence" / "exports_guard.verdict.json"

def _run(env=None) -> subprocess.CompletedProcess:
    env2 = dict(os.environ)
    if env: env2.update(env)
    return subprocess.run([sys.executable, str(SCRIPT)], cwd=str(ROOT), env=env2,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

def _load_verdict():
    assert EVIDENCE.exists(), f"missing verdict at {EVIDENCE}"
    return json.loads(EVIDENCE.read_text())

def test_hint_mode_schema_passes_and_writes_verdict(tmp_path):
    # HINT mode (no STRICT vars): should exit 0, write verdict, strict:false
    cp = _run()
    assert cp.returncode == 0, cp.stderr
    v = _load_verdict()
    assert v["ok"] is True
    assert v["strict"] is False
    # All tracked files present with json_ok True; schema_ok should be True now that schemas are committed
    files = v["files"]
    for name in ("graph_latest.scored.json","ai_nouns.json","graph_stats.json","graph_patterns.json"):
        assert name in files, f"{name} missing in verdict"
        f = files[name]
        assert f["exists"] is True
        assert f["json_ok"] is True
        assert f["schema_ok"] is True

def test_strict_tag_context_succeeds_with_schema(tmp_path):
    # STRICT simulated via STRICT_TAG_CONTEXT=1
    cp = _run(env={"STRICT_TAG_CONTEXT":"1"})
    assert cp.returncode == 0, cp.stderr
    v = _load_verdict()
    assert v["ok"] is True
    assert v["strict"] is True
    # sanity: at least 4 schema_ok True
    assert sum(1 for f in v["files"].values() if f["schema_ok"]) >= 4
