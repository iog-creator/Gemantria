# MODEL MANIFEST (authoritative)

Provider: LM Studio (all services)

Base URL: http://127.0.0.1:9994/v1

## Active Models

- Theology (chat): christian-bible-expert-v2.0-12b              # GGUF name as LM Studio exposes it

- Embeddings:    text-embedding-bge-m3                          # 1024-dim

- Reranker:      qwen3-reranker-8b

- Math (reasoning/calc): self-certainty-qwen3-1.7b-base-math  # LM Studio GGUF model (available)

## Inactive / Optional

- vLLM: sleepdeprived3/Reformed-Christian-Bible-Expert-12B (BF16) — SHELVED on 16GB

## Rules

1) This file is the SSOT for all model names.

2) .env.local must match this manifest exactly.

3) Code may not hardcode model names; it must read from env vars listed below.

## Env Vars (required)

INFERENCE_PROVIDER=lmstudio

OPENAI_BASE_URL=http://127.0.0.1:9994/v1

THEOLOGY_MODEL=christian-bible-expert-v2.0-12b

EMBEDDING_MODEL=BAAI/bge-m3

RERANKER_MODEL=Qwen/Qwen3-Reranker-8B

MATH_MODEL=self-certainty-qwen3-1.7b-base-math          # Must match LM Studio listing exactly
