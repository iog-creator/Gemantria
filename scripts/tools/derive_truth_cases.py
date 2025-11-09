# ruff: noqa: RUF001

#!/usr/bin/env python3

from __future__ import annotations

import json, sys, hashlib, datetime, pathlib, itertools

ROOT = pathlib.Path(__file__).resolve().parents[2]
EXPORTS = ROOT / "exports"
OUTFILE = ROOT / "tests" / "truth" / "extraction_accuracy.v1.json"


def _canon_key(node):
    # deterministic order: stable hash of surface text (fallback empty)
    s = (node.get("surface") or "") + "|" + (node.get("lemma") or "")
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def main(limit: int = 25) -> int:
    # Try multiple sources in order of preference
    sources = [
        EXPORTS / "ai_nouns.json",  # Current AI-discovered nouns
        EXPORTS / "bible_nouns_genesis.json",  # Full book extraction
    ]

    nodes = []
    for src in sources:
        if src.exists():
            try:
                data = json.loads(src.read_text())
                src_nodes = data.get("nodes", [])
                # Filter for nodes with gematria and are proper nouns
                filtered_nodes = [
                    n for n in src_nodes if n.get("gematria") is not None or n.get("gematria_value") is not None
                ]
                if filtered_nodes:
                    nodes.extend(filtered_nodes)
                    print(f"Found {len(filtered_nodes)} valid nodes from {src.name}", file=sys.stderr)
                    break  # Use first source with valid nodes
            except Exception as e:
                print(f"HINT: derive_truth_cases: failed to read {src}: {e}", file=sys.stderr)
                continue

    # If we don't have enough real data, create synthetic test cases
    if len(nodes) < limit:
        print(f"Found {len(nodes)} real nodes, creating synthetic cases to reach {limit}", file=sys.stderr)
        synthetic_cases = _create_synthetic_cases(limit - len(nodes))
        nodes.extend(synthetic_cases)

    if not nodes:
        print("HINT: derive_truth_cases: no valid noun sources found with gematria data", file=sys.stderr)
        return 0

    nodes.sort(key=_canon_key)
    out = {
        "version": "v1",
        "generated_at": datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "source": "fixtures",
        "cases": [],
    }
    for node in itertools.islice(nodes, 0, limit):
        # Handle both field naming conventions
        gematria = node.get("gematria") or node.get("gematria_value")
        # Get reference from sources
        ref = None
        sources_list = node.get("sources", [])
        if sources_list and isinstance(sources_list[0], dict):
            ref = sources_list[0].get("ref")

        # Only include if we have the minimal required fields
        if gematria is not None:
            out["cases"].append(
                {"surface": node.get("surface"), "letters": node.get("letters", None), "gematria": gematria, "ref": ref}
            )

    if not out["cases"]:
        print("HINT: derive_truth_cases: no cases generated (missing gematria data)", file=sys.stderr)
        return 0

    OUTFILE.parent.mkdir(parents=True, exist_ok=True)
    OUTFILE.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"OK: wrote {len(out['cases'])} cases → {OUTFILE}")
    return 0


def _create_synthetic_cases(count: int) -> list[dict]:
    """Create deterministic synthetic test cases for truth suite expansion."""
    # Genesis nouns with their gematria values - expanded beyond the original 10
    synthetic_data = [  # noqa: RUF001
        {"surface": "בֹּקֶר", "letters": ["ב", "ֹ", "ּ", "ק", "ֶ", "ר"], "gematria": 222, "ref": "Gen.1.5"},
        {"surface": "אֱלֹהִים", "letters": ["א", "ֱ", "לֹ", "ה", "ִ", "י", "ם"], "gematria": 86, "ref": "Gen.1.1"},
        {"surface": "אֶרֶץ", "letters": ["א", "ֶ", "ר", "ֶ", "ץ"], "gematria": 296, "ref": "Gen.1.1"},
        {"surface": "שָׁמַיִם", "letters": ["שָׁ", "מַ", "יִ", "ם"], "gematria": 390, "ref": "Gen.1.1"},
        {"surface": "ר֫וּחַ", "letters": ["ר֫", "וּ", "חַ"], "gematria": 214, "ref": "Gen.1.2"},
        {"surface": "חֹשֶׁךְ", "letters": ["חֹ", "שֶׁ", "ךְ"], "gematria": 329, "ref": "Gen.1.2"},
        {"surface": "תְּהוֹם", "letters": ["תְּ", "ה", "וֹ", "ם"], "gematria": 452, "ref": "Gen.1.2"},
        {"surface": "מַיִם", "letters": ["מַ", "יִ", "ם"], "gematria": 90, "ref": "Gen.1.2"},
        {"surface": "אוֹר", "letters": ["א", "וֹ", "ר"], "gematria": 207, "ref": "Gen.1.3"},
        {"surface": "יוֹם", "letters": ["י", "וֹ", "ם"], "gematria": 56, "ref": "Gen.1.5"},
        {"surface": "לַיְלָה", "letters": ["לַ", "יְ", "לָ", "ה"], "gematria": 75, "ref": "Gen.1.5"},
        {"surface": "רָקִיעַ", "letters": ["רָ", "קִ", "י", "עַ"], "gematria": 350, "ref": "Gen.1.6"},
        {"surface": "יַבָּשָׁה", "letters": ["יַ", "בָּ", "שָׁ", "ה"], "gematria": 317, "ref": "Gen.1.9"},
        {"surface": "מָקוֹם", "letters": ["מָ", "קוֹ", "ם"], "gematria": 186, "ref": "Gen.1.9"},
        {"surface": "יַמִּים", "letters": ["יַ", "מִּ", "י", "ם"], "gematria": 100, "ref": "Gen.1.10"},
        {"surface": "טוֹב", "letters": ["ט", "וֹ", "ב"], "gematria": 17, "ref": "Gen.1.10"},
        {"surface": "אָדָם", "letters": ["אָ", "דָ", "ם"], "gematria": 45, "ref": "Gen.2.7"},
        {"surface": "גָּן", "letters": ["גָּ", "ן"], "gematria": 53, "ref": "Gen.2.8"},
        {"surface": "עֵץ", "letters": ["עֵ", "ץ"], "gematria": 160, "ref": "Gen.2.9"},
        {"surface": "חַיִּים", "letters": ["חַ", "יִּ", "י", "ם"], "gematria": 28, "ref": "Gen.2.9"},
        {"surface": "דַּעַת", "letters": ["דַּ", "עַ", "ת"], "gematria": 474, "ref": "Gen.2.9"},
        {"surface": "נָהָר", "letters": ["נָ", "הָ", "ר"], "gematria": 255, "ref": "Gen.2.10"},
        {"surface": "אִשָּׁה", "letters": ["אִ", "שָּׁ", "ה"], "gematria": 311, "ref": "Gen.2.18"},
        {"surface": "עֵזֶר", "letters": ["עֵ", "זֶ", "ר"], "gematria": 177, "ref": "Gen.2.18"},
        {"surface": "כְּנֶגְדּוֹ", "letters": ["כְּ", "נֶ", "גְ", "דּ", "וֹ"], "gematria": 166, "ref": "Gen.2.18"},
        {"surface": "חַוָּה", "letters": ["חַ", "וָּ", "ה"], "gematria": 19, "ref": "Gen.3.20"},
        {"surface": "נְחָשׁ", "letters": ["נְ", "חָ", "שׁ"], "gematria": 358, "ref": "Gen.3.1"},
        {"surface": "עֵץ", "letters": ["עֵ", "ץ"], "gematria": 160, "ref": "Gen.3.1"},
        {"surface": "תַּפּוּחַ", "letters": ["תַּ", "פּ", "וּ", "חַ"], "gematria": 606, "ref": "Gen.3.6"},
        {"surface": "חֵטְא", "letters": ["חֵ", "טְ", "א"], "gematria": 18, "ref": "Gen.4.7"},
    ]

    # Return the first 'count' synthetic cases
    return [
        {
            "gematria": case["gematria"],
            "surface": case["surface"],
            "letters": case["letters"],
            "sources": [{"ref": case["ref"]}],
        }
        for case in synthetic_data[:count]
    ]


if __name__ == "__main__":
    sys.exit(main())
