from __future__ import annotations
import uuid, os, psycopg
from src.services.lmstudio_client import get_lmstudio_client
from src.infra.structured_logger import get_logger, log_json
LOG = get_logger("gemantria.enrichment")

GEMATRIA_DSN = os.getenv("GEMATRIA_DSN")

def enrichment_node(state: dict) -> dict:
    client = get_lmstudio_client()
    nouns = state.get("nouns", [])
    out = []
    with psycopg.connect(GEMATRIA_DSN) as conn, conn.cursor() as cur:
        for n in nouns:
            run_id = state.get("run_id", uuid.uuid4())
            try:
                insight = client.generate_insight(n)
                confidence = client.confidence_check(n, n["value"])
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
    state["nouns"] = out
    return state
