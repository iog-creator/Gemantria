#!/bin/bash
# PMS (Project Management System) Deployment Script
# Deploys the complete PMS system in any project

set -e  # Exit on any error

echo "🏗️  Project Management System (PMS) Deployment"
echo "=============================================="

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Error: Must be run from a git repository"
    exit 1
fi

# Check if PROJECT_MASTER_PLAN.md exists
if [ ! -f "PROJECT_MASTER_PLAN.md" ]; then
    echo "❌ Error: PROJECT_MASTER_PLAN.md not found"
    echo "Please create your project master plan first."
    exit 1
fi

echo "📋 Found project master plan: PROJECT_MASTER_PLAN.md"

# Create scripts directory if it doesn't exist
mkdir -p scripts

# Copy PMS core scripts (assuming we're deploying from the source project)
PMS_SCRIPTS=(
    "enforce_metadata.py"
    "create_agents_md.py"
    "rules_audit.py"
    "envelope_processor.py"
    "pms_init.py"
)

echo "🔧 Deploying PMS scripts..."
for script in "${PMS_SCRIPTS[@]}"; do
    if [ -f "scripts/$script" ]; then
        echo "✅ Script already exists: $script"
    else
        # Try to copy from current directory (deployment scenario)
        if [ -f "$script" ]; then
            cp "$script" "scripts/"
            chmod +x "scripts/$script"
            echo "📄 Copied: $script"
        else
            echo "⚠️  Script not found: $script (will be created by pms-init)"
        fi
    fi
done

# Deploy the PMS spec
if [ ! -f "PROJECT_MANAGEMENT_SYSTEM_SPEC.md" ]; then
    echo "📋 Deploying PMS specification..."
    # This would be copied from the deployment package
    echo "⚠️  PMS spec not found - will be created by pms-init"
fi

# Initialize PMS
echo "🚀 Initializing PMS..."
if [ -f "scripts/pms_init.py" ]; then
    python3 scripts/pms_init.py --init
else
    echo "❌ Error: pms_init.py not found"
    exit 1
fi

# Run initial housekeeping
echo "🧹 Running initial housekeeping..."
if [ -f "Makefile" ]; then
    make housekeeping
else
    echo "⚠️  Makefile not found - running individual commands..."

    # Run individual housekeeping commands
    if [ -f "scripts/rules_audit.py" ]; then
        python3 scripts/rules_audit.py
    fi

    if [ -f "scripts/enforce_metadata.py" ]; then
        python3 scripts/enforce_metadata.py --staged --fix
    fi

    if [ -f "scripts/envelope_processor.py" ]; then
        python3 scripts/envelope_processor.py --process-pending
    fi
fi

echo ""
echo "✅ PMS Deployment Complete!"
echo ""
echo "🎯 What PMS Provides:"
echo "  • Hints envelopes with imperative commands"
echo "  • AGENTS.md plural with Related ADRs tables"
echo "  • .mdc rules for Cursor workspace governance"
echo "  • Automated housekeeping and metadata enforcement"
echo "  • Envelope processing with critical failure handling"
echo ""
echo "📋 Daily Workflow:"
echo "  1. make housekeeping    # After any changes"
echo "  2. make metadata-check  # Verify metadata compliance"
echo "  3. make envelope-process # Process hints envelopes"
echo ""
echo "🔗 Key Files:"
echo "  • PROJECT_MASTER_PLAN.md - Your project requirements (SSOT)"
echo "  • AGENTS.md - Main project documentation"
echo "  • .cursor/rules/ - Cursor workspace rules"
echo "  • scripts/ - PMS automation scripts"
echo ""
echo "🛡️  Governance:"
echo "  • Master plan overrides all other guidance"
echo "  • Envelope errors block execution"
echo "  • Makefile targets only (no inventing commands)"
echo "  • Auto-housekeeping prevents drift"
