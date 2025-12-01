from __future__ import annotations

import json, os, subprocess, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[3]

SCRIPT = ROOT / "scripts" / "guards" / "guard_exports_rfc3339.py"

VERDICT = ROOT / "evidence" / "exports_rfc3339.verdict.json"


def _run(env=None):
    e = dict(os.environ)

    if env:
        e.update(env)

    return subprocess.run([sys.executable, str(SCRIPT)], cwd=str(ROOT), env=e, capture_output=True, text=True)


def _load():
    assert VERDICT.exists(), "missing rfc3339 verdict"

    return json.loads(VERDICT.read_text())


def test_hint_mode_passes_and_writes_verdict():
    cp = _run()

    assert cp.returncode == 0, cp.stderr

    v = _load()

    assert v["strict"] is False

    assert v["ok"] is True

    for _k, f in v["files"].items():
        assert f["exists"] is True

        assert f["has_generated_at"] is True

        assert f["rfc3339_ok"] is True


def test_strict_tag_context_passes():
    cp = _run({"STRICT_TAG_CONTEXT": "1"})

    assert cp.returncode == 0, cp.stderr

    v = _load()

    assert v["strict"] is True

    assert v["ok"] is True


def test_strict_fails_on_bad_timestamp(tmp_path, monkeypatch):
    # Temporarily rewrite one export with a bad generated_at (space instead of 'T')

    p = ROOT / "exports" / "graph_stats.json"

    obj = json.loads(p.read_text())

    obj["generated_at"] = "2025-01-01 00:00:00Z"

    backup = p.read_text()

    try:
        p.write_text(json.dumps(obj))

        cp = _run({"STRICT_TAG_CONTEXT": "1"})

        assert cp.returncode != 0, "STRICT should fail on bad timestamp"

        v = _load()

        assert v["ok"] is False

        assert v["files"]["graph_stats.json"]["rfc3339_ok"] is False

    finally:
        p.write_text(backup)
