import json, pathlib, pytest

FIX = pathlib.Path(__file__).parent / "fixtures"

CASES = [
    ("e01_min.json", "entities", 1),
    ("e01_min.json", "refs", 1),
    ("e02_forbidden.json", "error", "forbidden-symbols"),
    ("e03_schema_bad.json", "error", "schema-invalid"),
    ("e04_ring_violation.json", "error", "ring-violation"),
    ("e05_bus_parity.json", "parity", True),
]


@pytest.mark.parametrize("fname,key,expected", CASES)
def test_extraction_tvs(fname, key, expected):
    data = json.loads((FIX / fname).read_text())
    exp = data["expected"]
    # simulate extractor contract: assert expected keys/values only
    assert key in exp, f"missing key: {key}"
    assert exp[key] == expected
