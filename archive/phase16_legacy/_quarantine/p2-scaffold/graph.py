from __future__ import annotations

from typing import List, Dict, Any

from .envelope import emit

from .nodes import extract_nouns, compute_gematria, enrich


def run_pipeline(texts: List[str]) -> List[Dict[str, Any]]:
    emit("extract.nouns.start", ok=True, items=len(texts))

    nouns = extract_nouns(texts)

    emit("extract.nouns.done", ok=True, items=len(nouns))

    emit("compute.gematria.start", ok=True, items=len(nouns))

    with_g = compute_gematria(nouns)

    emit("compute.gematria.done", ok=True, items=len(with_g))

    emit("enrich.start", ok=True, items=len(with_g))

    enriched = enrich(with_g)

    emit("enrich.done", ok=True, items=len(enriched))

    # aggregation placeholder (counts per parity)

    counts = {"even": 0, "odd": 0}

    for r in enriched:
        counts[r["parity"]] += 1

    emit("aggregate.done", ok=True, items=len(enriched), **counts)

    return enriched


def main() -> int:
    # Hermetic: no network, optional SKIP_DB

    sample = ["בראשית ברא אלהים את השמים ואת הארץ"]

    run_pipeline(sample)

    emit("pipeline.done", ok=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
