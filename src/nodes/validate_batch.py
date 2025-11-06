"""
Validate batch node for pipeline batch size validation.

Related Rules: Rule-003 (Graph and Batch), Rule-039 (Execution Contract)
Related ADRs: ADR-003 (Batch Semantics)
"""

from typing import Any

from src.graph.batch_processor import BatchProcessor, BatchConfig
from src.infra.structured_logger import get_logger, log_json

LOG = get_logger("gematria.validate_batch")


def validate_batch_node(state: dict[str, Any]) -> dict[str, Any]:
    """
    Validate batch size and filter invalid nouns before enrichment.

    This node validates that the noun batch meets minimum size requirements
    and filters out nouns with missing or invalid Hebrew text to prevent
    enrichment of placeholder/unknown nouns.
    """
    try:
        nouns = state.get("nouns", [])
        if not nouns:
            log_json(LOG, 30, "validate_batch_skipped", reason="no_nouns")
            state["weighted_nouns"] = []
            state["validated_nouns"] = []
            return state

        # Filter out invalid nouns (missing Hebrew text, empty surface, or "Unknown")
        initial_count = len(nouns)
        valid_nouns = []
        filtered_count = 0

        for noun in nouns:
            # Check for valid Hebrew text/surface
            surface = noun.get("surface", "") or noun.get("hebrew", "") or noun.get("hebrew_text", "")
            name = noun.get("name", "")

            # Reject if:
            # - No Hebrew text at all (empty/null/None)
            # - Surface is "Unknown" (placeholder)
            # - Name is "Unknown" and no Hebrew text
            if not surface or surface.strip() == "" or surface == "Unknown":
                if name != "Unknown" or not surface:
                    # Only log if it's not just "Unknown" as name (which enrichment would catch)
                    filtered_count += 1
                    log_json(LOG, 20, "noun_filtered_invalid", noun_id=noun.get("noun_id"), surface=surface, name=name)
                continue

            # Reject if name is "Unknown" and we have no valid Hebrew
            if name == "Unknown" and not surface:
                filtered_count += 1
                log_json(LOG, 20, "noun_filtered_unknown", noun_id=noun.get("noun_id"))
                continue

            valid_nouns.append(noun)

        if filtered_count > 0:
            log_json(
                LOG, 20, "nouns_filtered", filtered=filtered_count, remaining=len(valid_nouns), initial=initial_count
            )

        # Create batch processor with config from environment
        config = BatchConfig.from_env()
        processor = BatchProcessor(config)

        # Validate batch size (will raise BatchAbortError if < minimum and ALLOW_PARTIAL=0)
        # Pass list of noun IDs (strings) for validation
        noun_ids = [str(n.get("noun_id", n.get("surface", n.get("hebrew", "")))) for n in valid_nouns]
        processor.validate_batch_size(noun_ids)

        # Set validated nouns for downstream processing (only valid ones)
        state["weighted_nouns"] = valid_nouns
        state["validated_nouns"] = state["weighted_nouns"]
        state["nouns"] = valid_nouns  # Update state with filtered nouns

        log_json(LOG, 20, "batch_validated", count=len(valid_nouns), filtered=filtered_count)
        return state

    except Exception as e:
        log_json(LOG, 40, "validate_batch_failed", error=str(e))
        raise
