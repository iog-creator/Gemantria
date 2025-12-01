# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

"""
Math Verifier Node

Verifies gematria calculations using the MATH_MODEL for numeric sanity checks.
Uses self-certainty-qwen3-1.7b-base-math to verify arithmetic correctness.
"""

from __future__ import annotations

import os

from src.core.hebrew_utils import MAP, calculate_gematria
from src.infra.metrics_core import get_metrics_client
from src.infra.structured_logger import get_logger, log_json
from src.services.lmstudio_client import chat_completion
from src.utils.json_sanitize import parse_llm_json

LOG = get_logger("gemantria.math_verifier")

# Phase-7C: Router integration (optional, behind ROUTER_ENABLED flag)
try:
    from agentpm.lm.router import RouterTask, route_task
    from agentpm.adapters.lm_studio import chat as lm_studio_chat
    from agentpm.adapters.ollama import chat as ollama_chat
    from agentpm.adapters.theology import chat as theology_chat

    ROUTER_AVAILABLE = True
except ImportError:
    ROUTER_AVAILABLE = False


def math_verifier_node(state: dict) -> dict:
    """
    Verify gematria calculations using MATH_MODEL for numeric sanity checks.

    For each noun with letters and gematria:
    1. Recompute gematria locally using calculate_gematria()
    2. Ask MATH_MODEL to verify the arithmetic
    3. Attach math_check results to noun.analysis

    Args:
        state: Pipeline state containing enriched_nouns

    Returns:
        Updated state with math_check added to each noun's analysis
    """
    math_model = os.getenv("MATH_MODEL", "self-certainty-qwen3-1.7b-base-math")
    if not math_model:
        log_json(
            LOG,
            30,
            "math_model_not_configured",
            message="MATH_MODEL not set, skipping verification",
        )
        return state

    enriched_nouns = state.get("enriched_nouns", [])
    if not enriched_nouns:
        log_json(LOG, 20, "math_verifier_start", noun_count=0, message="No nouns to verify")
        return state

    log_json(LOG, 20, "math_verifier_start", noun_count=len(enriched_nouns), model=math_model)
    metrics_client = get_metrics_client()
    run_id = state.get("run_id", "unknown")

    verified_nouns = []
    verification_count = 0

    # Process in batches to avoid overwhelming LM Studio
    batch_size = 8
    for i in range(0, len(enriched_nouns), batch_size):
        batch = enriched_nouns[i : i + batch_size]
        batch_verified = []

        for noun in batch:
            # Get letters and claimed gematria
            letters = noun.get("letters", [])
            hebrew = noun.get("hebrew", noun.get("surface", noun.get("name", "")))
            claimed = noun.get("gematria") or noun.get("gematria_value")

            # Skip if no letters or no claimed value
            if not letters and not hebrew:
                log_json(LOG, 20, "skipping_no_letters", noun=noun.get("name"))
                noun_copy = dict(noun)
                noun_copy.setdefault("analysis", {})
                noun_copy["analysis"]["math_check"] = {
                    "ok": False,
                    "reason": "no_letters_or_hebrew",
                    "model": math_model,
                }
                batch_verified.append(noun_copy)
                continue

            # Calculate local sum from letters or hebrew text
            if letters:
                # Use letters if available
                letter_values_list = [MAP.get(ch, 0) for ch in letters]
                local_sum = sum(letter_values_list)
                letters_str = ", ".join(letters)
            elif hebrew:
                # Fallback to hebrew text
                local_sum = calculate_gematria(hebrew)
                letter_values_list = [MAP.get(ch, 0) for ch in hebrew]
                letters_str = hebrew
            else:
                local_sum = 0
                letter_values_list = []
                letters_str = ""

            # Skip if no claimed value to verify
            if claimed is None:
                log_json(LOG, 20, "skipping_no_claimed_gematria", noun=noun.get("name"))
                noun_copy = dict(noun)
                noun_copy.setdefault("analysis", {})
                noun_copy["analysis"]["math_check"] = {
                    "ok": False,
                    "reason": "no_claimed_gematria",
                    "local_sum": local_sum,
                    "model": math_model,
                }
                batch_verified.append(noun_copy)
                continue

            # Build verification prompt for math model
            values_str = ", ".join(str(v) for v in letter_values_list)
            prompt = (
                f"Sum these integers exactly and answer ONLY true or false (no text).\n"
                f"Integers: {values_str}\n"
                f"Claimed total: {claimed}\n"
                f"Is the claimed total equal to the true sum? Answer with only 'true' or 'false'."
            )

            # Call math model for verification
            try:
                messages = [
                    {
                        "role": "system",
                        "content": "You are a precise mathematical verifier. Answer only 'true' or 'false' for arithmetic verification questions.",
                    },
                    {"role": "user", "content": prompt},
                ]

                # Phase-7C: Use router if enabled, otherwise use legacy path
                use_router = ROUTER_AVAILABLE and os.getenv("ROUTER_ENABLED", "1") in (
                    "1",
                    "true",
                    "yes",
                )
                if use_router:
                    # Route task through router
                    router_task = RouterTask(
                        kind="math_verification",
                        domain="math",
                        needs_tools=False,
                        temperature=0.0,
                    )
                    decision = route_task(router_task, dry_run=False)

                    # Call appropriate adapter based on router decision
                    if decision.provider == "ollama":
                        response_text = (
                            ollama_chat(
                                prompt, model=decision.model_name, system=messages[0]["content"]
                            )
                            .strip()
                            .lower()
                        )
                    elif decision.provider == "lmstudio":
                        # Use theology adapter if slot is theology, otherwise lm_studio_chat
                        if decision.slot == "theology":
                            response_text = (
                                theology_chat(prompt, system=messages[0]["content"]).strip().lower()
                            )
                        else:
                            response_text = (
                                lm_studio_chat(
                                    prompt,
                                    model_slot=decision.slot,
                                    system=messages[0]["content"],
                                    temperature=decision.temperature,
                                )
                                .strip()
                                .lower()
                            )
                    else:
                        # Fallback to legacy
                        results = chat_completion([messages], model=math_model, temperature=0.0)
                        response_text = results[0].text.strip().lower()
                else:
                    # Legacy path: direct call
                    results = chat_completion([messages], model=math_model, temperature=0.0)
                    response_text = results[0].text.strip().lower()

                # Parse response (look for true/false)
                model_ok = False
                model_confidence = 0.0

                if "true" in response_text:
                    model_ok = True
                    model_confidence = 0.95
                elif "false" in response_text:
                    model_ok = False
                    model_confidence = 0.95
                else:
                    # Try to parse as JSON
                    try:
                        parsed = parse_llm_json(response_text)
                        model_ok = bool(parsed.get("value", False) or parsed.get("result", False))
                        model_confidence = float(parsed.get("confidence", 0.9))
                    except Exception:
                        # Fallback: use local calculation
                        model_ok = local_sum == claimed
                        model_confidence = 0.5
                        log_json(
                            LOG,
                            30,
                            "math_model_parse_failed",
                            noun=noun.get("name"),
                            response=response_text[:100],
                        )

            except Exception as e:
                log_json(LOG, 30, "math_model_call_failed", noun=noun.get("name"), error=str(e))
                # Fallback to local calculation only
                model_ok = local_sum == claimed
                model_confidence = 0.0

            # Final verification: both local and model must agree
            local_ok = local_sum == claimed
            final_ok = local_ok and model_ok

            # Create math_check result
            noun_copy = dict(noun)
            noun_copy.setdefault("analysis", {})
            noun_copy["analysis"]["math_check"] = {
                "ok": final_ok,
                "local_sum": local_sum,
                "claimed": claimed,
                "local_ok": local_ok,
                "model_ok": model_ok,
                "model": math_model,
                "confidence": model_confidence,
                "letters": letters_str,
            }

            batch_verified.append(noun_copy)
            verification_count += 1

            if final_ok:
                log_json(
                    LOG,
                    20,
                    "gematria_verified",
                    noun=noun.get("name"),
                    local_sum=local_sum,
                    claimed=claimed,
                )
            else:
                log_json(
                    LOG,
                    30,
                    "gematria_mismatch",
                    noun=noun.get("name"),
                    local_sum=local_sum,
                    claimed=claimed,
                    local_ok=local_ok,
                    model_ok=model_ok,
                )

        verified_nouns.extend(batch_verified)

        # Emit batch metrics
        metrics_client.emit(
            {
                "run_id": run_id,
                "node": "math_verifier",
                "event": "batch_processed",
                "items_in": len(batch),
                "items_out": len(batch_verified),
            }
        )

    log_json(
        LOG,
        20,
        "math_verifier_complete",
        verified_count=verification_count,
        total_nouns=len(enriched_nouns),
    )

    state["enriched_nouns"] = verified_nouns
    return state
