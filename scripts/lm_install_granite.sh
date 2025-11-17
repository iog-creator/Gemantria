#!/usr/bin/env bash
# Phase-7D: Granite Model Installation Helper
# Interactive script to guide Granite model installation via LM Studio CLI

set -euo pipefail

echo "Phase-7D: Granite Model Installation"
echo "===================================="
echo ""
echo "This script will guide you through installing Granite models using LM Studio CLI."
echo "You'll need to interactively select models from search results."
echo ""

# Check if lms CLI is available
if ! command -v lms &> /dev/null; then
    echo "ERROR: LM Studio CLI (lms) not found in PATH"
    echo "Please install LM Studio CLI or add it to your PATH"
    exit 1
fi

echo "✓ LM Studio CLI found: $(which lms)"
echo ""

# Function to prompt for model installation
install_model() {
    local model_name=$1
    local search_term=$2
    local expected_id=$3
    
    echo "Installing: $model_name"
    echo "Search term: $search_term"
    echo ""
    echo "When prompted, select: $expected_id"
    echo "Press Enter to continue..."
    read -r
    
    lms get "$search_term" || {
        echo "WARNING: Model installation may have been cancelled or failed"
        echo "You can retry this step manually with: lms get $search_term"
        return 1
    }
    
    echo ""
}

# Install Granite 4.0 H Tiny
install_model \
    "Granite 4.0 H Tiny (Local Agent Model)" \
    "granite" \
    "ibm-granite/granite-4.0-h-tiny-GGUF"

# Install Granite embedding model
install_model \
    "Granite Embedding English R2" \
    "granite-embedding" \
    "ibm-granite/granite-embedding-english-r2"

# Install Granite reranker model
install_model \
    "Granite Embedding Reranker English R2" \
    "granite-reranker" \
    "ibm-granite/granite-embedding-reranker-english-r2"

echo ""
echo "Installation complete!"
echo ""
echo "Verifying installed models..."
echo ""

# Verify installation
if python3 -m scripts.lm_models_ls 2>/dev/null; then
    echo ""
    echo "✓ Model verification complete"
else
    echo ""
    echo "WARNING: Could not verify models via API"
    echo "Make sure LM Studio server is running: lms server start"
fi

echo ""
echo "Next steps:"
echo "1. Update your .env file to use the GRANITE profile (see env_example.txt)"
echo "2. Verify model IDs match your installation: python -m scripts.lm_models_ls"
echo "3. Update LOCAL_AGENT_MODEL, EMBEDDING_MODEL, and RERANKER_MODEL in .env"
echo ""

