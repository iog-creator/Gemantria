# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
"""
ai_integration_example.py — Example integration of AI learning tracking.

This script demonstrates how to integrate AI learning tracking into
development workflows. It shows how to:

1. Start/end AI sessions
2. Track tool usage
3. Log code generation
4. Capture user feedback
5. Monitor performance

Usage:
    python scripts/ai_integration_example.py demo
"""

import sys
import time
from pathlib import Path

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from ai_session_monitor import AISessionMonitor


def demo_ai_integration():
    """Demonstrate AI learning integration workflow."""
    print("🎯 AI LEARNING INTEGRATION DEMO")
    print("=" * 50)

    monitor = AISessionMonitor()

    # 1. Start a development session
    session_id = f"demo_session_{int(time.time())}"
    print(f"1. Starting AI session: {session_id}")

    initial_context = {
        "project": "Gemantria",
        "task": "Database schema design",
        "files_open": ["migrations/", "scripts/"],
        "tools_available": ["search_replace", "run_terminal_cmd", "grep", "read_file"],
    }

    monitor.start_session(session_id, initial_context)

    # 2. Simulate some tool usage
    print("\n2. Simulating tool interactions...")

    # Successful tool usage
    monitor.log_tool_usage("grep", success=True, execution_time_ms=150)
    monitor.log_tool_usage("read_file", success=True, execution_time_ms=200)

    # Failed tool usage
    monitor.log_tool_usage("run_terminal_cmd", success=False, execution_time_ms=500, error_details="command not found")

    # 3. Log a user query interaction
    print("\n3. Logging user query interaction...")
    monitor.log_user_query(
        query="How can I improve the database schema for AI learning tracking?",
        response="I'll help you design a comprehensive schema for tracking AI interactions and learning patterns.",
        tools_used=["read_file", "grep"],
        execution_time_ms=2500,
    )

    # 4. Log code generation
    print("\n4. Logging code generation...")
    sample_migration = """
-- Migration for AI learning tracking
CREATE TABLE ai_interactions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    interaction_type VARCHAR(50) NOT NULL
);
"""
    monitor.log_code_generation(
        file_path="migrations/016_create_ai_learning_tracking.sql",
        generation_type="migration",
        code_content=sample_migration,
        context={"purpose": "AI learning analytics", "complexity": "high"},
    )

    # 5. Capture context snapshot
    print("\n5. Capturing development context...")
    context = monitor.capture_context_snapshot()
    print(f"   Captured {len(context) if context else 0} context data points")

    # 6. Log a learning event
    print("\n6. Logging AI learning event...")
    monitor.log_learning_event(
        learning_type="pattern_recognition",
        trigger={"event": "repeated_tool_failures", "tool": "run_terminal_cmd"},
        outcome="Identified need for better error handling in terminal commands",
        confidence=0.85,
    )

    # 7. Get session summary
    print("\n7. Session summary:")
    summary = monitor.get_session_summary()
    print(f"   Duration: {summary['duration_seconds']:.1f} seconds")
    print(f"   Interactions: {len(summary['interactions'])} types")
    print(f"   Tools used: {summary['tools_used']}")

    # 8. End session with feedback
    print("\n8. Ending session with user feedback...")
    monitor.end_session(
        feedback_rating=5,
        feedback_text="Excellent AI assistance with comprehensive tracking",
        tags=["database_design", "ai_integration", "performance_monitoring"],
    )

    print("\n✅ AI Learning Integration Demo Complete!")
    print("\n📊 View results with:")
    print("   make ai.analytics          # Full analytics dashboard")
    print("   make ai.learning.export    # Export learning data")
    print("   python scripts/ai_analytics_dashboard.py insights  # Actionable insights")


def show_integration_patterns():
    """Show common integration patterns."""
    print("🔧 AI LEARNING INTEGRATION PATTERNS")
    print("=" * 50)

    patterns = [
        {
            "pattern": "Session Management",
            "code": """
# Start session at beginning of AI-assisted work
monitor.start_session(session_id, initial_context)

# End session with user feedback
monitor.end_session(feedback_rating, feedback_text, tags)
            """,
            "use_case": "Track complete AI-assisted development sessions",
        },
        {
            "pattern": "Tool Usage Tracking",
            "code": """
# After each tool call
monitor.log_tool_usage(tool_name, success, execution_time, error_details)
            """,
            "use_case": "Monitor tool effectiveness and identify improvement areas",
        },
        {
            "pattern": "Code Generation Logging",
            "code": """
# After generating code
monitor.log_code_generation(file_path, gen_type, code_content, context)
            """,
            "use_case": "Track code generation patterns and acceptance rates",
        },
        {
            "pattern": "Learning Event Capture",
            "code": """
# When AI learns something new
monitor.log_learning_event(learning_type, trigger, outcome, confidence)
            """,
            "use_case": "Capture AI learning moments for continuous improvement",
        },
        {
            "pattern": "Context Awareness",
            "code": """
# Periodically capture development context
context = monitor.capture_context_snapshot()
            """,
            "use_case": "Understand what context leads to successful outcomes",
        },
    ]

    for i, pattern in enumerate(patterns, 1):
        print(f"{i}. {pattern['pattern']}")
        print(f"   Use Case: {pattern['use_case']}")
        print("   Code:")
        print(f"   {pattern['code'].strip()}")
        print()


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/ai_integration_example.py {demo|patterns}")
        sys.exit(1)

    command = sys.argv[1]

    if command == "demo":
        demo_ai_integration()
    elif command == "patterns":
        show_integration_patterns()
    else:
        print(f"Unknown command: {command}")
        print("Available commands: demo, patterns")


if __name__ == "__main__":
    main()
