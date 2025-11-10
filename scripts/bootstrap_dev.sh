#!/usr/bin/env bash
set -euo pipefail

echo "🔧 Bootstrapping Gemantria development environment..."

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install --upgrade "psycopg[binary]" pgvector requests python-dotenv

# Environment setup
cp -n env_example.txt .env
set -a && source .env && set +a

# Database setup
sudo systemctl start postgresql 2>/dev/null || echo "PostgreSQL may already be running"
psql "$GEMATRIA_DSN" -c "CREATE EXTENSION IF NOT EXISTS vector;" 2>/dev/null || echo "Vector extension may already exist"

# LM Studio probe
echo "🌐 Probing LM Studio..."
if curl -s "$LM_STUDIO_HOST/v1/models" >/dev/null 2>&1; then
    echo "✅ LM Studio API available"
else
    echo "⚠️  LM Studio API not available (server may not be running)"
fi

# Final verification
echo "🔍 Running doctor diagnostic..."
python3 scripts/doctor.py

echo "🎉 Bootstrap complete! Run 'make doctor' anytime to verify environment."
