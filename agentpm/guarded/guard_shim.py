from scripts.config.env import get_rw_dsn
# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

"""Guard shim: JSON Schema validation, tiny-menu enforcement, budgets, retries, agent_run writes."""

import json
import pathlib
import time
from typing import Any, Callable, Dict, List

try:
    import jsonschema
    from jsonschema import Draft202012Validator
except ImportError:
    jsonschema = None
    Draft202012Validator = None

try:
    import psycopg
except ImportError:
    psycopg = None

from agentpm.guarded.gatekeeper import check_session_ttl, validate_por
from agentpm.guarded.violations import (
    ARG_SCHEMA_INVALID,
    FORBIDDEN_TOOL,
    MISSING_POR,
    PROVENANCE_MISMATCH,
    RETRY_EXHAUSTED,
    RING_VIOLATION,
    create_violation,
)


def load_schema(schema_name: str) -> Dict[str, Any]:
    """Load a JSON Schema from schemas/ directory."""
    schema_dir = pathlib.Path(__file__).resolve().parent / "schemas"
    schema_path = schema_dir / f"{schema_name}.schema.json"

    if not schema_path.exists():
        raise FileNotFoundError(f"Schema not found: {schema_path}")

    with schema_path.open() as f:
        return json.load(f)


def validate_json_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> tuple[bool, str | None]:
    """
    Validate data against JSON Schema (2020-12).
    Returns (is_valid, error_message).
    """
    if jsonschema is None or Draft202012Validator is None:
        return False, "jsonschema not available"

    try:
        validator = Draft202012Validator(schema)
        errors = list(validator.iter_errors(data))
        if errors:
            error_msg = "; ".join(str(e) for e in errors[:3])  # Limit to first 3 errors
            return False, error_msg
        return True, None
    except Exception as e:
        return False, f"Schema validation error: {e}"


def check_tiny_menu(tool: str, tiny_menu: List[str]) -> bool:
    """Check if tool is in tiny-menu allowlist."""
    return tool in tiny_menu


def check_ring(tool_ring: int, allowed_ring: int) -> bool:
    """Check if tool ring is allowed."""
    return tool_ring <= allowed_ring


def check_budget(budget_key: str, used: int, limit: int) -> bool:
    """Check if budget limit is exceeded."""
    return used < limit


class GuardShim:
    """Guard shim for tool call validation and execution."""

    def __init__(
        self,
        session_id: str,
        project_id: int,
        retry_max: int = 3,
        strict_mode: str = "HINT",
    ):
        self.session_id = session_id
        self.project_id = project_id
        self.retry_max = retry_max
        self.strict_mode = strict_mode
        self.violations: List[Dict[str, Any]] = []
        self.retry_count = 0

    def _get_session_data(self) -> Dict[str, Any] | None:
        """Get session data from DB."""
        if psycopg is None:
            return None

        from agentpm.control_plane.sessions import get_session

        return get_session(self.session_id)

    def _get_tool_catalog(self, tool: str) -> Dict[str, Any] | None:
        """Get tool catalog entry."""
        if psycopg is None:
            return None

        dsn = get_rw_dsn()
        if not dsn:
            return None

        try:
            with psycopg.connect(dsn) as conn, conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, name, ring, io_schema, enabled
                    FROM control.tool_catalog
                    WHERE project_id = %s AND name = %s AND enabled = true
                    """,
                    (self.project_id, tool),
                )
                row = cur.fetchone()
                if row is None:
                    return None

                return {
                    "id": str(row[0]),
                    "name": row[1],
                    "ring": row[2],
                    "io_schema": row[3],
                    "enabled": row[4],
                }
        except Exception:
            return None

    def _get_capability_rule(self, rule_id: str) -> Dict[str, Any] | None:
        """Get capability rule."""
        if psycopg is None:
            return None

        dsn = get_rw_dsn()
        if not dsn:
            return None

        try:
            with psycopg.connect(dsn) as conn, conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, name, ring, allowlist, denylist, budgets
                    FROM control.capability_rule
                    WHERE id = %s
                    """,
                    (rule_id,),
                )
                row = cur.fetchone()
                if row is None:
                    return None

                return {
                    "id": str(row[0]),
                    "name": row[1],
                    "ring": row[2],
                    "allowlist": row[3] or [],
                    "denylist": row[4] or [],
                    "budgets": row[5] or {},
                }
        except Exception:
            return None

    def _write_agent_run(
        self,
        tool: str,
        args_json: Dict[str, Any],
        result_json: Dict[str, Any],
        violations_json: List[Dict[str, Any]],
    ) -> str | None:
        """Write agent_run row to DB. Returns run ID."""
        if psycopg is None:
            return None

        dsn = get_rw_dsn()
        if not dsn:
            return None

        try:
            with psycopg.connect(dsn) as conn, conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO control.agent_run
                    (project_id, session_id, tool, args_json, result_json, violations_json)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        self.project_id,
                        self.session_id,
                        tool,
                        psycopg.types.json.dumps(args_json),
                        psycopg.types.json.dumps(result_json),
                        psycopg.types.json.dumps(violations_json),
                    ),
                )
                run_id = cur.fetchone()[0]
                conn.commit()
                return str(run_id)
        except Exception:
            if self.strict_mode == "STRICT":
                raise
            return None

    def execute(
        self,
        tool: str,
        args: Dict[str, Any],
        tool_fn: Callable[[Dict[str, Any]], Dict[str, Any]],
        por_token: str | None = None,
        provenance: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """
        Execute a guarded tool call.
        Returns result dict with schema_ok, por_ok, provenance_ok, violations, etc.
        """
        start_time = time.time()
        self.violations = []
        self.retry_count = 0

        # Get session data
        session = self._get_session_data()
        if session is None:
            violation = create_violation(MISSING_POR, "Session not found or expired")
            self.violations.append(violation)
            result = {
                "schema_ok": False,
                "por_ok": False,
                "provenance_ok": False,
                "violations": [violation],
                "retry_count": 0,
                "latency_ms": int((time.time() - start_time) * 1000),
            }
            self._write_agent_run(tool, args, result, self.violations)
            return result

        # Check session TTL
        if not check_session_ttl(self.session_id):
            violation = create_violation(MISSING_POR, "Session expired")
            self.violations.append(violation)
            result = {
                "schema_ok": False,
                "por_ok": False,
                "provenance_ok": False,
                "violations": [violation],
                "retry_count": 0,
                "latency_ms": int((time.time() - start_time) * 1000),
            }
            self._write_agent_run(tool, args, result, self.violations)
            return result

        # Validate PoR
        por_ok, por_error = validate_por(self.session_id, por_token)
        if not por_ok:
            violation = create_violation(MISSING_POR, por_error or "PoR validation failed")
            self.violations.append(violation)

        # Get capability rule
        rule_id = session.get("rule_id")
        rule = self._get_capability_rule(rule_id) if rule_id else None

        # Check tiny-menu
        tiny_menu = session.get("tiny_menu", [])
        if not check_tiny_menu(tool, tiny_menu):
            violation = create_violation(FORBIDDEN_TOOL, f"Tool '{tool}' not in tiny-menu")
            self.violations.append(violation)
            result = {
                "schema_ok": False,
                "por_ok": por_ok,
                "provenance_ok": False,
                "violations": self.violations,
                "retry_count": 0,
                "latency_ms": int((time.time() - start_time) * 1000),
            }
            self._write_agent_run(tool, args, result, self.violations)
            return result

        # Get tool catalog entry
        tool_catalog = self._get_tool_catalog(tool)
        if tool_catalog is None:
            violation = create_violation(FORBIDDEN_TOOL, f"Tool '{tool}' not in catalog")
            self.violations.append(violation)
            result = {
                "schema_ok": False,
                "por_ok": por_ok,
                "provenance_ok": False,
                "violations": self.violations,
                "retry_count": 0,
                "latency_ms": int((time.time() - start_time) * 1000),
            }
            self._write_agent_run(tool, args, result, self.violations)
            return result

        # Check ring
        tool_ring = tool_catalog.get("ring", 999)
        allowed_ring = rule.get("ring", 1) if rule else 1
        if not check_ring(tool_ring, allowed_ring):
            violation = create_violation(RING_VIOLATION, f"Tool ring {tool_ring} > allowed ring {allowed_ring}")
            self.violations.append(violation)
            result = {
                "schema_ok": False,
                "por_ok": por_ok,
                "provenance_ok": False,
                "violations": self.violations,
                "retry_count": 0,
                "latency_ms": int((time.time() - start_time) * 1000),
            }
            self._write_agent_run(tool, args, result, self.violations)
            return result

        # Validate args against schema
        io_schema = tool_catalog.get("io_schema", {})
        input_schema = io_schema.get("input")
        schema_ok = True
        schema_error = None

        if input_schema:
            schema_ok, schema_error = validate_json_schema(args, input_schema)
            if not schema_ok:
                violation = create_violation(ARG_SCHEMA_INVALID, schema_error or "Schema validation failed")
                self.violations.append(violation)

        # Retry loop for schema validation failures
        while not schema_ok and self.retry_count < self.retry_max:
            self.retry_count += 1
            # In a real implementation, we might retry with corrected args
            # For Phase-1, we just record the retry
            time.sleep(0.1)  # Small delay

        if not schema_ok and self.retry_count >= self.retry_max:
            violation = create_violation(RETRY_EXHAUSTED, f"Retry limit {self.retry_max} exceeded")
            self.violations.append(violation)

        # Validate provenance if provided
        provenance_ok = True
        if provenance:
            try:
                provenance_schema = load_schema("provenance")
                provenance_ok, prov_error = validate_json_schema(provenance, provenance_schema)
                if not provenance_ok:
                    violation = create_violation(PROVENANCE_MISMATCH, prov_error or "Provenance validation failed")
                    self.violations.append(violation)
            except Exception as e:
                violation = create_violation(PROVENANCE_MISMATCH, f"Provenance error: {e}")
                self.violations.append(violation)
                provenance_ok = False

        # Execute tool if all checks pass
        tool_result = {}
        if schema_ok and por_ok and provenance_ok and not self.violations:
            try:
                tool_result = tool_fn(args)
            except Exception as e:
                violation = create_violation("TOOL_ERROR", f"Tool execution failed: {e}")
                self.violations.append(violation)

        # Build result
        latency_ms = int((time.time() - start_time) * 1000)
        result = {
            "schema_ok": schema_ok,
            "por_ok": por_ok,
            "provenance_ok": provenance_ok,
            "seed": provenance.get("seed") if provenance else None,
            "model": provenance.get("model") if provenance else None,
            "tool_version": provenance.get("tool_version") if provenance else None,
            "latency_ms": latency_ms,
            "retry_count": self.retry_count,
            "result": tool_result,
        }

        # Write agent_run
        self._write_agent_run(tool, args, result, self.violations)

        # Add violations to result for easy access
        result["violations"] = self.violations

        return result
