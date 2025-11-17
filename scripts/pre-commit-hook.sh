#!/bin/bash

# Git Safety Pre-commit Hook
# Prevents destructive git operations that could cause data loss
# Install by copying to .git/hooks/pre-commit and making executable

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

# Check if this is a dangerous operation by examining the command that triggered this hook
# Git doesn't directly pass the command, so we check environment and recent operations

# Check for dangerous git operations in recent history (last command)
if [[ "$GIT_COMMAND" == *"reset --hard"* ]] || \
   [[ "$GIT_COMMAND" == *"rebase"* ]] || \
   [[ "$GIT_COMMAND" == *"pull --rebase"* ]] || \
   [[ "$GIT_COMMAND" == *"pull --force"* ]] || \
   [[ "$GIT_COMMAND" == *"push --force"* ]] || \
   [[ "$GIT_COMMAND" == *"clean -fd"* ]]; then

    echo -e "${RED}🚨 DANGEROUS GIT OPERATION BLOCKED 🚨${NC}"
    echo -e "${RED}Command contains: $GIT_COMMAND${NC}"
    echo ""
    echo -e "${YELLOW}This operation can cause irreversible data loss!${NC}"
    echo ""
    echo -e "${YELLOW}BLOCKED OPERATIONS:${NC}"
    echo "  - git reset --hard (destroys commits)"
    echo "  - git rebase (rewrites history)"
    echo "  - git pull --rebase (dangerous rebase)"
    echo "  - git pull --force (overwrites local)"
    echo "  - git push --force (overwrites remote)"
    echo "  - git clean -fd (deletes files)"
    echo ""
    echo -e "${YELLOW}SAFE ALTERNATIVES:${NC}"
    echo "  - git fetch origin (safe fetch)"
    echo "  - git merge (normal merge)"
    echo "  - git pull --ff-only (fast-forward only)"
    echo "  - git push (normal push)"
    echo "  - gh pr merge --squash (PR operations)"
    echo ""
    echo -e "${RED}OPERATION BLOCKED - NO COMMITS PROCESSED${NC}"
    exit 1
fi

# Check virtual environment
PYTHON_PATH=$(which python 2>/dev/null)
EXPECTED_PATH="/home/mccoy/Projects/Gemantria.v2/.venv/bin/python"

if [[ "$PYTHON_PATH" != "$EXPECTED_PATH" ]]; then
    echo -e "${RED}🚨 INCORRECT VIRTUAL ENVIRONMENT 🚨${NC}"
    echo -e "${RED}Expected: $EXPECTED_PATH${NC}"
    echo -e "${RED}Current:  $PYTHON_PATH${NC}"
    echo ""
    echo -e "${YELLOW}Run: source activate_venv.sh${NC}"
    echo ""
    echo -e "${RED}COMMIT BLOCKED - FIX ENVIRONMENT FIRST${NC}"
    exit 1
fi

# All checks passed
echo -e "${GREEN}✅ Git safety checks passed${NC}"
exit 0













