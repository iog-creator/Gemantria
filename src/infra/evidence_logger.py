# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

"""
Evidence Logger for Agent Observability

Provides structured evidence logging for agent execution results,
performance metrics, and quality validations. All evidence is stored
in share/evidence/ for external monitoring and auditing.
"""

import json
import time
from datetime import datetime, UTC
from pathlib import Path
from typing import Any, Dict

from src.infra.env_loader import ensure_env_loaded

# Load environment
ensure_env_loaded()

# Evidence directory
EVIDENCE_DIR = Path("share/evidence")
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)


class EvidenceLogger:
    """
    Structured evidence logging for agent observability.

    All evidence is timestamped and stored in share/evidence/ for
    external monitoring, auditing, and quality validation.
    """

    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.start_time = time.time()
        self.evidence = []

    def log_evidence(self, event_type: str, data: Dict[str, Any], level: str = "INFO") -> None:
        """
        Log a piece of evidence with timestamp and context.

        Args:
            event_type: Type of evidence (e.g., "noun_discovery", "validation_result")
            data: Evidence data dictionary
            level: Log level (INFO, WARN, ERROR)
        """
        evidence_entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "agent": self.agent_name,
            "event_type": event_type,
            "level": level,
            "data": data,
        }

        self.evidence.append(evidence_entry)

        # Also write to individual evidence file
        self._write_evidence_file(event_type, evidence_entry)

    def log_performance(self, operation: str, duration_ms: float, metadata: Dict[str, Any] | None = None) -> None:
        """
        Log performance metrics for an operation.

        Args:
            operation: Name of the operation
            duration_ms: Duration in milliseconds
            metadata: Additional performance metadata
        """
        data = {
            "operation": operation,
            "duration_ms": duration_ms,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        if metadata:
            data.update(metadata)

        self.log_evidence("performance", data)

    def log_validation_result(self, validation_type: str, passed: bool, details: Dict[str, Any]) -> None:
        """
        Log validation results.

        Args:
            validation_type: Type of validation (e.g., "schema", "invariants")
            passed: Whether validation passed
            details: Validation details and error messages
        """
        data = {"validation_type": validation_type, "passed": passed, "details": details}

        level = "INFO" if passed else "ERROR"
        self.log_evidence("validation", data, level)

    def log_agent_result(self, success: bool, output_summary: Dict[str, Any], error_details: str | None = None) -> None:
        """
        Log the final result of an agent execution.

        Args:
            success: Whether the agent completed successfully
            output_summary: Summary of outputs produced
            error_details: Error details if failed
        """
        data = {
            "success": success,
            "output_summary": output_summary,
            "execution_time_ms": (time.time() - self.start_time) * 1000,
        }

        if error_details:
            data["error_details"] = error_details

        level = "INFO" if success else "ERROR"
        self.log_evidence("agent_result", data, level)

    def get_evidence_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all evidence collected.

        Returns:
            Summary dictionary with counts and key metrics
        """
        total_events = len(self.evidence)
        error_count = sum(1 for e in self.evidence if e["level"] == "ERROR")
        warning_count = sum(1 for e in self.evidence if e["level"] == "WARN")

        # Get latest performance metrics
        perf_events = [e for e in self.evidence if e["event_type"] == "performance"]
        total_duration = sum(e["data"].get("duration_ms", 0) for e in perf_events)

        # Get validation results
        validation_events = [e for e in self.evidence if e["event_type"] == "validation"]
        validations_passed = sum(1 for e in validation_events if e["data"].get("passed", False))
        validations_total = len(validation_events)

        return {
            "agent": self.agent_name,
            "total_events": total_events,
            "error_count": error_count,
            "warning_count": warning_count,
            "performance_events": len(perf_events),
            "total_duration_ms": total_duration,
            "validations_passed": validations_passed,
            "validations_total": validations_total,
            "execution_time_ms": (time.time() - self.start_time) * 1000,
        }

    def _write_evidence_file(self, event_type: str, evidence_entry: Dict[str, Any]) -> None:
        """
        Write evidence to a timestamped file.

        Args:
            event_type: Type of evidence for filename
            evidence_entry: Full evidence entry
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.agent_name}_{event_type}_{timestamp}.json"
        filepath = EVIDENCE_DIR / filename

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(evidence_entry, f, indent=2, ensure_ascii=False)
        except Exception as e:
            # Fallback to simple text file if JSON fails
            txt_filepath = filepath.with_suffix(".txt")
            try:
                with open(txt_filepath, "w", encoding="utf-8") as f:
                    f.write(f"Evidence logging failed: {e}\n")
                    f.write(json.dumps(evidence_entry, indent=2, ensure_ascii=False))
            except Exception:
                pass  # Silent failure - don't break agent execution

    def finalize(self) -> None:
        """
        Finalize evidence collection and write summary.
        """
        summary = self.get_evidence_summary()

        # Write summary evidence
        summary_entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "agent": self.agent_name,
            "event_type": "evidence_summary",
            "level": "INFO",
            "data": summary,
        }

        self._write_evidence_file("summary", summary_entry)


# Global evidence logger registry
_active_loggers: Dict[str, EvidenceLogger] = {}


def get_evidence_logger(agent_name: str) -> EvidenceLogger:
    """
    Get or create an evidence logger for an agent.

    Args:
        agent_name: Name of the agent

    Returns:
        EvidenceLogger instance
    """
    if agent_name not in _active_loggers:
        _active_loggers[agent_name] = EvidenceLogger(agent_name)
    return _active_loggers[agent_name]


def finalize_all_evidence() -> None:
    """
    Finalize all active evidence loggers.
    """
    for logger in _active_loggers.values():
        logger.finalize()
    _active_loggers.clear()


def get_evidence_summary(agent_name: str | None = None) -> Dict[str, Any]:
    """
    Get evidence summary for an agent or all agents.

    Args:
        agent_name: Specific agent name, or None for all

    Returns:
        Evidence summary dictionary
    """
    if agent_name:
        logger = _active_loggers.get(agent_name)
        return logger.get_evidence_summary() if logger else {}
    else:
        return {name: logger.get_evidence_summary() for name, logger in _active_loggers.items()}
