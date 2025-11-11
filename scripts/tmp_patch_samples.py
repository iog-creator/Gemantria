#!/usr/bin/env python3
"""Patch sample JSON files to SSOT envelopes (safe transforms only)."""

import datetime
import json
import os
import pathlib
import shutil


def wrap_ai_nouns_array(path):
    """Wrap array or add missing envelope fields to ai-nouns JSON."""
    with open(path, encoding="utf-8") as f:
        try:
            data = json.load(f)
        except Exception as e:
            return False, f"invalid JSON: {e}"

    if isinstance(data, list):
        obj = {
            "schema": "SSOT_ai-nouns.v1",
            "book": "SAMPLE",
            "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
            "nodes": data,
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=2, ensure_ascii=False)
        return True, "wrapped list->envelope"
    elif isinstance(data, dict):
        changed = False
        if "schema" not in data:
            data["schema"] = "SSOT_ai-nouns.v1"
            changed = True
        if "book" not in data:
            data["book"] = "SAMPLE"
            changed = True
        if "generated_at" not in data:
            data["generated_at"] = datetime.datetime.utcnow().isoformat() + "Z"
            changed = True
        if "nodes" not in data:
            data["nodes"] = []
            changed = True
        if changed:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True, "added missing envelope fields"
        return False, "already envelope"
    return False, "unexpected type"


def main():
    changes = []

    # 5a) evidence/ai_nouns.sample.json — wrap if list
    if os.path.exists("evidence/ai_nouns.sample.json"):
        ok, msg = wrap_ai_nouns_array("evidence/ai_nouns.sample.json")
        changes.append(("evidence/ai_nouns.sample.json", ok, msg))

    # 5b) evidence/guard_ai_nouns_xrefs.json — ensure envelope keys
    if os.path.exists("evidence/guard_ai_nouns_xrefs.json"):
        ok, msg = wrap_ai_nouns_array("evidence/guard_ai_nouns_xrefs.json")
        changes.append(("evidence/guard_ai_nouns_xrefs.json", ok, msg))

    # 5c) ui/out/graph_correlations.json — ensure minimal correlations envelope
    if os.path.exists("ui/out/graph_correlations.json"):
        try:
            with open("ui/out/graph_correlations.json", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}
        if not isinstance(data, dict):
            data = {}
        changed = False
        if "correlations" not in data:
            data["correlations"] = []
            changed = True
        if "metadata" not in data:
            data["metadata"] = {
                "schema": "SSOT_graph-correlations.v1",
                "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
            }
            changed = True
        if changed:
            with open("ui/out/graph_correlations.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            changes.append(("ui/out/graph_correlations.json", True, "added minimal correlations envelope"))
        else:
            changes.append(("ui/out/graph_correlations.json", False, "ok"))

    # 5d) share/graph_stats.head.json — if ambiguous, quarantine rather than guess
    if os.path.exists("share/graph_stats.head.json"):
        new_dir = "share/quarantined"
        pathlib.Path(new_dir).mkdir(parents=True, exist_ok=True)
        shutil.move("share/graph_stats.head.json", f"{new_dir}/graph_stats.head.json")
        changes.append(("share/graph_stats.head.json", True, "moved to share/quarantined/ (ambiguous schema)"))

    # Emit a small report
    report = {"changes": changes}
    pathlib.Path("evidence").mkdir(parents=True, exist_ok=True)
    with open("evidence/data_fix_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
