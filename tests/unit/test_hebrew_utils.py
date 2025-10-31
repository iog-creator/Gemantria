from src.core.hebrew_utils import calc_string, calculate_gematria
from src.core.ids import normalize_hebrew


def test_adam_45():
    assert calculate_gematria("אדם") == 45


def test_hevel_37_after_normalization():
    assert normalize_hebrew("הֶבֶל") == "הבל"
    assert calculate_gematria("הבל") == 37


def test_calc_string():
    assert calc_string("אדם") == "א(1)+ד(4)+ם(40)=45"
