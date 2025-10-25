from __future__ import annotations

CANONICAL_BOOKS = {
    "genesis": "Genesis",
    "gen": "Genesis",
    "bereshit": "Genesis",
    "exodus": "Exodus",
    "exo": "Exodus",
    "shemot": "Exodus",
    "leviticus": "Leviticus",
    "lev": "Leviticus",
    "vayikra": "Leviticus",
    "numbers": "Numbers",
    "num": "Numbers",
    "bamidbar": "Numbers",
    "deuteronomy": "Deuteronomy",
    "deut": "Deuteronomy",
    "devarim": "Deuteronomy",
}


def normalize_book(book: str) -> str:
    if not book:
        raise ValueError("book is required")
    key = book.strip().lower()
    return CANONICAL_BOOKS.get(key, book.strip())
