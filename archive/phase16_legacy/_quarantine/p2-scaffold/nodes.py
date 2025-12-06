from __future__ import annotations

from typing import List, Dict, Any

import os


# super-minimal hebrew handling placeholder; real impl lives in core module later

HEBREW_SAMPLE = ["אֱלֹהִים", "בְּרֵאשִׁית", "אֹור"]


def extract_nouns(texts: List[str]) -> List[Dict[str, Any]]:
    if os.getenv("MOCK_AI", "0") == "1":
        # return fixed nouns deterministically

        return [{"surface_form": w, "lemma": w} for w in HEBREW_SAMPLE]

    # TODO: integrate actual NLP; for now, return tokens split

    nouns = []

    for t in texts:
        for tok in t.split():
            nouns.append({"surface_form": tok, "lemma": tok})

    return nouns


HEB_MAP = {  # Mispar Hechrachi (simplified placeholder)
    "א": 1,  # noqa: RUF001
    "ב": 2,  # noqa: RUF001
    "ג": 3,  # noqa: RUF001
    "ד": 4,  # noqa: RUF001
    "ה": 5,  # noqa: RUF001
    "ו": 6,  # noqa: RUF001
    "ז": 7,  # noqa: RUF001
    "ח": 8,  # noqa: RUF001
    "ט": 9,  # noqa: RUF001
    "י": 10,  # noqa: RUF001
    "כ": 20,  # noqa: RUF001
    "ל": 30,  # noqa: RUF001
    "מ": 40,  # noqa: RUF001
    "נ": 50,  # noqa: RUF001
    "ס": 60,  # noqa: RUF001
    "ע": 70,  # noqa: RUF001
    "פ": 80,  # noqa: RUF001
    "צ": 90,  # noqa: RUF001
    "ק": 100,  # noqa: RUF001
    "ר": 200,  # noqa: RUF001
    "ש": 300,  # noqa: RUF001
    "ת": 400,  # noqa: RUF001
}


def gematria_value(word: str) -> int:
    return sum(HEB_MAP.get(ch, 0) for ch in word)


def compute_gematria(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []

    for r in rows:
        g = gematria_value(r["lemma"])

        r2 = dict(r)

        r2["gematria_value"] = g

        out.append(r2)

    return out


def enrich(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # trivial enrichment: classify parity

    for r in rows:
        r["parity"] = "even" if r.get("gematria_value", 0) % 2 == 0 else "odd"

    return rows
