#!/usr/bin/env bash

set -euo pipefail

# Validate .env file integrity and required variables
# This script ensures the .env file has all required variables

ENV_FILE=".env"
EXAMPLE_FILE="env_example.txt"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Required variables (from env_example.txt, excluding comments and optional)
REQUIRED_VARS=(
    "BIBLE_DB_DSN"
    "GEMATRIA_DSN"
    "LM_STUDIO_HOST"
    "THEOLOGY_MODEL"
    "MATH_MODEL"
    "EMBEDDING_MODEL"
    "RERANKER_MODEL"
    "USE_QWEN_EMBEDDINGS"
    "ENFORCE_QWEN_LIVE"
    "ALLOW_MOCKS_FOR_TESTS"
    "BATCH_SIZE"
    "VECTOR_DIM"
    "ENABLE_RELATIONS"
    "ENABLE_RERANK"
    "LOG_LEVEL"
    "METRICS_ENABLED"
    "WORKFLOW_ID"
    "PIP_REQUIRE_VENV"
    "ALLOW_PARTIAL"
    "CHECKPOINTER"
)

echo "🔍 Validating .env file integrity..."
echo ""

# Check if .env exists
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}❌ ERROR: $ENV_FILE does not exist${NC}"
    exit 1
fi

# Check if .env.example exists
if [ ! -f "$EXAMPLE_FILE" ]; then
    echo -e "${YELLOW}⚠️  WARNING: $EXAMPLE_FILE does not exist for comparison${NC}"
fi

MISSING_VARS=()
INVALID_VARS=()

# Check required variables
for var in "${REQUIRED_VARS[@]}"; do
    if ! grep -q "^${var}=" "$ENV_FILE" 2>/dev/null; then
        MISSING_VARS+=("$var")
    else
        # Check if variable has a value (not empty)
        value=$(grep "^${var}=" "$ENV_FILE" | cut -d'=' -f2-)
        if [ -z "$value" ]; then
            INVALID_VARS+=("$var (empty value)")
        fi
    fi
done

# Report results
if [ ${#MISSING_VARS[@]} -eq 0 ] && [ ${#INVALID_VARS[@]} -eq 0 ]; then
    echo -e "${GREEN}✅ SUCCESS: All required environment variables are present and valid${NC}"
    echo ""
    echo "📊 Environment Summary:"
    echo "   - Total required variables: ${#REQUIRED_VARS[@]}"
    echo "   - File size: $(wc -c < "$ENV_FILE") bytes"
    echo "   - Last modified: $(stat -c '%y' "$ENV_FILE" | cut -d'.' -f1)"
    exit 0
else
    echo -e "${RED}❌ VALIDATION FAILED${NC}"
    echo ""

    if [ ${#MISSING_VARS[@]} -gt 0 ]; then
        echo -e "${RED}Missing variables:${NC}"
        for var in "${MISSING_VARS[@]}"; do
            echo "   - $var"
        done
    fi

    if [ ${#INVALID_VARS[@]} -gt 0 ]; then
        echo -e "${YELLOW}Invalid variables:${NC}"
        for var in "${INVALID_VARS[@]}"; do
            echo "   - $var"
        done
    fi

    echo ""
    echo "💡 To fix: Run './scripts/env/edit_env.sh' to add missing variables"
    echo "💡 Compare with: env_example.txt for reference values"
    exit 1
fi
