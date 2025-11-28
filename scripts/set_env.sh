#!/bin/bash

# Environment Setup Script
# Sets all required environment variables for Gemantria operations

echo "🔧 Setting up Gemantria environment variables..."

# LM Studio Configuration
export LM_STUDIO_HOST="http://127.0.0.1:9994"
export THEOLOGY_MODEL="christian-bible-expert-v2.0-12b"
export GENERAL_MODEL="Qwen2.5-14B-Instruct-GGUF"
export MATH_MODEL="self-certainty-qwen3-1.7b-base-math"
export EMBEDDING_MODEL="text-embedding-bge-m3"
export RERANKER_MODEL="qwen.qwen3-reranker-0.6b"

# AI Configuration
export USE_QWEN_EMBEDDINGS=true
export ENFORCE_QWEN_LIVE=1
export ALLOW_MOCKS_FOR_TESTS=0

# Database Configuration (defaults - customize as needed)
export GEMATRIA_DSN="${GEMATRIA_DSN:-postgresql://mccoy@/gematria?host=/var/run/postgresql}"
export BIBLE_DB_DSN="${BIBLE_DB_DSN:-postgresql://postgres@/bible_db?host=/var/run/postgresql}"

# Pipeline Configuration
export BATCH_SIZE=50
export ALLOW_PARTIAL=0
export CHECKPOINTER=memory

# Logging and Development
export LOG_LEVEL=INFO
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

echo "✅ Environment variables set:"
echo "  LM_STUDIO_HOST: $LM_STUDIO_HOST"
echo "  THEOLOGY_MODEL: $THEOLOGY_MODEL"
echo "  RERANKER_MODEL: $RERANKER_MODEL"
echo "  EMBEDDING_MODEL: $EMBEDDING_MODEL"
echo "  USE_QWEN_EMBEDDINGS: $USE_QWEN_EMBEDDINGS"
echo ""
echo "💡 TIP: Add 'source scripts/set_env.sh' to your shell profile"
echo "   or run it before any AI operations"















