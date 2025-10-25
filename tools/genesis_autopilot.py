import glob
import json
import os
import re
import shlex
import subprocess
import sys
import time

import requests

"""Headless-only Autopilot: resolve CLI strictly; no UI fallback allowed."""
try:
    cfg = json.loads(
        subprocess.check_output(["python3", "tools/lm_bootstrap_strict.py"], text=True)
    )
except subprocess.CalledProcessError as e:
    print((e.stdout or "") + (e.stderr or ""), file=sys.stderr)
    sys.exit(1)
os.environ["LM_CLI"] = cfg["cli"]
LM = os.environ["LM_CLI"]  # absolute path to LM Studio CLI

PORTS = {"embed": 9994, "llm": 9991, "critic": 9993}
# Use remote server if available
USE_REMOTE = os.environ.get("USE_REMOTE_LM_STUDIO", "true").lower() == "true"
REMOTE_HOST = os.environ.get("LM_STUDIO_REMOTE_HOST", "192.168.1.119")
MODELS = {
    # Prefer explicit local/remote identifiers via env; fall back to defaults
    "embed": os.environ.get(
        "EMBED_MODEL_ID", os.environ.get("EMBEDDING_MODEL", "text-embedding-bge-m3")
    ),
    "llm": os.environ.get(
        "LLM_MODEL_ID", os.environ.get("ANSWERER_MODEL", "Qwen2.5-14B-Instruct-GGUF")
    ),
    "critic": os.environ.get("CRITIC_MODEL_ID", "skywork-critic-llama-3.1-8b"),
}
QUANT_OK = {
    "llm": re.compile(r"Q4_K_M", re.I),
    "critic": re.compile(r"Q4_K_(S|M)", re.I),
    # embeddings likely non-GGUF → "UNKNOWN" ok
}

ROOTS = [
    os.path.expanduser("~/Library/Application Support/LM Studio/models"),
    os.path.expandvars(r"%APPDATA%\\LM Studio\\models"),
    os.path.expanduser("~/.cache/lm-studio/models"),
]


def run(cmd):
    p = subprocess.run(
        shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )
    return p.returncode, p.stdout


def start_server(port, model):
    if USE_REMOTE:
        # For remote server, just wait for the correct model to be loaded
        print(f"[REMOTE] Waiting for {model} on {REMOTE_HOST}:{port}")
        _wait_ready_remote(port, model)
    else:
        # one big model at a time
        stop_all()
        # Start the server only; LM Studio serves models by id at request time
        code, out = run(f"{LM} server start --port {port}")
        if code != 0:
            print(f"Failed to start server on port {port}: {out}", file=sys.stderr)
            sys.exit(1)
        _wait_ready(port)


def stop_all():
    if not USE_REMOTE:
        run(f"{LM} server stop")
        run(f"{LM} unload --all")


def _wait_ready(port, timeout=30):
    url = f"http://127.0.0.1:{port}/v1/models"
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            r = requests.get(url, timeout=2)
            if r.ok and "data" in r.json():
                return
        except Exception:
            pass
        time.sleep(0.5)
    print(f"Server on :{port} not ready", file=sys.stderr)
    sys.exit(1)


def assert_no_ui_server():
    for port in (1234, 1235):
        try:
            requests.get(f"http://127.0.0.1:{port}/v1/models", timeout=1)
            print(
                f"[FAIL] UI server detected on :{port}. Close LM Studio UI. Headless-only mode enforced.",  # noqa: E501
                file=sys.stderr,
            )
            sys.exit(1)
        except Exception:
            pass


def _wait_ready_remote(port, expected_model):
    # Allow longer startup via env override
    timeout = int(os.environ.get("LM_STUDIO_REMOTE_TIMEOUT", "120"))
    url = f"http://{REMOTE_HOST}:{port}/v1/models"
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            r = requests.get(url, timeout=5)
            if r.ok:
                data = r.json().get("data", [])
                model_ids = [m.get("id", "") for m in data]
                if expected_model in model_ids:
                    print(f"[REMOTE] Found {expected_model} on {REMOTE_HOST}:{port}")
                    return
                else:
                    print(
                        f"[REMOTE] Waiting for {expected_model}, currently loaded: {model_ids}"
                    )
        except Exception as e:
            msg = str(e)
            print(f"[REMOTE] Connection failed: {msg}")
            # Fail-fast on explicit connection refused (server not running)
            if (
                "Connection refused" in msg
                or "Errno 111" in msg
                or "ECONNREFUSED" in msg
            ):
                print(
                    f"[FAIL] Remote server not reachable at {REMOTE_HOST}:{port} (connection refused)",  # noqa: E501
                    file=sys.stderr,
                )
                sys.exit(1)
        time.sleep(3)
    print(
        f"[REMOTE] Timeout waiting for {expected_model} on {REMOTE_HOST}:{port}",
        file=sys.stderr,
    )
    sys.exit(1)


def smoke_chat(port, model):
    host = REMOTE_HOST if USE_REMOTE else "127.0.0.1"
    url = f"http://{host}:{port}/v1/chat/completions"
    try:
        resp = requests.post(
            url,
            json={
                "model": model,
                "messages": [{"role": "user", "content": "Say OK."}],
                "max_tokens": 5,
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        print(f"[OK] chat live: model={data.get('model', model)}")
    except Exception as e:
        print(f"[FAIL] chat smoke failed on {url}: {e}", file=sys.stderr)
        sys.exit(1)


def active_models(port):
    host = REMOTE_HOST if USE_REMOTE else "127.0.0.1"
    r = requests.get(f"http://{host}:{port}/v1/models", timeout=5)
    r.raise_for_status()
    return [m.get("id", "") for m in r.json().get("data", [])]


def gguf_quant_for(model_id):
    # best effort: find GGUF and parse quant suffix (…-Q4_K_M.gguf)
    hits = []
    for root in ROOTS:
        if not root or not os.path.isdir(root):
            continue
        for p in glob.glob(os.path.join(root, "**", "*.gguf"), recursive=True):
            if any(s for s in model_id.split("/") if s and s.lower() in p.lower()):
                hits.append(p)
    if not hits:
        return "UNKNOWN", None
    path = hits[0]
    m = re.search(r"(Q[0-9]_(?:K_[MS]|0))\.gguf$", path, re.I)
    return (m.group(1).upper() if m else "UNKNOWN"), path


def audit_phase(phase):
    port = PORTS[phase]
    ids = active_models(port)
    if not ids:
        print(f"[FAIL] :{port} has no active model", file=sys.stderr)
        sys.exit(1)
    expected = MODELS[phase]
    if expected not in ids:
        print(
            f"[FAIL] :{port} expected model '{expected}' not found. Available: {ids}",  # noqa: E501
            file=sys.stderr,
        )
        sys.exit(1)
    quant, path = gguf_quant_for(expected)
    print(f"[OK] {phase} -> id={expected} quant={quant} path={path or '<n/a>'}")
    if phase in QUANT_OK and quant != "UNKNOWN" and not QUANT_OK[phase].search(quant):
        print(f"[FAIL] {phase} quant {quant} not allowed", file=sys.stderr)
        sys.exit(1)


def set_env_defaults():
    host = REMOTE_HOST if USE_REMOTE else "127.0.0.1"
    os.environ.setdefault("EMBED_PROFILE", "bge_m3")
    os.environ.setdefault("EMBED_URL", f"http://{host}:{PORTS['embed']}/v1")
    os.environ.setdefault("LLM_URL", f"http://{host}:{PORTS['llm']}/v1")
    os.environ.setdefault("CRITIC_URL", f"http://{host}:{PORTS['critic']}/v1")
    os.environ.setdefault("EDGE_ALPHA", "0.60")
    os.environ.setdefault("EDGE_STRONG", "0.88")
    os.environ.setdefault("EDGE_WEAK", "0.70")
    os.environ.setdefault("NN_TOPK", "10")
    os.environ.setdefault("EMBED_BATCH_MAX", "2048")
    os.environ.setdefault("STATS_CENTRALITY_FALLBACK", "1")


def run_graph(book, batch_size):
    code, out = run(
        f"python3 -m src.graph.graph --book {book} --batch-size {batch_size}"
    )
    print(out)
    if code != 0:
        print("[FAIL] graph run failed", file=sys.stderr)
        sys.exit(1)
    # Fail-fast if health gate or pipeline reported errors
    if '"qwen_unavailable": true' in out:
        print("[FAIL] Qwen Live Gate failed (qwen_unavailable)", file=sys.stderr)
        sys.exit(1)
    if (
        '"pipeline_failed": true' in out
        or '"network_aggregation_failed": true' in out
        or '"confidence_validation_failed": true' in out
    ):
        print("[FAIL] pipeline reported failure", file=sys.stderr)
        sys.exit(1)


def sanity_sql():
    dsn = os.environ.get("GEMATRIA_DSN")
    if not dsn:
        print("[WARN] GEMATRIA_DSN not set; skipping SQL checks")
        return

    def psql(q):
        code, out = run(f'psql "{dsn}" -c "{q}"')
        print(out)

    psql(
        "SELECT COUNT(*) AS null_scores FROM concept_relations WHERE rerank_score IS NULL;"
    )
    psql("SELECT relation_type, COUNT(*) FROM concept_relations GROUP BY 1;")
    psql(
        "SELECT AVG(rerank_score) avg, MIN(rerank_score) min, MAX(rerank_score) max FROM concept_relations;"  # noqa: E501
    )
    psql(
        "SELECT cosine, rerank_score, edge_strength, relation_type FROM concept_relations ORDER BY edge_strength DESC LIMIT 20;"  # noqa: E501
    )


def main():
    if len(sys.argv) < 2:
        print(
            "usage: python tools/genesis_autopilot.py Genesis [--batch 10]",
            file=sys.stderr,
        )
        sys.exit(1)
    book = sys.argv[1]
    batch = 10
    if "--batch" in sys.argv:
        batch = int(sys.argv[sys.argv.index("--batch") + 1])
    set_env_defaults()
    assert_no_ui_server()

    # Phase A: embeddings
    print("\n== Phase A: embeddings ==")
    start_server(PORTS["embed"], MODELS["embed"])
    audit_phase("embed")
    # smoke test /v1/embeddings with real call
    code, out = run("python3 tools/smoke_lms_embeddings.py")
    print(out)
    if code != 0:
        sys.exit(1)
    # Ensure chat server is ready in remote mode before graph (health gate needs chat)
    if USE_REMOTE:
        _wait_ready_remote(PORTS["llm"], MODELS["llm"])  # christian model on :9991
        smoke_chat(PORTS["llm"], MODELS["llm"])  # ensure inference actually works
    run_graph(book, batch)
    sanity_sql()

    # Phase B: answerer
    print("\n== Phase B: answerer ==")
    start_server(PORTS["llm"], MODELS["llm"])
    audit_phase("llm")
    # your LangGraph nodes will call the LLM via LLM_URL during downstream steps

    # Phase C: critic
    print("\n== Phase C: critic ==")
    start_server(PORTS["critic"], MODELS["critic"])
    audit_phase("critic")
    # your Verify node runs within the pipeline; ensure it reads CRITIC_URL

    print("\nAll phases completed.")


if __name__ == "__main__":
    main()
