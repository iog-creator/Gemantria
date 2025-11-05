#!/usr/bin/env python3
"""Lightweight vLLM server launcher for theology model.

Usage:
    HF_MODEL=sleepdeprived3/Reformed-Christian-Bible-Expert-12B \
    VLLM_PORT=8001 VLLM_GPU_UTIL=0.90 VLLM_MAXLEN=3072 \
    python scripts/vllm_serve.py
"""

import os
import subprocess
import sys

HF_MODEL = os.getenv("HF_MODEL", "sleepdeprived3/Reformed-Christian-Bible-Expert-12B")
PORT = os.getenv("VLLM_PORT", "8001")
GPU_UTIL = os.getenv("VLLM_GPU_UTIL", "0.90")  # 90% VRAM target
MAXLEN = os.getenv("VLLM_MAXLEN", "3072")
DTYPE = os.getenv("VLLM_DTYPE", "bfloat16")  # try bfloat16, fallback to float16 if needed
TP = os.getenv("VLLM_TENSOR_PARALLEL_SIZE", None)  # optional multi-GPU later
EXTRA = os.getenv("VLLM_EXTRA_FLAGS", "").strip()

cmd = [
    sys.executable,
    "-m",
    "vllm.entrypoints.api_server",
    "--model",
    HF_MODEL,
    "--dtype",
    DTYPE,
    "--gpu-memory-utilization",
    GPU_UTIL,
    "--max-model-len",
    MAXLEN,
    "--port",
    PORT,
    "--trust-remote-code",
]
if TP:
    cmd += ["--tensor-parallel-size", TP]
if EXTRA:
    cmd += EXTRA.split()

print("Launching vLLM:", " ".join(cmd))
sys.exit(subprocess.call(cmd))
