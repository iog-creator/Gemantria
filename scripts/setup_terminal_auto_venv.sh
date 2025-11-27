#!/bin/bash
# Setup script to configure terminal auto-activation of venv
# This prevents the "yellow" duplicate venv indicator issue

set -euo pipefail

SHELL_RC=""
if [ -n "${ZSH_VERSION:-}" ]; then
  SHELL_RC="$HOME/.zshrc"
elif [ -n "${BASH_VERSION:-}" ]; then
  SHELL_RC="$HOME/.bashrc"
else
  echo "❌ Unsupported shell. Please manually add to your shell config."
  exit 1
fi

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
AUTO_ACTIVATE_SCRIPT="$REPO_ROOT/scripts/auto_activate_venv.sh"

# Check if already configured
if grep -q "auto_activate_venv.sh" "$SHELL_RC" 2>/dev/null; then
  echo "✅ Auto-activation already configured in $SHELL_RC"
  echo "   To re-configure, remove the line and run this script again"
  exit 0
fi

# Add to shell config
echo "" >> "$SHELL_RC"
echo "# Gemantria: Auto-activate venv when in project directory" >> "$SHELL_RC"
echo "source '$AUTO_ACTIVATE_SCRIPT'" >> "$SHELL_RC"

echo "✅ Auto-activation configured!"
echo ""
echo "   Added to: $SHELL_RC"
echo "   Script: $AUTO_ACTIVATE_SCRIPT"
echo ""
echo "   To activate:"
echo "   1. Restart your terminal, OR"
echo "   2. Run: source $SHELL_RC"
echo ""
echo "   The venv will now auto-activate when you cd into the project directory"
echo "   and won't duplicate the prompt indicator."

