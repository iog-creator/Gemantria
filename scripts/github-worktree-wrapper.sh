#!/bin/bash

# GitHub Worktree Wrapper
# Automatically handles GitHub CLI operations from worktrees by switching to main repo

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in a worktree
is_worktree() {
    git rev-parse --is-inside-work-tree &> /dev/null && [ -f ".git" ] && grep -q "gitdir:" .git
}

# Get main repo path
get_main_repo() {
    git rev-parse --git-dir | sed 's/\.git\/worktrees\/.*//' | sed 's/\/\.git$//'
}

# Get current branch
get_current_branch() {
    git branch --show-current 2>/dev/null || echo "unknown"
}

# Main function
main() {
    if ! is_worktree; then
        print_status "Not in a worktree, proceeding normally..."
        exec "$@"
        return
    fi

    MAIN_REPO=$(get_main_repo)
    CURRENT_BRANCH=$(get_current_branch)
    CURRENT_DIR=$(pwd)

    print_warning "Detected worktree usage at: $CURRENT_DIR"
    print_warning "Switching to main repo for GitHub CLI operations: $MAIN_REPO"

    # Change to main repo and execute command
    cd "$MAIN_REPO"

    # If we're on a branch that's checked out in worktree, we need to reference the remote branch
    if git branch --list "$CURRENT_BRANCH" | grep -q "$CURRENT_BRANCH"; then
        print_status "Branch $CURRENT_BRANCH exists locally, using it..."
    else
        print_status "Branch $CURRENT_BRANCH not local, will reference remote branch..."
        # For PR operations, we'll need to specify the head branch
        if [[ "$1" == "pr" && "$2" == "create" ]]; then
            set -- "$@" --head "$CURRENT_BRANCH"
        fi
    fi

    print_status "Executing: gh $@"
    exec gh "$@"
}

# Show usage if no arguments
if [ $# -eq 0 ]; then
    echo "GitHub Worktree Wrapper"
    echo "Usage: $0 <gh command args...>"
    echo ""
    echo "Automatically handles GitHub CLI operations from worktrees"
    echo "by switching to the main repository directory."
    echo ""
    echo "Examples:"
    echo "  $0 pr create --title 'My PR'"
    echo "  $0 pr list"
    echo "  $0 issue list"
    exit 1
fi

main "$@"
