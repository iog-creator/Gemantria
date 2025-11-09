#!/bin/bash

# Environment Validation Script
# Ensures correct venv and required environment variables are set

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Log functions
log() {
    echo -e "${GREEN}[ENV VALIDATION]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[ENV WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ENV ERROR]${NC} $1"
}

# Check virtual environment
check_venv() {
    local python_path=$(which python 2>/dev/null)
    local expected_path="/home/mccoy/Projects/Gemantria.v2/.venv/bin/python"

    if [[ "$python_path" != "$expected_path" ]]; then
        error "INCORRECT VIRTUAL ENVIRONMENT!"
        error "Expected: $expected_path"
        error "Current:  $python_path"
        error ""
        error "SOLUTION: Run 'source activate_venv.sh'"
        error "Then re-run your command"
        return 1
    fi

    log "Virtual environment validated: $python_path"
    return 0
}

# Check LM Studio configuration
check_lm_studio() {
    # Check required environment variables
    local required_vars=("LM_STUDIO_HOST" "THEOLOGY_MODEL" "EMBEDDING_MODEL" "RERANKER_MODEL")
    local missing_vars=()

    for var in "${required_vars[@]}"; do
        if [[ -z "${!var}" ]]; then
            missing_vars+=("$var")
        fi
    done

    if [[ ${#missing_vars[@]} -gt 0 ]]; then
        warn "LM Studio environment variables not set:"
        for var in "${missing_vars[@]}"; do
            echo "  - $var"
        done
        warn ""
        warn "RECOMMENDED: Add to your shell profile:"
        warn "  export LM_STUDIO_HOST=\"http://127.0.0.1:9994\""
        warn "  export THEOLOGY_MODEL=\"christian-bible-expert-v2.0-12b\""
        warn "  export EMBEDDING_MODEL=\"text-embedding-bge-m3\""
        warn "  export RERANKER_MODEL=\"qwen.qwen3-reranker-0.6b\""
        warn "  export USE_QWEN_EMBEDDINGS=true"
        warn "  export ENFORCE_QWEN_LIVE=1"
        warn ""
        warn "Or run: source scripts/set_env.sh"
        return 1
    fi

    log "LM Studio environment variables validated"
    return 0
}

# Check database configuration
check_database() {
    local has_bible_db=${BIBLE_DB_DSN:+1}
    local has_gematria_db=${GEMATRIA_DSN:+1}

    if [[ -z "$has_bible_db" ]]; then
        warn "BIBLE_DB_DSN not set - Bible database operations will fail"
        warn "Default: postgresql://postgres@/bible_db?host=/var/run/postgresql"
    else
        log "Bible DB DSN configured"
    fi

    if [[ -z "$has_gematria_db" ]]; then
        warn "GEMATRIA_DSN not set - Gematria database operations will fail"
        warn "Default: postgresql://mccoy@/gematria?host=/var/run/postgresql"
    else
        log "Gematria DB DSN configured"
    fi

    # At least one DB should be configured for most operations
    if [[ -z "$has_bible_db" && -z "$has_gematria_db" ]]; then
        error "No database DSNs configured!"
        error "Set at least BIBLE_DB_DSN or GEMATRIA_DSN"
        return 1
    fi

    return 0
}

# Test LM Studio connectivity (optional, can fail)
test_lm_studio_health() {
    if command -v python &> /dev/null; then
        log "Testing LM Studio health check..."
        if python -c "
from src.services.lmstudio_client import assert_qwen_live
try:
    result = assert_qwen_live(['christian-bible-expert-v2.0-12b'])
    print(f'Health check: {\"PASS\" if result.ok else \"FAIL\"} - {result.reason}')
    exit(0 if result.ok else 1)
except Exception as e:
    print(f'Health check failed: {e}')
    exit(1)
" 2>/dev/null; then
            log "LM Studio health check passed"
            return 0
        else
            warn "LM Studio health check failed - AI operations may not work"
            warn "Ensure LM Studio is running on port 9994 with required models loaded"
            return 1
        fi
    fi

    return 0  # Skip health check if python not available
}

# Main validation
main() {
    log "Starting environment validation..."

    local all_passed=true

    # Check virtual environment (required)
    if ! check_venv; then
        all_passed=false
    fi

    # Check LM Studio config (recommended)
    if ! check_lm_studio; then
        warn "LM Studio configuration incomplete - AI features may not work"
    fi

    # Check database config (recommended)
    if ! check_database; then
        warn "Database configuration incomplete - DB operations may fail"
    fi

    # Test LM Studio health (optional)
    test_lm_studio_health || true  # Don't fail on health check

    if [[ "$all_passed" == "true" ]]; then
        log "✅ Environment validation PASSED"
        return 0
    else
        error "❌ Environment validation FAILED"
        error "Fix the issues above before proceeding"
        return 1
    fi
}

# Run main validation
main "$@"


