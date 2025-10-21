from __future__ import annotations
import uuid, os, psycopg
from src.services.lmstudio_client import get_lmstudio_client
from src.infra.structured_logger import get_logger, log_json
LOG = get_logger("gemantria.enrichment")

GEMATRIA_DSN = os.getenv("GEMATRIA_DSN")

def enrichment_node(state: dict) -> dict:
    client = get_lmstudio_client()
    nouns = state.get("validated_nouns", [])
    log_json(LOG, 20, "enrichment_start", noun_count=len(nouns), nouns=nouns)
    out = []
    with psycopg.connect(GEMATRIA_DSN) as conn, conn.cursor() as cur:
        for n in nouns:
            run_id = state.get("run_id", uuid.uuid4())
            try:
                log_json(LOG, 20, "processing_noun", noun=n.get("name"), hebrew=n.get("hebrew"))
                insight = client.generate_insight(n)
                log_json(LOG, 20, "insight_generated", tokens=insight.get("tokens"))
                confidence = client.confidence_check(n, n["value"])
                log_json(LOG, 20, "confidence_checked", confidence=confidence)
                cur.execute(
                    """INSERT INTO ai_enrichment_log
                       (run_id,node,noun_id,model_name,confidence_model,
                        confidence_score,insights,significance,tokens_used)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (run_id,"enrichment",uuid.uuid4(),
                     os.getenv("THEOLOGY_MODEL"),os.getenv("MATH_MODEL"),
                     confidence,insight["text"][:250],"Auto-generated significance",
                     insight["tokens"])
                )
                conn.commit()
                n["confidence"] = confidence
                n["insights"] = insight["text"]
                out.append(n)
            except Exception as e:
                log_json(LOG,30,"ai_enrichment_failed",error=str(e))
                continue
    log_json(LOG, 20, "enrichment_complete", enriched_count=len(out))
    state["enriched_nouns"] = out
    return state
