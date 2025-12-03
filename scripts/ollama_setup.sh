#!/usr/bin/env bash
# Phase-7D: Ollama Setup Script
# Automated setup and model installation for Ollama

set -euo pipefail

echo "Phase-7D: Ollama Setup"
echo "====================="
echo ""

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "Ollama not found. Installing..."
    echo ""
    echo "Please install Ollama from https://ollama.com/download"
    echo "Or run: curl -fsSL https://ollama.com/install.sh | sh"
    exit 1
fi

echo "✓ Ollama found: $(which ollama)"
echo ""

# Check if Ollama service is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "Starting Ollama service..."
    ollama serve &
    sleep 2
    
    # Wait for service to be ready
    for i in {1..10}; do
        if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
            echo "✓ Ollama service started"
            break
        fi
        sleep 1
    done
else
    echo "✓ Ollama service is running"
fi

echo ""

# Function to pull a model if not already installed
pull_model() {
    local model_name=$1
    local description=$2
    
    echo "Checking for model: $model_name ($description)"
    
    # Check if model exists
    if ollama list | grep -q "$model_name"; then
        echo "  ✓ Already installed"
    else
        echo "  → Installing..."
        ollama pull "$model_name" || {
            echo "  ✗ Failed to install $model_name"
            echo "    Note: Some models may not be available in Ollama's library"
            echo "    You may need to create a custom Modelfile"
            return 1
        }
        echo "  ✓ Installed"
    fi
    echo ""
}

# Install Granite 4.0 models (Phase-7D)
echo "Installing Granite 4.0 models..."
echo ""
echo "Phase-7D: Granite 4.0 models are available in Ollama!"
echo ""

# Granite 4.0 chat models
pull_model "ibm/granite4.0-preview:tiny" "Granite 4.0 H Tiny (Local Agent)"
pull_model "ibm/granite4.0-preview:micro" "Granite 4.0 H Micro (Smaller alternative)"
pull_model "ibm/granite4.0-preview:small" "Granite 4.0 H Small (Larger alternative)"

# Granite embedding models
pull_model "ibm/granite-embedding:30m" "Granite Embedding 30M (English-only)"
pull_model "ibm/granite-embedding:278m" "Granite Embedding 278M (Multilingual + Reranker)"

# Install other required models
echo "Installing other required models..."
pull_model "qwen2.5:14b" "Theology Model (alternative)"
pull_model "qwen2.5:8b" "Local Agent Model (alternative)"

echo ""
echo "Installed models:"
ollama list

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .env: INFERENCE_PROVIDER=ollama"
echo "2. Update .env: OLLAMA_ENABLED=1"
echo "3. Update .env: OPENAI_BASE_URL=http://localhost:11434/v1"
echo "4. Update model names in .env (use canonical names, adapter will map to Ollama):"
echo "   - LOCAL_AGENT_MODEL=granite-4.0-h-tiny"
echo "   - EMBEDDING_MODEL=granite-embedding-english-r2"
echo "   - RERANKER_MODEL=granite-embedding-reranker-english-r2"
echo "5. Test: python -c 'from pmagent.adapters.ollama import ollama_health_check; print(ollama_health_check())'"
echo ""

