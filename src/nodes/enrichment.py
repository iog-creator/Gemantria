from __future__ import annotations

import os
import time
import uuid

import psycopg

from src.infra.metrics import get_metrics_client
from src.infra.structured_logger import get_logger, log_json
from src.services.lmstudio_client import chat_completion, safe_json_parse

LOG = get_logger("gemantria.enrichment")

GEMATRIA_DSN = os.getenv("GEMATRIA_DSN")

# Confidence gates
SOFT = float(os.getenv("AI_CONFIDENCE_SOFT", 0.90))
HARD = float(os.getenv("AI_CONFIDENCE_HARD", 0.95))


def evaluate_confidence(conf):
    """Evaluate confidence against soft/hard gates."""
    status = "pass"
    if conf < SOFT:
        status = "warn"
        metrics_client = get_metrics_client()
        metrics_client.emit({"event": "ai_conf_soft_warn"})
    if conf < HARD:
        status = "fail"
        metrics_client = get_metrics_client()
        metrics_client.emit({"event": "ai_conf_hard_fail"})
    return status


def enrichment_node(state: dict) -> dict:
    # Pipeline-level Qwen Live Gate already verified all required models are available
    theology_model = os.getenv("THEOLOGY_MODEL")
    if not theology_model:
        raise ValueError("THEOLOGY_MODEL environment variable required")

    nouns = state.get("validated_nouns", [])
    if not nouns:
        log_json(
            LOG, 20, "enrichment_start", noun_count=0, message="No nouns to enrich"
        )
        state["enriched_nouns"] = []
        state["ai_enrichments_generated"] = 0
        return state

    log_json(LOG, 20, "enrichment_start", noun_count=len(nouns))
    metrics_client = get_metrics_client()
    run_id = state.get("run_id", uuid.uuid4())

    # 1) Build prompts once per noun
    sys_msg = "You are a concise biblical scholar. Provide a short theological insight (150–250 words max) and a 0–1 confidence score. Return only valid JSON with keys 'insight' and 'confidence'."
    tmpl = (
        "Noun: {name}\nHebrew: {hebrew}\nPrimary Verse: {primary_verse}\n"
        "Task: Provide 1 concise theological insight. Return JSON: "
        '{{"insight": "...", "confidence": <0..1>}}'
    )

    # 2) Process in batches of 4 to avoid overwhelming LM Studio
    batch_size = 4
    enriched_nouns = []
    total_tokens = 0

    for i in range(0, len(nouns), batch_size):
        chunk = nouns[i : i + batch_size]
        batch_start = time.time()

        # Build message batches
        messages_batch = [
            [
                {"role": "system", "content": sys_msg},
                {"role": "user", "content": tmpl.format(**n)},
            ]
            for n in chunk
        ]

        # Call LM Studio with batched requests
        try:
            outs = chat_completion(
                messages_batch, model=theology_model, temperature=0.0
            )
            batch_lat_ms = int((time.time() - batch_start) * 1000)

            # Process responses
            for n, out in zip(chunk, outs, strict=False):
                try:
                    # Parse and validate JSON response
                    data = safe_json_parse(
                        out.text, required_keys=["insight", "confidence"]
                    )

                    insight_text = data["insight"]
                    confidence = float(data["confidence"])

                    # Validate confidence range
                    if not (0.0 <= confidence <= 1.0):
                        raise ValueError(f"Confidence {confidence} out of range [0,1]")

                    # Evaluate confidence gates
                    confidence_status = evaluate_confidence(confidence)

                    # Validate insight length (150-250 words)
                    word_count = len(insight_text.split())
                    if not (150 <= word_count <= 250):
                        log_json(
                            LOG,
                            30,
                            "insight_length_warning",
                            noun=n.get("name"),
                            word_count=word_count,
                            expected="150-250",
                        )

                    # Estimate tokens (rough approximation: 4 chars per token)
                    tokens_used = len(out.text) // 4
                    total_tokens += tokens_used

                    # Persist to database (optional for testing)
                    if GEMATRIA_DSN:
                        try:
                            with psycopg.connect(
                                GEMATRIA_DSN
                            ) as conn, conn.cursor() as cur:
                                cur.execute(
                                    """INSERT INTO ai_enrichment_log
                                       (run_id,node,noun_id,model_name,confidence_model,
                                        confidence_score,insights,significance,tokens_used)
                                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                                    (
                                        run_id,
                                        "enrichment",
                                        uuid.uuid4(),
                                        theology_model,
                                        None,  # No separate confidence model in new approach
                                        confidence,
                                        insight_text[:250],
                                        "Live LM Studio enrichment",
                                        tokens_used,
                                    ),
                                )
                                conn.commit()
                        except Exception as db_error:
                            log_json(
                                LOG, 30, "db_persistence_failed", error=str(db_error)
                            )
                            # Continue with enrichment even if DB fails

                    # Add to enriched nouns
                    enriched_noun = n.copy()
                    enriched_noun["confidence"] = confidence
                    enriched_noun["insights"] = insight_text
                    enriched_nouns.append(enriched_noun)

                    log_json(
                        LOG,
                        20,
                        "noun_enriched",
                        noun=n.get("name"),
                        confidence=confidence,
                        tokens=tokens_used,
                    )

                except Exception as e:
                    log_json(
                        LOG,
                        30,
                        "noun_enrichment_failed",
                        noun=n.get("name"),
                        error=str(e),
                        raw_response=out.text[:200],
                    )
                    continue

            # Emit batch metrics
            metrics_client.emit(
                {
                    "run_id": run_id,
                    "node": "enrichment",
                    "event": "batch_processed",
                    "batch_size": len(chunk),
                    "latency_ms": batch_lat_ms,
                    "success_count": len(enriched_nouns)
                    - (len(enriched_nouns) - len(chunk)),
                }
            )

        except Exception as e:
            log_json(
                LOG,
                40,
                "batch_enrichment_failed",
                batch_start=i,
                batch_size=len(chunk),
                error=str(e),
            )
            continue

    log_json(
        LOG,
        20,
        "enrichment_complete",
        enriched_count=len(enriched_nouns),
        total_tokens=total_tokens,
    )
    state["enriched_nouns"] = enriched_nouns
    state["ai_enrichments_generated"] = len(enriched_nouns)
    return state
