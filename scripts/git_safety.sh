#!/bin/bash

# Git Safety Script - Prevents destructive operations
# Include this in all git operations to ensure safety

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Log function
log() {
    echo -e "${GREEN}[GIT SAFETY]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[GIT SAFETY WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[GIT SAFETY ERROR]${NC} $1"
}

# Banned commands that cause data loss
BANNED_COMMANDS=(
    "reset --hard"
    "rebase"
    "pull --rebase"
    "pull --force"
    "push --force"
    "push --force-with-lease"
    "clean -fd"
    "clean -f"
)

# Function to check if command is banned
is_command_banned() {
    local cmd="$1"
    for banned in "${BANNED_COMMANDS[@]}"; do
        if [[ "$cmd" == *"$banned"* ]]; then
            return 0  # True - command is banned
        fi
    done
    return 1  # False - command is safe
}

# Function to create backup
create_backup() {
    local timestamp=$(date +%Y%m%d_%H%M%S)

    log "Creating backup before operation..."

    # Create backup branch
    if git branch "backup_$timestamp" 2>/dev/null; then
        log "Created backup branch: backup_$timestamp"
    else
        warn "Could not create backup branch (may already exist)"
    fi

    # Stash any uncommitted changes
    if git diff --quiet && git diff --cached --quiet; then
        log "No uncommitted changes to stash"
    else
        if git stash push -m "backup_$timestamp" 2>/dev/null; then
            log "Stashed uncommitted changes"
        else
            warn "Could not stash changes"
        fi
    fi

    echo "backup_$timestamp"
}

# Function to validate environment
validate_environment() {
    log "Validating environment..."

    # Check if we're in the correct virtual environment
    local python_path=$(which python)
    local expected_path="/home/mccoy/Projects/Gemantria.v2/.venv/bin/python"

    if [[ "$python_path" != "$expected_path" ]]; then
        error "INCORRECT VIRTUAL ENVIRONMENT!"
        error "Expected: $expected_path"
        error "Current:  $python_path"
        error "Run: source activate_venv.sh"
        exit 1
    fi

    log "Virtual environment validated: $python_path"
}

# Function to show recovery options
show_recovery_options() {
    local backup_branch="$1"

    echo ""
    warn "If something goes wrong, recovery options:"
    echo "1. Restore from backup branch: git checkout $backup_branch"
    echo "2. Restore stashed changes: git stash pop"
    echo "3. Check reflog: git reflog --oneline -10"
    echo "4. List backup branches: git branch | grep backup"
    echo ""
}

# Main safety check function
check_git_safety() {
    local git_command="$1"

    log "Checking git command safety: $git_command"

    # Validate environment first
    validate_environment

    # Check if command is banned
    if is_command_banned "$git_command"; then
        error "🚨 DANGEROUS COMMAND BLOCKED 🚨"
        error "Command: git $git_command"
        error "This command can cause irreversible data loss!"
        echo ""
        error "BLOCKED COMMANDS:"
        for cmd in "${BANNED_COMMANDS[@]}"; do
            echo "  - git $cmd"
        done
        echo ""
        warn "SAFE ALTERNATIVES:"
        echo "  - git fetch origin (then merge manually)"
        echo "  - git pull --ff-only (safe fast-forward only)"
        echo "  - git push (normal push)"
        echo "  - gh pr merge --squash (for PR operations)"
        echo ""
        error "Operation ABORTED for safety"
        exit 1
    fi

    # Create backup for any git operation
    local backup_branch=$(create_backup)

    # Show recovery options
    show_recovery_options "$backup_branch"

    log "Command approved: git $git_command"
}

# If script is called directly with arguments, check those arguments
if [[ $# -gt 0 ]]; then
    check_git_safety "$*"
fi


