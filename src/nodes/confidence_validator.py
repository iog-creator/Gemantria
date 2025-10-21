from __future__ import annotations
import os, psycopg, uuid
from typing import Dict, Any, List
from src.infra.structured_logger import get_logger, log_json

LOG = get_logger("gemantria.confidence_validator")

GEMATRIA_DSN = os.getenv("GEMATRIA_DSN")
GEMATRIA_CONFIDENCE_THRESHOLD = float(os.getenv("GEMATRIA_CONFIDENCE_THRESHOLD", "0.90"))
AI_CONFIDENCE_THRESHOLD = float(os.getenv("AI_CONFIDENCE_THRESHOLD", "0.95"))

class ConfidenceValidationError(Exception):
    """Raised when confidence validation fails and pipeline should abort."""
    def __init__(self, message: str, low_confidence_nouns: List[Dict[str, Any]]):
        super().__init__(message)
        self.low_confidence_nouns = low_confidence_nouns

def confidence_validator_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate confidence scores from AI enrichment.

    Checks both gematria calculation confidence and AI insights confidence
    against configured thresholds. Logs all validations and aborts pipeline
    if any noun fails confidence checks.
    """
    nouns = state.get("enriched_nouns", [])
    run_id = state.get("run_id", uuid.uuid4())

    if not nouns:
        log_json(LOG, 20, "confidence_validation_skipped", reason="no_nouns")
        return state

    low_confidence_nouns = []
    validation_results = []

    with psycopg.connect(GEMATRIA_DSN) as conn, conn.cursor() as cur:
        for noun in nouns:
            noun_id = noun.get("noun_id", uuid.uuid4())

            # Get confidence scores (default to 1.0 if not available)
            gematria_confidence = noun.get("gematria_confidence", 1.0)
            ai_confidence = noun.get("confidence", 1.0)  # From AI enrichment

            # Check thresholds
            gematria_passed = gematria_confidence >= GEMATRIA_CONFIDENCE_THRESHOLD
            ai_passed = ai_confidence >= AI_CONFIDENCE_THRESHOLD
            validation_passed = gematria_passed and ai_passed

            abort_reason = None
            if not validation_passed:
                reasons = []
                if not gematria_passed:
                    reasons.append(".2f")
                if not ai_passed:
                    reasons.append(".2f")
                abort_reason = "; ".join(reasons)

                low_confidence_nouns.append({
                    "noun": noun.get("name", "unknown"),
                    "gematria_confidence": gematria_confidence,
                    "ai_confidence": ai_confidence,
                    "reason": abort_reason
                })

            # Log validation result to database
            cur.execute(
                """INSERT INTO confidence_validation_log
                   (run_id, node, noun_id, gematria_confidence, ai_confidence,
                    gematria_threshold, ai_threshold, validation_passed, abort_reason)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (run_id, "confidence_validator", noun_id,
                 gematria_confidence, ai_confidence,
                 GEMATRIA_CONFIDENCE_THRESHOLD, AI_CONFIDENCE_THRESHOLD,
                 validation_passed, abort_reason)
            )

            validation_results.append({
                "noun_id": str(noun_id),
                "noun": noun.get("name", "unknown"),
                "gematria_confidence": gematria_confidence,
                "ai_confidence": ai_confidence,
                "validation_passed": validation_passed
            })

        conn.commit()

    # Log summary
    log_json(LOG, 20, "confidence_validation_complete",
             total_nouns=len(nouns),
             passed_validations=sum(1 for r in validation_results if r["validation_passed"]),
             failed_validations=len(low_confidence_nouns),
             thresholds={
                 "gematria": GEMATRIA_CONFIDENCE_THRESHOLD,
                 "ai": AI_CONFIDENCE_THRESHOLD
             })

    # Abort if any validations failed
    if low_confidence_nouns:
        error_msg = f"Confidence validation failed for {len(low_confidence_nouns)} nouns"
        log_json(LOG, 40, "confidence_validation_failed",
                 low_confidence_nouns=low_confidence_nouns)
        raise ConfidenceValidationError(error_msg, low_confidence_nouns)

    # Update state with validation results
    state["confidence_validation"] = {
        "passed": True,
        "results": validation_results,
        "thresholds": {
            "gematria": GEMATRIA_CONFIDENCE_THRESHOLD,
            "ai": AI_CONFIDENCE_THRESHOLD
        }
    }

    return state
