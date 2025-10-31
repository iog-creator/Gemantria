#!/usr/bin/env python3
import json
import sys
from pathlib import Path

MAP = {
    "א": 1,
    "ב": 2,
    "ג": 3,
    "ד": 4,
    "ה": 5,
    "ו": 6,  # noqa: RUF001
    "ז": 7,
    "ח": 8,
    "ט": 9,  # noqa: RUF001
    "י": 10,  # noqa: RUF001
    "כ": 20,
    "ך": 20,
    "ל": 30,
    "מ": 40,
    "ם": 40,
    "נ": 50,
    "ן": 50,  # noqa: RUF001
    "ס": 60,  # noqa: RUF001
    "ע": 70,
    "פ": 80,
    "ף": 80,
    "צ": 90,
    "ץ": 90,
    "ק": 100,
    "ר": 200,
    "ש": 300,
    "ת": 400,
}


def gematria(word: str) -> int:
    return sum(MAP.get(ch, 0) for ch in word)


def main():
    p = Path("examples/archive/valid_cases.json")
    if not p.exists():
        print(f"[gematria] missing {p}", file=sys.stderr)
        return 2
    cases = json.loads(p.read_text(encoding="utf-8"))
    bad = 0
    for c in cases:
        got = gematria(c["hebrew"])
        exp = int(c["expected_value"])
        print(f"{c['hebrew']}: got={got} expected={exp}  {'OK' if got == exp else 'FAIL'}")
        if got != exp:
            bad += 1
    if bad:
        print(f"[gematria] {bad} failures")
        return 1
    print("[gematria] all cases OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
