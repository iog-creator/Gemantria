from __future__ import annotations

import os
import re
import time
import uuid

import psycopg

from src.infra.metrics_core import get_metrics_client
from src.infra.structured_logger import get_logger, log_json
from src.services.lmstudio_client import chat_completion
from src.utils.json_sanitize import parse_llm_json

LOG = get_logger("gemantria.enrichment")

GEMATRIA_DSN = os.getenv("GEMATRIA_DSN")

# Confidence gates
SOFT = float(os.getenv("AI_CONFIDENCE_SOFT", 0.90))
HARD = float(os.getenv("AI_CONFIDENCE_HARD", 0.95))


def evaluate_confidence(conf, run_id=None, node=None):
    """Evaluate confidence against soft/hard gates."""
    if conf < SOFT:
        status = "fail"
        metrics_client = get_metrics_client()
        metrics_client.emit({"event": "ai_conf_hard_fail", "run_id": run_id, "node": node})
    elif conf < HARD:
        status = "warn"
        metrics_client = get_metrics_client()
        metrics_client.emit({"event": "ai_conf_soft_warn", "run_id": run_id, "node": node})
    else:
        status = "pass"
    return status


def enrichment_node(state: dict) -> dict:
    # Pipeline-level Qwen Live Gate already verified all required models are available
    theology_model = os.getenv("THEOLOGY_MODEL")
    if not theology_model:
        raise ValueError("THEOLOGY_MODEL environment variable required")

    nouns = state.get("validated_nouns", [])
    if not nouns:
        log_json(LOG, 20, "enrichment_start", noun_count=0, message="No nouns to enrich")
        state["enriched_nouns"] = []
        state["ai_enrichments_generated"] = 0
        return state

    # Filter out nouns without valid Hebrew text (known issue: "Unknown" nouns)
    valid_nouns = []
    for noun in nouns:
        hebrew = noun.get("hebrew", noun.get("surface", noun.get("name", "")))
        # Skip empty, null, or "Unknown" Hebrew
        if not hebrew or not hebrew.strip() or hebrew.strip().lower() in ("unknown", "null", "none"):
            log_json(LOG, 20, "skipping_invalid_hebrew", noun=noun.get("name"), hebrew=hebrew)
            continue
        # Skip Strong's numbers (H#### format) - these aren't Hebrew text
        if re.match(r"^H\d+$", hebrew.strip(), re.IGNORECASE):
            log_json(LOG, 20, "skipping_strongs_number", noun=noun.get("name"), hebrew=hebrew)
            continue
        valid_nouns.append(noun)

    nouns = valid_nouns
    if not nouns:
        log_json(LOG, 20, "enrichment_start", noun_count=0, message="No valid nouns to enrich after filtering")
        state["enriched_nouns"] = []
        state["ai_enrichments_generated"] = 0
        return state

    log_json(LOG, 20, "enrichment_start", noun_count=len(nouns))
    metrics_client = get_metrics_client()
    run_id = state.get("run_id", uuid.uuid4())

    # 1) Build prompts once per noun
    sys_msg = (
        "You are an expert biblical scholar with deep theological insight. Provide a comprehensive 200-300 word theological analysis and a confidence score (0.0-1.0). You have sufficient context length to provide detailed analysis. Return only valid JSON with keys 'insight' and 'confidence'. "  # noqa: E501
        'When a node expects JSON, respond with only minified JSON on one line, no markdown, matching the provided schema; include "confidence" as a float in [0,1].'  # noqa: E501
    )

    # Escape Hebrew text to prevent JSON parsing issues
    import json

    def escape_hebrew(text):
        """Escape Hebrew text for safe inclusion in prompts."""
        if not text:
            return ""
        # First escape backslashes, then use JSON escaping for Unicode
        text = text.replace("\\", "\\\\")  # Escape literal backslashes
        return json.dumps(text)[1:-1]  # JSON escape Unicode but remove quotes

    def build_enrichment_prompt(noun):
        """Build enrichment prompt, leveraging AI-discovered analysis when available."""
        # Get fields with empty string fallbacks (not "Unknown") since we filter invalid nouns
        name = noun.get("name", noun.get("hebrew", noun.get("surface", "")))
        hebrew = noun.get("hebrew", noun.get("surface", ""))
        verse = noun.get("primary_verse", "")
        base_info = f"Noun: {name}\nHebrew: {escape_hebrew(hebrew)}\nPrimary Verse: {verse}\n"

        # Leverage AI-discovered analysis if available
        if noun.get("ai_discovered"):
            ai_analysis = (
                f"AI Analysis:\n"
                f"- Letters: {', '.join(noun.get('letters', []))}\n"
                f"- Gematria Value: {noun.get('gematria', 'Unknown')}\n"
                f"- Classification: {noun.get('classification', 'Unknown')} (person/place/thing)\n"
                f"- Initial Meaning: {noun.get('meaning', 'Not analyzed')}\n"
            )
            task_desc = (
                "This noun was discovered and initially analyzed by AI. "
                "Build upon this analysis to provide deeper theological insight. "
                "Explore how the Hebrew letters, gematria value, and classification "
                "contribute to the noun's biblical significance, symbolic meanings, "
                "and connections to broader theological themes. "
            )
        else:
            ai_analysis = ""
            task_desc = (
                "Provide a detailed theological analysis exploring biblical significance, "
                "historical context, symbolic meanings, and theological implications. "
            )

        full_prompt = (
            base_info + ai_analysis + f"Task: {task_desc} "
            "Provide a comprehensive 200-300 word scholarly analysis. "
            'Return JSON: {{"insight": "...detailed analysis...", "confidence": <0.90-1.0>}}'
        )

        return full_prompt

    # Build prompts for each noun
    prompts = [build_enrichment_prompt(noun) for noun in nouns]

    # 2) Process in batches of 4 to avoid overwhelming LM Studio
    batch_size = 4
    enriched_nouns = []
    total_tokens = 0

    for i in range(0, len(nouns), batch_size):
        chunk = nouns[i : i + batch_size]
        batch_start = time.time()

        # Build message batches using pre-built prompts
        messages_batch = []
        for j, n in enumerate(chunk):
            try:
                # Use the corresponding prompt from our pre-built prompts array
                prompt_idx = i + j  # Global index in the prompts array
                content = prompts[prompt_idx] if prompt_idx < len(prompts) else build_enrichment_prompt(n)
                messages_batch.append([{"role": "system", "content": sys_msg}, {"role": "user", "content": content}])
            except Exception as e:
                log_json(LOG, 40, "template_format_error", noun=n.get("name"), error=str(e))
                # Fallback: use basic format (no "Unknown" fallbacks)
                name = n.get("name", n.get("hebrew", n.get("surface", "")))
                hebrew = n.get("hebrew", n.get("surface", ""))
                verse = n.get("primary_verse", "")
                content = f"Noun: {name}\nHebrew: {escape_hebrew(hebrew)}\nPrimary Verse: {verse}\nTask: Provide theological analysis. Return JSON with insight and confidence."
                messages_batch.append([{"role": "system", "content": sys_msg}, {"role": "user", "content": content}])

        # Call LM Studio with batched requests
        try:
            outs = chat_completion(messages_batch, model=theology_model, temperature=0.0)
            batch_lat_ms = int((time.time() - batch_start) * 1000)

            # Process responses
            for n, out in zip(chunk, outs, strict=False):
                try:
                    # Parse and validate JSON response with repair + retry up to 2
                    retry = 0
                    raw_text = out.text
                    while True:
                        try:
                            data = parse_llm_json(raw_text)
                            break
                        except Exception:
                            if retry >= 2:
                                raise
                            # Re-prompt this single item with stricter instruction
                            retry_prompt = (
                                build_enrichment_prompt(n) + "\nReturn only valid JSON; previous reply was invalid."
                            )
                            messages = [
                                {"role": "system", "content": sys_msg},
                                {
                                    "role": "user",
                                    "content": retry_prompt,
                                },
                            ]
                            metrics_client.emit(
                                {
                                    "event": "enrichment_json_retry",
                                    "retry": retry + 1,
                                    "run_id": run_id,
                                    "node": "enrichment",
                                }
                            )
                            raw_text = chat_completion([messages], model=theology_model, temperature=0.0)[0].text
                            retry += 1

                    # enforce required keys; extract confidence if needed
                    if "confidence" not in data:
                        import json as _json  # noqa: E402

                        # Try to extract confidence from text if JSON is incomplete
                        m = re.search(
                            r"\bconfidence(?:\s+score)?\s*(?:is|:)?\s*(0?\.\d+|1(?:\.0+)?)\b",
                            _json.dumps(data, ensure_ascii=False) + " " + raw_text,
                            re.I,
                        )
                        if m:
                            data["confidence"] = float(m.group(1))
                        else:
                            # If truncated and no confidence found, use default and log warning
                            log_json(
                                LOG,
                                30,
                                "json_truncated_no_confidence",
                                noun=n.get("name"),
                                raw_preview=raw_text[:200] if raw_text else "",
                            )
                            # Use default confidence for truncated responses
                            data["confidence"] = 0.85  # Default confidence for incomplete responses
                            # Continue processing instead of failing

                    insight_text = data.get("insight", "").strip()
                    confidence = float(data.get("confidence", 0.0))

                    # Hard schema checks
                    missing = [k for k in ("insight", "confidence") if k not in data]
                    if missing:
                        raise ValueError(f"JSON response missing required keys: {missing}")
                    if not (0.0 <= confidence <= 1.0):
                        raise ValueError("confidence must be a float in [0,1]")

                    # Evaluate confidence gates
                    evaluate_confidence(confidence, run_id=run_id, node="enrichment")

                    # Validate insight length (200-300 words)
                    word_count = len(insight_text.split())
                    if not (200 <= word_count <= 300):
                        log_json(
                            LOG,
                            30,
                            "insight_length_warning",
                            noun=n.get("name"),
                            word_count=word_count,
                            expected="200-300",
                        )

                    # Estimate tokens (rough approximation: 4 chars per token)
                    tokens_used = len(out.text) // 4
                    total_tokens += tokens_used

                    # Persist to database (optional for testing)
                    if GEMATRIA_DSN:
                        try:
                            with (
                                psycopg.connect(GEMATRIA_DSN) as conn,
                                conn.cursor() as cur,
                            ):
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
                            log_json(LOG, 30, "db_persistence_failed", error=str(db_error))
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
                    "items_in": len(chunk),
                    "items_out": len(enriched_nouns),
                    "duration_ms": batch_lat_ms,
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
