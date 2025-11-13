from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

BADGES_PATH = Path("share/atlas/badges/reranker.json")
VERDICT_PATH = Path("evidence/guard_m14_reranker_badges.verdict.json")


def verdict(ok: bool, **extra: Any) -> int:
    VERDICT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload: Dict[str, Any] = {"ok": ok, **extra}
    VERDICT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0 if ok else 1


def main() -> int:
    if not BADGES_PATH.exists():
        return verdict(False, error="missing_reranker_badges", path=str(BADGES_PATH))

    try:
        data = json.loads(BADGES_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        return verdict(False, error="invalid_json", detail=str(e))

    # Check top-level keys
    required_keys = {"schema", "generated_at", "mode", "items", "ok"}
    if not required_keys.issubset(data.keys()):
        return verdict(False, error="missing_top_level_keys", keys=list(data.keys()))

    # Check schema
    schema = data.get("schema", {})
    if schema.get("id") != "atlas.badges.reranker.v1":
        return verdict(False, error="bad_schema_id", value=schema.get("id"))
    if not isinstance(schema.get("version"), int) or schema["version"] != 1:
        return verdict(False, error="bad_schema_version", value=schema.get("version"))

    # Check mode
    mode = data.get("mode", "").upper()
    if mode not in ("HINT", "STRICT"):
        return verdict(False, error="bad_mode", value=mode)

    # Check items
    items = data.get("items", [])
    if not isinstance(items, list):
        return verdict(False, error="items_not_list", value=type(items).__name__)

    min_items = 3 if mode == "HINT" else 1
    if len(items) < min_items:
        return verdict(False, error="insufficient_items", count=len(items), min_required=min_items)

    # Validate each item
    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            return verdict(False, error="item_not_dict", index=idx)

        # Check required fields
        node_id = item.get("node_id")
        if not isinstance(node_id, str) or not node_id:
            return verdict(False, error="bad_node_id", index=idx, value=node_id)

        score = item.get("score")
        if not isinstance(score, (int, float)) or not (0.0 <= float(score) <= 1.0):
            return verdict(False, error="bad_score", index=idx, value=score)

        badge = item.get("badge")
        if badge not in ("high", "med", "low"):
            return verdict(False, error="bad_badge_value", index=idx, value=badge)

        thresholds = item.get("thresholds")
        if not isinstance(thresholds, dict):
            return verdict(False, error="bad_thresholds", index=idx, value=thresholds)
        if "high" not in thresholds or "med" not in thresholds:
            return verdict(False, error="missing_threshold_keys", index=idx, keys=list(thresholds.keys()))

        # Validate badge classification matches rule
        score_val = float(score)
        thresh_high = float(thresholds["high"])
        thresh_med = float(thresholds["med"])

        expected_badge = "high" if score_val >= thresh_high else ("med" if score_val >= thresh_med else "low")
        if badge != expected_badge:
            return verdict(
                False,
                error="badge_classification_mismatch",
                index=idx,
                node_id=node_id,
                score=score_val,
                badge=badge,
                expected=expected_badge,
            )

    # Check sorting by node_id
    if len(items) > 1:
        for i in range(len(items) - 1):
            if items[i]["node_id"] > items[i + 1]["node_id"]:
                return verdict(False, error="not_sorted_by_node_id", index=i)

    return verdict(True, count=len(items), sorted_by="node_id", schema=schema, mode=mode)


if __name__ == "__main__":
    raise SystemExit(main())

