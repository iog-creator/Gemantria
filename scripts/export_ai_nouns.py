import os, json, re, sys, uuid, datetime, psycopg

BAD = re.compile(r'[\u0000-\u0008\u000B\u000C\u000E-\u001F]')

def scrub(x):
    if isinstance(x,str): return BAD.sub('',x)
    if isinstance(x,list): return [scrub(v) for v in x]
    if isinstance(x,dict): return {k:scrub(v) for k,v in x.items()}
    return x

dsn = os.environ.get("DSN")
book = os.environ.get("BOOK","Genesis")
outp = os.environ.get("OUT","exports/ai_nouns.json")

with psycopg.connect(dsn) as conn, conn.cursor() as cur:
    cur.execute("""
      SELECT noun_id::text, surface, COALESCE(lemma,''), letters, gematria, class, analysis, sources
      FROM gematria.ai_nouns WHERE book=%s ORDER BY surface
    """,[book])
    nodes = []
    for rid, surface, lemma, letters, gematria, cls, analysis, sources in cur.fetchall():
        nodes.append({
            "noun_id": rid, "surface": surface, "lemma": lemma or None,
            "letters": letters, "gematria": int(gematria), "class": cls,
            "ai_discovered": True, "analysis": analysis or {}, "sources": sources
        })

data = {"schema":"gemantria/ai-nouns.v1","book":book,
        "generated_at": datetime.datetime.utcnow().isoformat()+"Z",
        "nodes": nodes}
data = scrub(data)
os.makedirs(os.path.dirname(outp), exist_ok=True)
with open(outp,"w",encoding="utf-8") as f: json.dump(data,f,ensure_ascii=False,indent=2)
print("SSOT_AI_NOUNS_WRITTEN", outp)
