from __future__ import annotations

# Finals mapped to regular values (Mispar Hechrachi)
MAP: dict[str, int] = {
    "א":1,"ב":2,"ג":3,"ד":4,"ה":5,"ו":6,"ז":7,"ח":8,"ט":9,"י":10,
    "כ":20,"ך":20,"ל":30,"מ":40,"ם":40,"נ":50,"ן":50,"ס":60,"ע":70,
    "פ":80,"ף":80,"צ":90,"ץ":90,"ק":100,"ר":200,"ש":300,"ת":400
}

def calculate_gematria(word: str) -> int:
    return sum(MAP.get(ch, 0) for ch in word)

def calc_string(word: str) -> str:
    parts = [f"{ch}({MAP.get(ch,0)})" for ch in word]
    return "+".join(parts) + f"={calculate_gematria(word)}"
