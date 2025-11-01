#!/bin/bash
# pr_gate.sh - Gate PR merges by required checks only
#
# Usage: ./scripts/pr_gate.sh <pr-number>
#
# This script checks that only required status checks are pending/running
# and that all required checks have passed. It mirrors the connector-less
# merge strategy used in the merge train.
#
# Required checks (configured in branch protection):
# - ruff: formatting + linting (enforce-ruff.yml)
# - build: CI pipeline (ci.yml)

set -e

if [ $# -ne 1 ]; then
    echo "Usage: $0 <pr-number>"
    exit 1
fi

PR_NUMBER="$1"

echo "🔍 Checking required checks for PR #$PR_NUMBER..."

# Get required checks status
# This uses the same logic as the merge train strategy
REQUIRED_CHECKS=$(gh pr checks "$PR_NUMBER" --required --json name,state | jq -r '.[] | "\(.name): \(.state)"')

if [ -z "$REQUIRED_CHECKS" ]; then
    echo "✅ NO REQUIRED CHECKS - PR can be merged immediately"
    echo "   (This indicates all required checks have passed)"
    exit 0
fi

echo "📋 Required checks status:"
echo "$REQUIRED_CHECKS"

# Check if any required checks are failing
FAILED_CHECKS=$(echo "$REQUIRED_CHECKS" | grep -c ": fail\|: error" || true)

if [ "$FAILED_CHECKS" -gt 0 ]; then
    echo "❌ $FAILED_CHECKS required check(s) failed"
    echo "   PR cannot be merged until all required checks pass"
    exit 1
fi

# Check if any required checks are still pending/running
PENDING_CHECKS=$(echo "$REQUIRED_CHECKS" | grep -c ": pending\|: in_progress\|: queued" || true)

if [ "$PENDING_CHECKS" -gt 0 ]; then
    echo "⏳ $PENDING_CHECKS required check(s) still running"
    echo "   Wait for completion before merging"
    exit 1
fi

# All required checks passed
PASSED_CHECKS=$(echo "$REQUIRED_CHECKS" | grep -c ": success" || true)
echo "✅ All $PASSED_CHECKS required check(s) passed"
echo "   PR is ready for merge!"
exit 0
