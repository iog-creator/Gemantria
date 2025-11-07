#!/usr/bin/env bash

set -euo pipefail

# Backup and protect .env file
# This script creates backups and prevents accidental overwrites

ENV_FILE=".env"
BACKUP_DIR="backups/env"
BACKUP_FILE="$BACKUP_DIR/.env.$(date +%Y%m%d_%H%M%S).backup"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Check if .env exists
if [ ! -f "$ENV_FILE" ]; then
    echo "ERROR: $ENV_FILE does not exist"
    exit 1
fi

# Create backup with timestamp
cp "$ENV_FILE" "$BACKUP_FILE"
echo "✅ Environment file backed up to: $BACKUP_FILE"

# Create a protection marker
echo "# PROTECTED - Do not modify manually. Use scripts/env/edit_env.sh" > ".env.protected"
echo "# Last backup: $(date)" >> ".env.protected"
echo "# Backup file: $BACKUP_FILE" >> ".env.protected"

echo "✅ Environment protection marker created"
echo "📁 Latest backups in: $BACKUP_DIR/"
ls -la "$BACKUP_DIR"/*.backup 2>/dev/null | tail -5 || echo "No previous backups found"
