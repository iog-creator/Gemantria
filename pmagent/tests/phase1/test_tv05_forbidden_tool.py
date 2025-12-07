"""TV-05: FORBIDDEN_TOOL test.

Asserts that when tool is not in tiny-menu:
- Tiny-menu deny
- violations_json contains FORBIDDEN_TOOL
"""

import pathlib
import pytest

try:
    import psycopg
except ImportError:
    psycopg = None

from pmagent.control_plane.sessions import create_session
from pmagent.guarded.guard_shim import GuardShim
from pmagent.guarded.violations import FORBIDDEN_TOOL

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
                (project_id, "test_rule", 1, ["allowed_tool"], '{"BUDGET_TOKENS": 1000}'),
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
    """Create test tools in catalog."""
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

    tool_ids = []
    try:
        with psycopg.connect(dsn) as conn, conn.cursor() as cur:
            # Create allowed tool
            cur.execute(
                """
                INSERT INTO control.tool_catalog
                (project_id, name, ring, io_schema)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (project_id, name) DO UPDATE SET io_schema = EXCLUDED.io_schema
                RETURNING id
                """,
                (project_id, "allowed_tool", 1, psycopg.types.json.dumps(io_schema)),
            )
            tool_ids.append(cur.fetchone()[0])

            # Create forbidden tool
            cur.execute(
                """
                INSERT INTO control.tool_catalog
                (project_id, name, ring, io_schema)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (project_id, name) DO UPDATE SET io_schema = EXCLUDED.io_schema
                RETURNING id
                """,
                (project_id, "forbidden_tool", 1, psycopg.types.json.dumps(io_schema)),
            )
            tool_ids.append(cur.fetchone()[0])

            conn.commit()
            yield tool_ids

            # Cleanup
            for tool_id in tool_ids:
                cur.execute("DELETE FROM control.tool_catalog WHERE id = %s", (tool_id,))
            conn.commit()
    except Exception as e:
        pytest.skip(f"Failed to create test tools: {e}")


@pytest.fixture
def session_id(project_id, rule_id):
    """Create a test session with only 'allowed_tool' in tiny-menu."""
    repo_root = pathlib.Path(__file__).resolve().parents[4]
    session_id = create_session(
        project_id=project_id,
        rule_id=rule_id,
        tiny_menu=["allowed_tool"],  # Only allowed_tool, not forbidden_tool
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
                    cur.execute("DELETE FROM control.capability_session WHERE id = %s", (session_id,))
                    conn.commit()
            except Exception:
                pass


def test_tv05_forbidden_tool(session_id, project_id, tool_catalog):
    """Test that forbidden tool triggers FORBIDDEN_TOOL violation."""
    shim = GuardShim(session_id, project_id, retry_max=3)

    def tool_fn(args):
        return {"result": "ok"}

    # Try to call forbidden_tool (not in tiny-menu)
    result = shim.execute(
        tool="forbidden_tool",
        args={"query": "test"},
        tool_fn=tool_fn,
    )

    assert result["schema_ok"] is False  # Blocked before schema check
    assert len(result["violations"]) > 0

    violation_codes = [v["code"] for v in result["violations"]]
    assert FORBIDDEN_TOOL in violation_codes


def test_tv05_allowed_tool(session_id, project_id, tool_catalog):
    """Test that allowed tool works."""
    shim = GuardShim(session_id, project_id, retry_max=3)

    def tool_fn(args):
        return {"result": "ok"}

    # Call allowed_tool (in tiny-menu)
    result = shim.execute(
        tool="allowed_tool",
        args={"query": "test"},
        tool_fn=tool_fn,
    )

    # Should pass (assuming PoR is valid)
    # Note: This test may fail if PoR validation fails, which is expected
    # The key is that FORBIDDEN_TOOL is not in violations
    violation_codes = [v["code"] for v in result.get("violations", [])]
    assert FORBIDDEN_TOOL not in violation_codes
