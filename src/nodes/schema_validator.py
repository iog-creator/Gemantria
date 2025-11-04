import json
from pathlib import Path
from typing import Any

from src.infra.structured_logger import get_logger, log_json

LOG = get_logger("gematria.schema_validator")


class SchemaValidationError(Exception):
    """Raised when schema validation fails."""

    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__(f"Schema validation failed: {len(errors)} error(s)")


def schema_validator_node(state: dict[str, Any]) -> dict[str, Any]:
    """
    Validate pipeline outputs against JSON schemas.

    This node validates key pipeline artifacts against their expected schemas
    to ensure data integrity and catch issues early.
    """
    try:
        # Import jsonschema here to make it optional
        try:
            from jsonschema import ValidationError, validate
        except ImportError:
            log_json(LOG, 30, "schema_validation_skipped", reason="jsonschema not installed")
            return state

        validation_errors = []
        schemas_validated = []

        # Validate exports if they exist
        exports_dir = Path("exports")
        schemas_dir = Path("schemas")

        if exports_dir.exists():
            # Validate graph_latest.json against graph schema if available
            graph_file = exports_dir / "graph_latest.json"
            if graph_file.exists():
                schema_file = schemas_dir / "graph_output.schema.json"
                if not schema_file.exists():
                    # Try alternative schema locations
                    schema_file = Path("docs/SSOT/schemas/graph_output.schema.json")
                if not schema_file.exists():
                    schema_file = Path("docs/SSOT/graph_output.schema.json")

                if schema_file.exists():
                    try:
                        with open(graph_file, encoding="utf-8") as f:
                            graph_data = json.load(f)
                        with open(schema_file, encoding="utf-8") as f:
                            schema = json.load(f)

                        validate(instance=graph_data, schema=schema)
                        schemas_validated.append("graph_latest.json")
                        log_json(LOG, 20, "schema_validated", file="graph_latest.json", schema=str(schema_file))
                    except ValidationError as e:
                        validation_errors.append(f"graph_latest.json: {e.message}")
                    except Exception as e:
                        validation_errors.append(f"graph_latest.json validation error: {e}")

        # Validate envelope if it exists
        envelope_file = Path("share/exports/envelope.json")
        if envelope_file.exists():
            schema_file = schemas_dir / "envelope.schema.json"
            if not schema_file.exists():
                schema_file = Path("docs/SSOT/schemas/envelope.schema.json")

            if schema_file.exists():
                try:
                    with open(envelope_file, encoding="utf-8") as f:
                        envelope_data = json.load(f)
                    with open(schema_file, encoding="utf-8") as f:
                        schema = json.load(f)

                    validate(instance=envelope_data, schema=schema)
                    schemas_validated.append("envelope.json")
                    log_json(LOG, 20, "schema_validated", file="envelope.json", schema=str(schema_file))
                except ValidationError as e:
                    validation_errors.append(f"envelope.json: {e.message}")
                except Exception as e:
                    validation_errors.append(f"envelope.json validation error: {e}")

        # If there were validation errors, raise an exception
        if validation_errors:
            log_json(LOG, 40, "schema_validation_failed", errors=validation_errors)
            raise SchemaValidationError(validation_errors)

        # Log successful validation
        if schemas_validated:
            log_json(
                LOG,
                20,
                "schema_validation_complete",
                validated_count=len(schemas_validated),
                validated_files=schemas_validated,
            )

        return state

    except SchemaValidationError:
        raise  # Re-raise schema validation errors
    except Exception as e:
        log_json(LOG, 40, "schema_validator_unexpected_error", error=str(e))
        return state  # Don't fail the pipeline for unexpected errors
