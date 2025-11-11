from scripts.config.env import get_rw_dsn

# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
"""
ai_session_monitor.py — Automatic AI session monitoring and learning integration.

Monitors AI interactions during development sessions and automatically logs
learning data for continuous improvement. Integrates with existing workflows.

Features:
- Automatic session tracking
- Tool usage monitoring
- Code generation outcome tracking
- Context awareness logging
- Performance metrics collection

Usage:
    python scripts/ai_session_monitor.py start_session --id <session_id>
    python scripts/ai_session_monitor.py log_tool_usage --tool <name> --success <bool> --time <ms>
    python scripts/ai_session_monitor.py log_code_generation --file <path> --type <type>
    python scripts/ai_session_monitor.py end_session --feedback <rating>
"""

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Import our AI learning tracker
sys.path.insert(0, str(Path(__file__).parent))
from ai_learning_tracker import AILearningTracker

# Database connection
GEMATRIA_DSN = get_rw_dsn()
ROOT = Path(__file__).resolve().parent.parent


class AISessionMonitor:
    """Automatic AI session monitoring and learning integration."""

    def __init__(self):
        self.tracker = AILearningTracker()
        self.current_session = None
        self.session_start_time = None

    def start_session(self, session_id: str, context: Dict[str, Any] | None = None):
        """Start monitoring an AI development session."""
        self.current_session = session_id
        self.session_start_time = time.time()

        # Log session start
        self.tracker.log_interaction(
            session_id=session_id,
            interaction_type="session_start",
            context={
                "session_type": "development",
                "start_time": datetime.now().isoformat(),
                "context": context or {},
            },
        )

        print(f"🎯 Started AI session monitoring: {session_id}")

        # Log initial context awareness
        if context:
            self.tracker.log_context_awareness(
                session_id=session_id,
                context_type="session_start",
                context_data=context,
                relevance_score=1.0,
            )

    def log_tool_usage(
        self,
        tool_name: str,
        success: bool,
        execution_time_ms: int | None = None,
        error_details: str | None = None,
    ):
        """Log tool usage during the session."""
        if not self.current_session:
            print("⚠️  No active session - tool usage not logged")
            return

        # Log the tool interaction
        self.tracker.log_interaction(
            session_id=self.current_session,
            interaction_type="tool_call",
            tools_used=[tool_name],
            execution_time_ms=execution_time_ms,
            success=success,
            error_details=error_details,
        )

        print(f"🔧 Logged tool usage: {tool_name} ({'✅' if success else '❌'})")

    def log_code_generation(
        self,
        file_path: str,
        generation_type: str,
        code_content: str | None = None,
        context: Dict[str, Any] | None = None,
    ):
        """Log code generation event."""
        if not self.current_session:
            print("⚠️  No active session - code generation not logged")
            return

        # Calculate complexity score (simple line count for now)
        complexity_score = len(code_content.split("\n")) if code_content else 0

        # Log code generation
        self.tracker.log_code_generation(
            session_id=self.current_session,
            generation_type=generation_type,
            target_file=file_path,
            generated_code=code_content,
            complexity_score=complexity_score,
            context=context,
        )

        print(f"💻 Logged code generation: {generation_type} → {file_path}")

    def log_user_query(
        self,
        query: str,
        response: str | None = None,
        tools_used: List[str] | None = None,
        execution_time_ms: int | None = None,
    ):
        """Log a user query and AI response."""
        if not self.current_session:
            print("⚠️  No active session - user query not logged")
            return

        self.tracker.log_interaction(
            session_id=self.current_session,
            interaction_type="user_query",
            user_query=query,
            ai_response=response,
            tools_used=tools_used,
            execution_time_ms=execution_time_ms,
        )

        print("💬 Logged user query interaction")

    def capture_context_snapshot(self):
        """Capture current development context snapshot."""
        if not self.current_session:
            return

        context = {}

        # Get git status
        try:
            result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, cwd=ROOT)
            context["git_status"] = result.stdout.strip()
        except Exception:
            context["git_status"] = "unknown"

        # Get current branch
        try:
            result = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True, cwd=ROOT)
            context["git_branch"] = result.stdout.strip()
        except Exception:
            context["git_branch"] = "unknown"

        # Get recent files (last 10 modified)
        try:
            result = subprocess.run(
                [
                    "find",
                    ".",
                    "-name",
                    "*.py",
                    "-o",
                    "-name",
                    "*.sql",
                    "-o",
                    "-name",
                    "*.md",
                    "-o",
                    "-name",
                    "Makefile",
                    "|",
                    "xargs",
                    "ls",
                    "-t",
                    "|",
                    "head",
                    "-10",
                ],
                capture_output=True,
                text=True,
                cwd=ROOT,
            )
            context["recent_files"] = result.stdout.strip().split("\n")
        except Exception:
            context["recent_files"] = []

        # Log context awareness
        self.tracker.log_context_awareness(
            session_id=self.current_session,
            context_type="context_snapshot",
            context_data=context,
            relevance_score=0.8,
        )

        return context

    def log_learning_event(self, learning_type: str, trigger: Dict, outcome: str, confidence: float):
        """Log an AI learning event."""
        if not self.current_session:
            print("⚠️  No active session - learning event not logged")
            return

        self.tracker.log_learning_event(
            learning_type=learning_type,
            trigger_event=trigger,
            learning_outcome=outcome,
            confidence_score=confidence,
        )

        print(f"🧠 Logged learning event: {learning_type}")

    def end_session(
        self,
        feedback_rating: int | None = None,
        feedback_text: str | None = None,
        tags: List[str] | None = None,
    ):
        """End the monitoring session."""
        if not self.current_session:
            print("⚠️  No active session to end")
            return

        session_duration = time.time() - self.session_start_time

        # Log session end
        self.tracker.log_interaction(
            session_id=self.current_session,
            interaction_type="session_end",
            context={"duration_seconds": session_duration, "end_time": datetime.now().isoformat()},
        )

        # Log user feedback if provided
        if feedback_rating:
            self.tracker.log_user_feedback(
                session_id=self.current_session,
                feedback_type="session_satisfaction",
                rating=feedback_rating,
                feedback_text=feedback_text,
                tags=tags or ["development_session"],
            )

        # Run pattern analysis
        self.tracker.analyze_patterns()

        print(f"Session ended. Duration: {session_duration / 60:.1f} minutes")
        self.current_session = None
        self.session_start_time = None

    def get_session_summary(self):
        """Get summary of current session."""
        if not self.current_session:
            return {"status": "no_active_session"}

        duration = time.time() - self.session_start_time

        # Query session stats from database
        with self.tracker.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT interaction_type, COUNT(*) as count,
                           AVG(execution_time_ms) as avg_time
                    FROM ai_interactions
                    WHERE session_id = %s
                    GROUP BY interaction_type
                """,
                    (self.current_session,),
                )

                interactions = {}
                for row in cur.fetchall():
                    interactions[row[0]] = {
                        "count": row[1],
                        "avg_time": float(row[2]) if row[2] else 0,
                    }

                cur.execute(
                    """
                    SELECT COUNT(*) as tools_used
                    FROM ai_interactions
                    WHERE session_id = %s AND tools_used IS NOT NULL
                """,
                    (self.current_session,),
                )

                tools_count = cur.fetchone()[0]

        return {
            "session_id": self.current_session,
            "duration_seconds": duration,
            "interactions": interactions,
            "tools_used": tools_count,
            "status": "active",
        }


def main():
    parser = argparse.ArgumentParser(description="AI Session Monitor")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Start session
    start_parser = subparsers.add_parser("start_session", help="Start session monitoring")
    start_parser.add_argument("--id", required=True, help="Session ID")
    start_parser.add_argument("--context", type=json.loads, help="Initial context JSON")

    # Tool usage
    tool_parser = subparsers.add_parser("log_tool_usage", help="Log tool usage")
    tool_parser.add_argument("--tool", required=True, help="Tool name")
    tool_parser.add_argument("--success", type=bool, default=True, help="Success status")
    tool_parser.add_argument("--time", type=int, help="Execution time in ms")
    tool_parser.add_argument("--error", help="Error details")

    # Code generation
    code_parser = subparsers.add_parser("log_code_generation", help="Log code generation")
    code_parser.add_argument("--file", required=True, help="Target file path")
    code_parser.add_argument("--type", required=True, help="Generation type")
    code_parser.add_argument("--code", help="Generated code content")
    code_parser.add_argument("--context", type=json.loads, help="Generation context")

    # User query
    query_parser = subparsers.add_parser("log_user_query", help="Log user query")
    query_parser.add_argument("--query", required=True, help="User query")
    query_parser.add_argument("--response", help="AI response")
    query_parser.add_argument("--tools", nargs="*", help="Tools used")
    query_parser.add_argument("--time", type=int, help="Execution time in ms")

    # Learning event
    learn_parser = subparsers.add_parser("log_learning", help="Log learning event")
    learn_parser.add_argument("--type", required=True, help="Learning type")
    learn_parser.add_argument("--trigger", type=json.loads, required=True, help="Trigger event JSON")
    learn_parser.add_argument("--outcome", required=True, help="Learning outcome")
    learn_parser.add_argument("--confidence", type=float, required=True, help="Confidence score")

    # Context snapshot
    subparsers.add_parser("capture_context", help="Capture context snapshot")

    # Session summary
    subparsers.add_parser("get_summary", help="Get session summary")

    # End session
    end_parser = subparsers.add_parser("end_session", help="End session monitoring")
    end_parser.add_argument("--feedback", type=int, choices=range(1, 6), help="Session satisfaction 1-5")
    end_parser.add_parser("--text", help="Feedback text")
    end_parser.add_argument("--tags", nargs="*", help="Feedback tags")

    args = parser.parse_args()

    monitor = AISessionMonitor()

    try:
        if args.command == "start_session":
            monitor.start_session(args.id, args.context)

        elif args.command == "log_tool_usage":
            monitor.log_tool_usage(args.tool, args.success, args.time, args.error)

        elif args.command == "log_code_generation":
            monitor.log_code_generation(args.file, args.type, args.code, args.context)

        elif args.command == "log_user_query":
            monitor.log_user_query(args.query, args.response, args.tools, args.time)

        elif args.command == "log_learning":
            monitor.log_learning(args.type, args.trigger, args.outcome, args.confidence)

        elif args.command == "capture_context":
            context = monitor.capture_context_snapshot()
            print(f"📸 Captured context snapshot with {len(context) if context else 0} data points")

        elif args.command == "get_summary":
            summary = monitor.get_session_summary()
            print(json.dumps(summary, indent=2))

        elif args.command == "end_session":
            monitor.end_session(args.feedback, getattr(args, "text", None), args.tags)

        else:
            parser.print_help()

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
