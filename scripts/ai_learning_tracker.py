# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
"""
ai_learning_tracker.py — AI learning and interaction tracking system.

Tracks AI interactions, code generation patterns, user feedback, and learning events
to enable continuous improvement and personalization.

Usage:
    python scripts/ai_learning_tracker.py log_interaction --session-id <id> --type <type> [options]
    python scripts/ai_learning_tracker.py log_feedback --session-id <id> --rating <1-5> [options]
    python scripts/ai_learning_tracker.py analyze_patterns
    python scripts/ai_learning_tracker.py generate_insights
    python scripts/ai_learning_tracker.py export_learning_data
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import psycopg

# Database connection
GEMATRIA_DSN = os.environ.get("GEMATRIA_DSN")
if not GEMATRIA_DSN:
    print("ERROR: GEMATRIA_DSN environment variable required")
    exit(1)

ROOT = Path(__file__).resolve().parent.parent


class AILearningTracker:
    """AI learning and interaction tracking system."""

    def __init__(self):
        self.conn = None

    def get_connection(self):
        """Get database connection."""
        if not self.conn:
            self.conn = psycopg.connect(GEMATRIA_DSN)
        return self.conn

    def log_interaction(
        self,
        session_id: str,
        interaction_type: str,
        user_query: str | None = None,
        ai_response: str | None = None,
        tools_used: List[str] | None = None,
        context: Dict | None = None,
        execution_time_ms: int | None = None,
        success: bool = True,
        error_details: str | None = None,
    ):
        """Log an AI interaction event."""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                # Update tool usage analytics if tools were used
                if tools_used:
                    for tool in tools_used:
                        cur.execute(
                            """
                            SELECT update_tool_usage(%s, %s, %s, %s)
                        """,
                            (tool, success, execution_time_ms, error_details.split(":")[0] if error_details else None),
                        )

                # Log the interaction
                cur.execute(
                    """
                    SELECT log_ai_interaction(%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                    (
                        session_id,
                        interaction_type,
                        user_query,
                        ai_response,
                        tools_used,
                        json.dumps(context) if context else None,
                        execution_time_ms,
                        success,
                        error_details,
                    ),
                )

                conn.commit()
                print(f"✅ Logged {interaction_type} interaction for session {session_id}")

    def log_code_generation(
        self,
        session_id: str,
        generation_type: str,
        target_file: str,
        generated_code: str,
        complexity_score: int | None = None,
        context: Dict | None = None,
    ):
        """Log a code generation event."""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO code_generation_events
                    (session_id, generation_type, target_file, generated_code,
                     code_complexity_score, generation_context)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """,
                    (
                        session_id,
                        generation_type,
                        target_file,
                        generated_code,
                        complexity_score,
                        json.dumps(context) if context else None,
                    ),
                )

                conn.commit()
                print(f"✅ Logged {generation_type} code generation for {target_file}")

    def log_user_feedback(
        self,
        session_id: str,
        feedback_type: str,
        rating: int,
        feedback_text: str | None = None,
        suggestions: str | None = None,
        tags: List[str] | None = None,
    ):
        """Log user feedback."""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT log_user_feedback(%s, %s, %s, %s, %s, %s)
                """,
                    (session_id, feedback_type, rating, feedback_text, suggestions, tags),
                )

                # Update daily satisfaction metrics
                cur.execute("SELECT generate_daily_satisfaction_metrics()")

                conn.commit()
                print(f"✅ Logged {rating}/5 {feedback_type} feedback for session {session_id}")

    def log_context_awareness(
        self, session_id: str, context_type: str, context_data: Dict, relevance_score: float | None = None
    ):
        """Log context awareness event."""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO context_awareness_events
                    (session_id, context_type, context_data, relevance_score)
                    VALUES (%s, %s, %s, %s)
                """,
                    (session_id, context_type, json.dumps(context_data), relevance_score),
                )

                conn.commit()
                print(f"✅ Logged {context_type} context awareness event")

    def log_learning_event(
        self,
        learning_type: str,
        trigger_event: Dict,
        learning_outcome: str,
        confidence_score: float,
        applied_successfully: bool | None = None,
        improvement_metrics: Dict | None = None,
    ):
        """Log an AI learning event."""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO learning_events
                    (learning_type, trigger_event, learning_outcome,
                     confidence_score, applied_successfully, improvement_metrics)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """,
                    (
                        learning_type,
                        json.dumps(trigger_event),
                        learning_outcome,
                        confidence_score,
                        applied_successfully,
                        json.dumps(improvement_metrics) if improvement_metrics else None,
                    ),
                )

                conn.commit()
                print(f"✅ Logged {learning_type} learning event")

    def analyze_patterns(self):
        """Analyze interaction patterns and generate insights."""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                print("🔍 ANALYZING AI INTERACTION PATTERNS")
                print("=" * 50)

                # Tool effectiveness analysis
                print("\n📊 Tool Effectiveness Ranking:")
                cur.execute("""
                    SELECT tool_name, usage_count, success_rate,
                           average_execution_time_ms, last_used
                    FROM tool_effectiveness_ranking
                    LIMIT 10
                """)
                for row in cur.fetchall():
                    print(f"Tool: {row[0]}, Success rate: {row[1]:.1f}%, Avg time: {row[2]:.1f}ms")
                # Code generation quality analysis
                print("\n💻 Code Generation Quality:")
                cur.execute("SELECT * FROM code_generation_quality")
                for row in cur.fetchall():
                    acceptance_rate = (row[2] + row[3]) / row[1] if row[1] > 0 else 0
                    print(
                        f"Language: {row[0]}, Total: {row[1]}, Accepted: {row[2]}, Rejected: {row[3]}, Rate: {acceptance_rate:.1f}%"
                    )
                # User satisfaction trends
                print("\n😊 User Satisfaction (Last 7 days):")
                cur.execute("""
                    SELECT metric_date, average_rating, total_interactions
                    FROM satisfaction_metrics
                    WHERE metric_date >= CURRENT_DATE - INTERVAL '7 days'
                    ORDER BY metric_date DESC
                """)
                for row in cur.fetchall():
                    print(f"Date: {row[0]}, Rating: {row[1]:.2f}, Interactions: {row[2]}")
                # Learning insights
                print("\n🧠 Learning Insights:")
                cur.execute("SELECT * FROM learning_insights_summary")
                for row in cur.fetchall():
                    success_rate = row[2] / row[1] if row[1] > 0 else 0
                    print(f"Pattern: {row[0]}, Total: {row[1]}, Success: {row[2]}, Rate: {success_rate:.1f}%")
                # Generate automated insights
                self.generate_insights()

    def generate_insights(self):
        """Generate automated insights from the data."""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                insights = []

                # Insight 1: Tool usage patterns
                cur.execute("""
                    SELECT tool_name, success_rate, usage_count
                    FROM tool_effectiveness_ranking
                    WHERE usage_count > 5
                    ORDER BY success_rate ASC
                    LIMIT 3
                """)
                low_performing_tools = cur.fetchall()
                if low_performing_tools:
                    insights.append(
                        {
                            "type": "improvement",
                            "title": "Tools Needing Attention",
                            "description": f"Tools with low success rates: {', '.join([f'{t[0]} ({t[1]:.1%})' for t in low_performing_tools])}",
                            "confidence": 0.8,
                            "data": {"tools": low_performing_tools},
                        }
                    )

                # Insight 2: Code generation patterns
                cur.execute("""
                    SELECT generation_type, total_generations,
                           (accepted_count::float / total_generations) as acceptance_rate
                    FROM code_generation_quality
                    WHERE total_generations > 3
                    ORDER BY acceptance_rate DESC
                    LIMIT 1
                """)
                best_gen_type = cur.fetchone()
                if best_gen_type:
                    insights.append(
                        {
                            "type": "pattern",
                            "title": "Most Successful Code Generation Type",
                            "description": f"{best_gen_type[0]} has {best_gen_type[2]:.1%} acceptance rate from {best_gen_type[1]} generations",
                            "confidence": 0.9,
                            "data": {"generation_type": best_gen_type[0], "acceptance_rate": best_gen_type[2]},
                        }
                    )

                # Insight 3: User satisfaction trends
                cur.execute("""
                    SELECT AVG(average_rating) as avg_satisfaction,
                           STDDEV(average_rating) as satisfaction_variance
                    FROM satisfaction_metrics
                    WHERE metric_date >= CURRENT_DATE - INTERVAL '30 days'
                """)
                satisfaction_stats = cur.fetchone()
                if satisfaction_stats and satisfaction_stats[0]:
                    avg_sat, variance = satisfaction_stats
                    if variance > 0.5:  # High variance indicates inconsistent satisfaction
                        insights.append(
                            {
                                "type": "anomaly",
                                "title": "Inconsistent User Satisfaction",
                                "description": f"User satisfaction variance of {variance:.2f} detected",
                                "confidence": 0.7,
                                "data": {"avg_satisfaction": avg_sat, "variance": variance},
                            }
                        )

                # Store insights
                for insight in insights:
                    cur.execute(
                        """
                        INSERT INTO ai_performance_insights
                        (insight_type, insight_title, insight_description,
                         supporting_data, confidence_level)
                        VALUES (%s, %s, %s, %s, %s)
                    """,
                        (
                            insight["type"],
                            insight["title"],
                            insight["description"],
                            json.dumps(insight["data"]),
                            insight["confidence"],
                        ),
                    )

                conn.commit()

                if insights:
                    print(f"\n💡 Generated {len(insights)} automated insights")
                    for insight in insights:
                        print(f"  • {insight['title']}: {insight['description'][:100]}...")

    def export_learning_data(self, output_file: str | None = None):
        """Export learning data for analysis."""
        if not output_file:
            output_file = f"ai_learning_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "interactions": [],
            "tool_analytics": [],
            "code_generation": [],
            "user_feedback": [],
            "learning_events": [],
            "insights": [],
        }

        with self.get_connection() as conn:
            with conn.cursor() as cur:
                # Export recent interactions (last 30 days)
                cur.execute("""
                    SELECT session_id, interaction_type, user_query, ai_response,
                           tools_used, execution_time_ms, success, created_at
                    FROM ai_interactions
                    WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
                    ORDER BY created_at DESC
                """)
                export_data["interactions"] = [
                    {
                        "session_id": row[0],
                        "type": row[1],
                        "query": row[2],
                        "response": row[3],
                        "tools": row[4],
                        "execution_time_ms": row[5],
                        "success": row[6],
                        "timestamp": row[7].isoformat(),
                    }
                    for row in cur.fetchall()
                ]

                # Export tool analytics
                cur.execute("SELECT * FROM tool_effectiveness_ranking")
                export_data["tool_analytics"] = [
                    {
                        "tool_name": row[0],
                        "usage_count": row[1],
                        "success_rate": float(row[2]) if row[2] else 0,
                        "avg_execution_time": float(row[3]) if row[3] else 0,
                        "last_used": row[4].isoformat() if row[4] else None,
                    }
                    for row in cur.fetchall()
                ]

                # Export code generation data
                cur.execute("""
                    SELECT generation_type, target_file, acceptance_status,
                           time_to_accept_minutes, created_at
                    FROM code_generation_events
                    WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
                """)
                export_data["code_generation"] = [
                    {
                        "type": row[0],
                        "file": row[1],
                        "status": row[2],
                        "time_to_accept": row[3],
                        "timestamp": row[4].isoformat(),
                    }
                    for row in cur.fetchall()
                ]

                # Export user feedback
                cur.execute("""
                    SELECT feedback_type, rating, feedback_text, context_tags, created_at
                    FROM user_feedback
                    WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
                """)
                export_data["user_feedback"] = [
                    {
                        "type": row[0],
                        "rating": row[1],
                        "feedback": row[2],
                        "tags": row[3],
                        "timestamp": row[4].isoformat(),
                    }
                    for row in cur.fetchall()
                ]

                # Export learning events
                cur.execute("""
                    SELECT learning_type, learning_outcome, confidence_score,
                           applied_successfully, created_at
                    FROM learning_events
                    WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
                """)
                export_data["learning_events"] = [
                    {
                        "type": row[0],
                        "outcome": row[1],
                        "confidence": float(row[2]) if row[2] else 0,
                        "applied": row[3],
                        "timestamp": row[4].isoformat(),
                    }
                    for row in cur.fetchall()
                ]

                # Export insights
                cur.execute("""
                    SELECT insight_type, insight_title, insight_description,
                           confidence_level, actionable, created_at
                    FROM ai_performance_insights
                    WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
                """)
                export_data["insights"] = [
                    {
                        "type": row[0],
                        "title": row[1],
                        "description": row[2],
                        "confidence": float(row[3]) if row[3] else 0,
                        "actionable": row[4],
                        "timestamp": row[5].isoformat(),
                    }
                    for row in cur.fetchall()
                ]

        # Write export file
        output_path = ROOT / "exports" / output_file
        output_path.parent.mkdir(exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(export_data, f, indent=2)

        print(f"✅ Exported AI learning data to {output_path}")
        print(f"  📊 {len(export_data['interactions'])} interactions")
        print(f"  🛠️  {len(export_data['tool_analytics'])} tool analytics")
        print(f"  💻 {len(export_data['code_generation'])} code generations")
        print(f"  😊 {len(export_data['user_feedback'])} feedback entries")
        print(f"  🧠 {len(export_data['learning_events'])} learning events")
        print(f"  💡 {len(export_data['insights'])} insights")


def main():
    parser = argparse.ArgumentParser(description="AI Learning Tracker")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Log interaction
    log_parser = subparsers.add_parser("log_interaction", help="Log an AI interaction")
    log_parser.add_argument("--session-id", required=True)
    log_parser.add_argument(
        "--type", required=True, choices=["user_query", "tool_call", "code_generation", "validation"]
    )
    log_parser.add_argument("--query")
    log_parser.add_argument("--response")
    log_parser.add_argument("--tools", nargs="*")
    log_parser.add_argument("--context", type=json.loads)
    log_parser.add_argument("--exec-time", type=int)
    log_parser.add_argument("--error")

    # Log feedback
    feedback_parser = subparsers.add_parser("log_feedback", help="Log user feedback")
    feedback_parser.add_argument("--session-id", required=True)
    feedback_parser.add_argument("--type", required=True)
    feedback_parser.add_argument("--rating", type=int, required=True, choices=range(1, 6))
    feedback_parser.add_argument("--feedback")
    feedback_parser.add_argument("--suggestions")
    feedback_parser.add_argument("--tags", nargs="*")

    # Analysis commands
    subparsers.add_parser("analyze_patterns", help="Analyze interaction patterns")
    subparsers.add_parser("generate_insights", help="Generate automated insights")
    subparsers.add_parser("export_learning_data", help="Export learning data for analysis")

    args = parser.parse_args()

    tracker = AILearningTracker()

    try:
        if args.command == "log_interaction":
            success = args.error is None
            tracker.log_interaction(
                session_id=args.session_id,
                interaction_type=args.type,
                user_query=args.query,
                ai_response=args.response,
                tools_used=args.tools,
                context=args.context,
                execution_time_ms=args.exec_time,
                success=success,
                error_details=args.error,
            )

        elif args.command == "log_feedback":
            tracker.log_user_feedback(
                session_id=args.session_id,
                feedback_type=args.type,
                rating=args.rating,
                feedback_text=args.feedback,
                suggestions=args.suggestions,
                tags=args.tags,
            )

        elif args.command == "analyze_patterns":
            tracker.analyze_patterns()

        elif args.command == "generate_insights":
            tracker.generate_insights()

        elif args.command == "export_learning_data":
            tracker.export_learning_data()

        else:
            parser.print_help()

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
