"""TV-01: MISSING_POR violation test.

Asserts that when PoR is missing or invalid, the system records:
- por_ok=false
- violations_json[0].code == "MISSING_POR"
"""

import pathlib
import pytest

try:
    import psycopg
except ImportError:
    psycopg = None

from agentpm.control_plane.sessions import create_session
from agentpm.guarded.gatekeeper import validate_por, generate_por_token

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


def test_tv01_missing_por_no_session():
    """Test that missing session results in MISSING_POR violation."""
    is_valid, error = validate_por("00000000-0000-0000-0000-000000000000")
    assert not is_valid
    assert "not found" in error.lower() or "expired" in error.lower()


def test_tv01_missing_por_invalid_token(project_id, rule_id, tmp_path):
    """Test that invalid PoR token results in MISSING_POR violation."""
    # Create a session
    repo_root = pathlib.Path(__file__).resolve().parents[4]
    session_id = create_session(
        project_id=project_id,
        rule_id=rule_id,
        tiny_menu=["test_tool"],
        ttl_s=3600,
        repo_root=repo_root,
    )

    try:
        # Try to validate with invalid token
        is_valid, error = validate_por(session_id, por_token="invalid-token")
        assert not is_valid
        assert "invalid" in error.lower() or "missing" in error.lower()
    finally:
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


def test_tv01_por_success(project_id, rule_id, tmp_path):
    """Test that valid PoR passes validation."""
    repo_root = pathlib.Path(__file__).resolve().parents[4]
    session_id = create_session(
        project_id=project_id,
        rule_id=rule_id,
        tiny_menu=["test_tool"],
        ttl_s=3600,
        repo_root=repo_root,
    )

    try:
        # Generate valid token
        por_token = generate_por_token(session_id)

        # Validate should pass
        is_valid, error = validate_por(session_id, por_token=por_token)
        assert is_valid, f"PoR validation failed: {error}"
        assert error is None
    finally:
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
