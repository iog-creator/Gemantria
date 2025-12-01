"""TV-04: PROVENANCE_MISMATCH test.

Asserts that when provenance doesn't match schema:
- provenance_ok=false
- violation recorded
- seed/model/tool_version captured in result_json
"""

import pathlib
import pytest

try:
    import psycopg
except ImportError:
    psycopg = None

from agentpm.control_plane.sessions import create_session
from agentpm.guarded.guard_shim import GuardShim
from agentpm.guarded.violations import PROVENANCE_MISMATCH

pytestmark = pytest.mark.skipif(psycopg is None, reason="psycopg not available")


@pytest.fixture
def project_id():
    """Test project ID."""
    return 1


@pytest.fixture
def rule_id(project_id):
    """Create a test capability rule."""
    if psycopg is None:
        pytest.skip("psycopg not available")

    from scripts.config.env import get_rw_dsn

    dsn = get_rw_dsn()
    if not dsn:
        pytest.skip("GEMATRIA_DSN not set")

    try:
        with psycopg.connect(dsn) as conn, conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO control.capability_rule
                (project_id, name, ring, allowlist, budgets)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (project_id, name) DO UPDATE SET name = EXCLUDED.name
                RETURNING id
                """,
                (project_id, "test_rule", 1, ["test_tool"], '{"BUDGET_TOKENS": 1000}'),
            )
            rule_id = cur.fetchone()[0]
            conn.commit()
            yield str(rule_id)

            # Cleanup
            cur.execute("DELETE FROM control.capability_rule WHERE id = %s", (rule_id,))
            conn.commit()
    except Exception as e:
        pytest.skip(f"Failed to create test rule: {e}")


@pytest.fixture
def tool_catalog(project_id):
    """Create a test tool in catalog."""
    if psycopg is None:
        pytest.skip("psycopg not available")

    from scripts.config.env import get_rw_dsn

    dsn = get_rw_dsn()
    if not dsn:
        pytest.skip("GEMATRIA_DSN not set")

    io_schema = {
        "input": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
            },
        },
    }

    try:
        with psycopg.connect(dsn) as conn, conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO control.tool_catalog
                (project_id, name, ring, io_schema)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (project_id, name) DO UPDATE SET io_schema = EXCLUDED.io_schema
                RETURNING id
                """,
                (project_id, "test_tool", 1, psycopg.types.json.dumps(io_schema)),
            )
            tool_id = cur.fetchone()[0]
            conn.commit()
            yield str(tool_id)

            # Cleanup
            cur.execute("DELETE FROM control.tool_catalog WHERE id = %s", (tool_id,))
            conn.commit()
    except Exception as e:
        pytest.skip(f"Failed to create test tool: {e}")


@pytest.fixture
def session_id(project_id, rule_id):
    """Create a test session."""
    repo_root = pathlib.Path(__file__).resolve().parents[4]
    session_id = create_session(
        project_id=project_id,
        rule_id=rule_id,
        tiny_menu=["test_tool"],
        ttl_s=3600,
        repo_root=repo_root,
    )
    yield session_id

    # Cleanup
    if psycopg:
        from scripts.config.env import get_rw_dsn

        dsn = get_rw_dsn()
        if dsn:
            try:
                with psycopg.connect(dsn) as conn, conn.cursor() as cur:
                    cur.execute(
                        "DELETE FROM control.capability_session WHERE id = %s", (session_id,)
                    )
                    conn.commit()
            except Exception:
                pass


def test_tv04_provenance_mismatch(session_id, project_id, tool_catalog):
    """Test that invalid provenance triggers PROVENANCE_MISMATCH violation."""
    shim = GuardShim(session_id, project_id, retry_max=3)

    def tool_fn(args):
        return {"result": "ok"}

    # Call with invalid provenance (missing required fields)
    invalid_provenance = {
        "model": "test-model",
        # Missing "seed" and "ts_iso"
    }

    result = shim.execute(
        tool="test_tool",
        args={"query": "test"},
        tool_fn=tool_fn,
        provenance=invalid_provenance,
    )

    assert result["provenance_ok"] is False
    assert len(result["violations"]) > 0

    violation_codes = [v["code"] for v in result["violations"]]
    assert PROVENANCE_MISMATCH in violation_codes

    # Verify provenance fields are captured even on failure
    assert result.get("model") == "test-model"
    assert result.get("seed") is None  # Not provided
    assert result.get("tool_version") is None  # Not provided


def test_tv04_provenance_valid(session_id, project_id, tool_catalog):
    """Test that valid provenance passes."""
    shim = GuardShim(session_id, project_id, retry_max=3)

    def tool_fn(args):
        return {"result": "ok"}

    # Call with valid provenance
    valid_provenance = {
        "model": "test-model",
        "seed": 42,
        "ts_iso": "2024-01-01T00:00:00Z",
        "tool_version": "1.0.0",
    }

    result = shim.execute(
        tool="test_tool",
        args={"query": "test"},
        tool_fn=tool_fn,
        provenance=valid_provenance,
    )

    assert result["provenance_ok"] is True
    assert result.get("model") == "test-model"
    assert result.get("seed") == 42
    assert result.get("tool_version") == "1.0.0"
