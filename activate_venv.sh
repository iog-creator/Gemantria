#!/bin/bash
# Auto-activate Gemantria virtual environment and validate environment

# Function to check if venv is active
is_venv_active() {
    [ -n "$VIRTUAL_ENV" ] && [[ "$VIRTUAL_ENV" == *".venv" ]] && [ -f "$VIRTUAL_ENV/bin/python3" ]
}

# Function to validate environment
validate_environment() {
    echo "🔧 Validating Gemantria environment..."

    # Check if we're in venv
    if ! is_venv_active; then
        echo "❌ ERROR: Virtual environment not active!"
        echo "   Run: source .venv/bin/activate"
        return 1
    fi

    # Check .env file exists
    if [ ! -f ".env" ]; then
        echo "❌ ERROR: .env file not found!"
        echo "   Copy from: cp env_example.txt .env"
        return 1
    fi

    # Check if DSN is configured
    if ! grep -q "^GEMATRIA_DSN=" .env; then
        echo "❌ ERROR: GEMATRIA_DSN not configured in .env!"
        return 1
    fi

    # Try to load environment
    if command -v python3 >/dev/null 2>&1; then
        if python3 -c "import os; os.chdir('.'); from src.infra.env_loader import ensure_env_loaded; ensure_env_loaded(); print('✅ Environment loaded successfully')"; then
            echo "✅ Environment validation complete"
            return 0
        else
            echo "❌ ERROR: Failed to load environment configuration"
            return 1
        fi
    else
        echo "⚠️  WARNING: python3 not found in PATH"
        return 1
    fi
}

# Main logic
if ! is_venv_active; then
    echo "🔧 Activating Gemantria virtual environment..."
    source .venv/bin/activate
    echo "✅ Virtual environment active: $VIRTUAL_ENV"
fi

# Validate environment
if validate_environment; then
    echo "🎉 Environment ready for Gemantria operations!"
else
    echo "💥 Environment validation failed!"
    echo "   Please fix the issues above before proceeding."
    exit 1
fi
