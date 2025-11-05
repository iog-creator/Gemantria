#!/usr/bin/env bash

set -euo pipefail



BASE_URL="${OPENAI_BASE_URL:-http://127.0.0.1:9994/v1}"

LM_BIN="${LM_BIN:-lms}"   # if you have the LM Studio CLI, set LM_BIN=lms; otherwise we operate via REST only

TIMEOUT="${TIMEOUT:-3}"



usage() {

  cat <<USAGE

lmstudioctl.sh — idempotent controls for LM Studio (REST-first)



Commands:

  health           -> 200 OK from /models

  models           -> list model IDs (first 200 lines)

  ps               -> LM CLI: lms ps (if available), else "CLI not set"

  load <model_id>  -> POST /models/load (if supported by your build) else no-op

  smoke            -> theology+math quick calls using env models (no GUI needed)

  start            -> prints guidance for GUI/CLI since headless varies by build

  stop             -> prints guidance; actual stop is manual unless CLI is present



Env:

  OPENAI_BASE_URL (default http://127.0.0.1:9994/v1)

  THEOLOGY_MODEL, MATH_MODEL, EMBEDDING_MODEL, RERANKER_MODEL (must match docs/MODEL_MANIFEST.md)

  LM_BIN (optional CLI name e.g. "lms")

USAGE

}



die(){ echo "ERR:" "$@" >&2; exit 1; }



health(){

  curl -fsS --max-time "$TIMEOUT" "$BASE_URL/models" >/dev/null && echo "OK: $BASE_URL reachable" || die "LM Studio not reachable at $BASE_URL"

}



models(){

  curl -fsS --max-time "$TIMEOUT" "$BASE_URL/models" | sed -n '1,200p'

}



ps(){

  if command -v "$LM_BIN" >/dev/null 2>&1; then

    "$LM_BIN" ps || true

  else

    echo "NOTE: LM_BIN not set or cli not installed; ps unavailable"

  fi

}



load(){

  mid="${1:-}"; [ -n "$mid" ] || die "usage: $0 load <model_id>"

  # many LM Studio builds don't expose a load endpoint; we try, else warn.

  if curl -fsS --max-time "$TIMEOUT" -X POST "$BASE_URL/models/load" -H 'content-type: application/json' \

      -d "{\"model\": \"$mid\"}" >/dev/null 2>&1; then

    echo "Requested load: $mid"

  else

    echo "WARN: model load endpoint not available; open the model in LM Studio UI or ensure CLI supports it."

  fi

}



smoke(){

  # Load environment if .env.local exists
  if [ -f ".env.local" ]; then
    set -a
    source .env.local
    set +a
  fi

  : "${THEOLOGY_MODEL:?THEOLOGY_MODEL required}"

  : "${MATH_MODEL:?MATH_MODEL required}"

  py=$(cat <<'PY'

import os, json, sys, requests

base=os.environ.get("OPENAI_BASE_URL","http://127.0.0.1:9994/v1")

def ask(mid, prompt):

    r=requests.post(f"{base}/chat/completions", json={

        "model": mid,

        "messages":[{"role":"user","content":prompt}],

        "max_tokens":128,"temperature":0.2

    }, timeout=15)

    r.raise_for_status()

    j=r.json()

    text=j.get("choices",[{}])[0].get("message",{}).get("content","").strip()

    print("HINT:model=", mid)

    print("HINT:text=", text[:180])

ask(os.environ["THEOLOGY_MODEL"], "Define 'covenant' in Genesis in one sentence.")

ask(os.environ["MATH_MODEL"], "Compute: (37^2 - 13^2)/12 . Return only a number.")

PY

)

  python3 - <<PY

$py

PY

}



start(){

  cat <<'TXT'

LM Studio start guidance:

- If using GUI: Open LM Studio, set:

  • Server: OpenAI-compatible REST at http://127.0.0.1:9994/v1

  • Load models from docs/MODEL_MANIFEST.md

  • GPU Layers: ALL; KV cache: GPU; Batch: 256–512; Context: 4096

- If using CLI (example): LM_BIN=lms; use "lms serve --port 9994" or your distro's command.

- This project prefers REST-first; headless flags vary by version, so we keep this step manual unless your CLI is standardized.

TXT

}



stop(){

  if pgrep -f "lm-studio|LM Studio|lms serve" >/dev/null 2>&1; then

    echo "INFO: Found LM Studio processes:"

    pgrep -af "lm-studio|LM Studio|lms serve" || true

    echo "ACTION: Stop via GUI or terminate the listed PIDs (graceful preferred)."

  else

    echo "OK: no LM Studio process detected"

  fi

}



cmd="${1:-}"; shift || true

case "$cmd" in

  health) health ;;

  models) models ;;

  ps) ps ;;

  load) load "$@" ;;

  smoke) smoke ;;

  start) start ;;

  stop) stop ;;

  ""|-h|--help|help) usage ;;

  *) usage; exit 2 ;;

esac
