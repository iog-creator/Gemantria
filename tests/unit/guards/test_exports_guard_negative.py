from __future__ import annotations

import json, os, shutil, subprocess, sys, pathlib

REPO = pathlib.Path(__file__).resolve().parents[3]

def _mini_repo(tmp: pathlib.Path) -> tuple[pathlib.Path, pathlib.Path]:
    # Create minimal repo layout in tmp (scripts/guards, schemas, exports, evidence/)
    (tmp / "scripts" / "guards").mkdir(parents=True, exist_ok=True)
    (tmp / "schemas").mkdir(parents=True, exist_ok=True)
    (tmp / "exports").mkdir(parents=True, exist_ok=True)
    (tmp / "evidence").mkdir(exist_ok=True)
    # copy guard scripts
    for name in ("guard_exports_json.py", "jsonschema_min.py"):
        shutil.copy(REPO / "scripts" / "guards" / name, tmp / "scripts" / "guards" / name)
    # copy schemas
    for name in ("ai-nouns.schema.json","graph-stats.schema.json","graph-patterns.schema.json","graph.schema.json"):
        shutil.copy(REPO / "schemas" / name, tmp / "schemas" / name)
    # copy exports
    for name in ("graph_latest.scored.json","ai_nouns.json","graph_stats.json","graph_patterns.json"):
        shutil.copy(REPO / "exports" / name, tmp / "exports" / name)
    return tmp / "scripts" / "guards" / "guard_exports_json.py", tmp

def _run_guard(script: pathlib.Path, cwd: pathlib.Path, **env):
    e = dict(os.environ)
    e.update(env)
    return subprocess.run([sys.executable, str(script)], cwd=str(cwd),
                          capture_output=True, text=True, env=e)

def test_strict_fails_on_schema_violation_graph_stats(tmp_path):
    script, root = _mini_repo(tmp_path)
    # Break schema: remove required 'edges' property
    p = root / "exports" / "graph_stats.json"
    obj = json.loads(p.read_text())
    del obj["edges"]  # remove required property
    p.write_text(json.dumps(obj))
    cp = _run_guard(script, root, STRICT_TAG_CONTEXT="1")
    assert cp.returncode != 0, f"expected STRICT failure, got rc={cp.returncode}\nSTDERR:\n{cp.stderr}"
    verdict = json.loads((root / "evidence" / "exports_guard.verdict.json").read_text())
    assert verdict["ok"] is False
    assert verdict["files"]["graph_stats.json"]["schema_ok"] is False

def test_strict_fails_when_export_missing(tmp_path):
    script, root = _mini_repo(tmp_path)
    # Remove one export entirely
    (root / "exports" / "ai_nouns.json").unlink()
    cp = _run_guard(script, root, STRICT_TAG_CONTEXT="1")
    assert cp.returncode != 0, f"expected STRICT failure, got rc={cp.returncode}\nSTDERR:\n{cp.stderr}"
    verdict = json.loads((root / "evidence" / "exports_guard.verdict.json").read_text())
    assert verdict["ok"] is False
    assert verdict["files"]["ai_nouns.json"]["exists"] is False
