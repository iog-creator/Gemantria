from scripts.config.env import get_rw_dsn

# OPS meta: Rules 050/051/052 AlwaysApply | SSOT: ruff | Housekeeping: `make housekeeping`
# Timestamp contract: RFC3339 fast-lane (generated_at RFC3339; metadata.source="fallback_fast_lane")

#!/usr/bin/env python3
"""
ai_analytics_dashboard.py — AI performance analytics and insights dashboard.

Provides comprehensive analytics on AI interactions, learning patterns,
user satisfaction, and performance metrics with actionable insights.

Features:
- Real-time performance monitoring
- Trend analysis and forecasting
- User satisfaction tracking
- Learning effectiveness metrics
- Tool and model performance analysis

Usage:
    python scripts/ai_analytics_dashboard.py dashboard          # Full dashboard
    python scripts/ai_analytics_dashboard.py trends --days 30   # Trend analysis
    python scripts/ai_analytics_dashboard.py insights           # Actionable insights
    python scripts/ai_analytics_dashboard.py alerts             # Performance alerts
"""

import argparse
from pathlib import Path

import psycopg

# Database connection
GEMATRIA_DSN = get_rw_dsn()
if not GEMATRIA_DSN:
    print("ERROR: GEMATRIA_DSN environment variable required")
    exit(1)

ROOT = Path(__file__).resolve().parent.parent


def show_dashboard():
    """Show comprehensive AI analytics dashboard."""
    print("🤖 AI ANALYTICS DASHBOARD")
    print("=" * 50)

    try:
        conn = psycopg.connect(GEMATRIA_DSN)
        cur = conn.cursor()

        # Overall metrics
        cur.execute("""
            SELECT COUNT(*) as total_interactions,
                   AVG(execution_time_ms) as avg_response_time,
                   SUM(CASE WHEN success THEN 1 ELSE 0 END)::float / COUNT(*) as success_rate
            FROM ai_interactions
            WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
        """)

        row = cur.fetchone()
        total_interactions = row[0] or 0
        avg_response_time = row[1] or 0
        success_rate = row[2] or 0

        print(f"📊 Total Interactions (7d): {total_interactions}")
        print(f"⚡ Average Response Time: {avg_response_time:.1f}ms")
        print(f"✅ Success Rate: {success_rate:.1%}")

        # Active sessions
        cur.execute("""
            SELECT COUNT(DISTINCT session_id) as active_sessions
            FROM ai_interactions
            WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
        """)
        active_sessions = cur.fetchone()[0] or 0
        print(f"👥 Active Sessions (7d): {active_sessions}")

        # Code generations
        cur.execute("""
            SELECT COUNT(*) as code_generations,
                   SUM(CASE WHEN acceptance_status = 'accepted' THEN 1 ELSE 0 END)::float / COUNT(*) as acceptance_rate
            FROM code_generation_events
            WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
        """)
        row = cur.fetchone()
        code_generations = row[0] or 0
        acceptance_rate = row[1] or 0
        print(f"📝 Code Generations: {code_generations}, Acceptance Rate: {acceptance_rate:.1%}")

        # Tool effectiveness
        cur.execute("""
            SELECT tool_name, usage_count, success_rate
            FROM tool_effectiveness_ranking
            ORDER BY success_rate DESC, usage_count DESC
            LIMIT 5
        """)

        if cur.rowcount > 0:
            print("\n🛠️  Top Tools:")
            for row in cur.fetchall():
                tool_name = row[0]
                usage_count = row[1]
                success_rate = row[2] or 0
                status_icon = "🟢" if success_rate > 0.9 else "🟡" if success_rate > 0.7 else "🔴"
                print(
                    f"  {status_icon} {tool_name}: {usage_count} uses, {success_rate:.1%} success"
                )

        # User feedback
        cur.execute("""
            SELECT AVG(rating) as avg_rating, COUNT(*) as total_feedback
            FROM user_feedback
            WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
        """)
        row = cur.fetchone()
        avg_rating = row[0] or 0
        total_feedback = row[1] or 0
        if total_feedback > 0:
            print(
                f"\n⭐ User Satisfaction (7d): {avg_rating:.1f}/5.0 from {total_feedback} ratings"
            )

        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("💡 Make sure GEMATRIA_DSN is set and database is accessible")


def show_trends(days: int = 30):
    """Show performance trends over time."""
    print(f"📈 PERFORMANCE TRENDS (Last {days} days)")
    print("=" * 50)

    try:
        conn = psycopg.connect(GEMATRIA_DSN)
        cur = conn.cursor()

        # Daily success rates
        cur.execute(f"""
            SELECT DATE(created_at) as date,
                   COUNT(*) as interactions,
                   SUM(CASE WHEN success THEN 1 ELSE 0 END)::float / COUNT(*) as success_rate
            FROM ai_interactions
            WHERE created_at >= CURRENT_DATE - INTERVAL '{days} days'
            GROUP BY DATE(created_at)
            ORDER BY date
        """)

        print("📈 Daily Success Rate Trends:")
        prev_rate = None
        for row in cur.fetchall():
            date_str = row[0].strftime("%m/%d")
            interactions = row[1]
            success_rate = row[2] or 0
            trend = ""
            if prev_rate is not None:
                if success_rate > prev_rate + 0.05:
                    trend = "↗️"
                elif success_rate < prev_rate - 0.05:
                    trend = "↘️"
                else:
                    trend = "➡️"
            print(f"  {date_str}: {interactions} interactions, {success_rate:.1%} success {trend}")
            prev_rate = success_rate

        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Database connection failed: {e}")


def show_insights():
    """Show actionable insights from AI learning data."""
    print("💡 AI LEARNING INSIGHTS")
    print("=" * 30)

    try:
        conn = psycopg.connect(GEMATRIA_DSN)
        cur = conn.cursor()

        # Learning effectiveness
        cur.execute("""
            SELECT learning_type, COUNT(*) as events,
                   AVG(confidence_score) as avg_confidence,
                   SUM(CASE WHEN applied_successfully THEN 1 ELSE 0 END)::float / COUNT(*) as success_rate
            FROM learning_events
            WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
            GROUP BY learning_type
            ORDER BY events DESC
            LIMIT 5
        """)

        if cur.rowcount > 0:
            print("🎓 Learning Effectiveness:")
            for row in cur.fetchall():
                learning_type = row[0]
                events = row[1]
                avg_confidence = row[2] or 0
                success_rate = row[3] or 0
                print(
                    f"  📖 {learning_type}: {events} events, {success_rate:.1%} success, {avg_confidence:.2f} confidence"
                )

        # Performance insights
        cur.execute("""
            SELECT 'High Error Rate' as insight,
                   tool_name || ' has ' || ROUND(error_rate * 100, 1) || '% error rate' as description,
                   error_rate as severity
            FROM (
                SELECT tool_name,
                       1.0 - (SUM(CASE WHEN success THEN 1 ELSE 0 END)::float / COUNT(*)) as error_rate
                FROM tool_usage_analytics
                WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
                GROUP BY tool_name
                HAVING COUNT(*) >= 10
            ) t
            WHERE error_rate > 0.2
            ORDER BY error_rate DESC
            LIMIT 3
        """)

        if cur.rowcount > 0:
            print("\n⚠️  Performance Alerts:")
            for row in cur.fetchall():
                insight = row[0]
                description = row[1]
                severity = row[2]
                severity_icon = "🔴" if severity > 0.3 else "🟡"
                print(f"  {severity_icon} {insight}: {description}")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Database connection failed: {e}")


def show_alerts():
    """Show critical performance alerts."""
    print("🚨 AI PERFORMANCE ALERTS")
    print("=" * 30)

    try:
        conn = psycopg.connect(GEMATRIA_DSN)
        cur = conn.cursor()

        alerts = []

        # Check for low success rates
        cur.execute("""
            SELECT 'Low Success Rate' as alert_type,
                   'Overall success rate below 80%' as message,
                   success_rate as value
            FROM (
                SELECT SUM(CASE WHEN success THEN 1 ELSE 0 END)::float / COUNT(*) as success_rate
                FROM ai_interactions
                WHERE created_at >= CURRENT_DATE - INTERVAL '1 day'
            ) t
            WHERE success_rate < 0.8
        """)

        if cur.rowcount > 0:
            row = cur.fetchone()
            alerts.append(f"🔴 {row[0]}: {row[1]} ({row[2]:.1%})")

        # Check for high error tools
        cur.execute("""
            SELECT 'Tool Error Rate' as alert_type,
                   tool_name || ' error rate: ' || ROUND(error_rate * 100, 1) || '%' as message,
                   error_rate as value
            FROM (
                SELECT tool_name,
                       1.0 - (SUM(CASE WHEN success THEN 1 ELSE 0 END)::float / COUNT(*)) as error_rate
                FROM tool_usage_analytics
                WHERE created_at >= CURRENT_DATE - INTERVAL '1 day'
                GROUP BY tool_name
                HAVING COUNT(*) >= 5
            ) t
            WHERE error_rate > 0.25
            ORDER BY error_rate DESC
            LIMIT 2
        """)

        for row in cur.fetchall():
            alerts.append(f"🟡 {row[0]}: {row[1]}")

        # Check for low user satisfaction
        cur.execute("""
            SELECT 'Low User Satisfaction' as alert_type,
                   'Average rating below 3.5' as message,
                   avg_rating as value
            FROM (
                SELECT AVG(rating) as avg_rating
                FROM user_feedback
                WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
                HAVING COUNT(*) >= 5
            ) t
            WHERE avg_rating < 3.5
        """)

        if cur.rowcount > 0:
            row = cur.fetchone()
            alerts.append(f"🟡 {row[0]}: {row[1]} ({row[2]:.1f}/5.0)")

        if alerts:
            for alert in alerts:
                print(alert)
        else:
            print("✅ No critical alerts at this time")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Database connection failed: {e}")


def main():
    parser = argparse.ArgumentParser(description="AI Analytics Dashboard")
    parser.add_argument(
        "command", choices=["dashboard", "trends", "insights", "alerts"], help="Command to run"
    )
    parser.add_argument("--days", type=int, default=30, help="Number of days for trend analysis")

    args = parser.parse_args()

    if args.command == "dashboard":
        show_dashboard()
    elif args.command == "trends":
        show_trends(args.days)
    elif args.command == "insights":
        show_insights()
    elif args.command == "alerts":
        show_alerts()


if __name__ == "__main__":
    main()
