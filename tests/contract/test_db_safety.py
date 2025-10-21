import pytest
from src.infra.db import get_bible_ro, ReadOnlyViolation

@pytest.mark.parametrize("sql", [
    "INSERT INTO t(x) VALUES (%s)",
    "UPDATE t SET x=%s",
    "DELETE FROM t WHERE x=%s",
    "CREATE TABLE x(id int)",
    "ALTER TABLE x ADD COLUMN y int",
    "DROP TABLE x",
    "TRUNCATE t",
    "GRANT SELECT ON t TO u",
    "REVOKE SELECT ON t FROM u",
])
def test_bible_ro_denies_writes_without_touching_db(sql):
    ro = get_bible_ro()
    with pytest.raises(ReadOnlyViolation):
        # Must raise before any connection attempt
        list(ro.execute(sql, (1,)))
