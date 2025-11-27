#!/usr/bin/env python3
"""
Control-plane BibleScholar reference answer slice export for Phase-6P.

Exports BibleScholar reference questions and answers from control.agent_run:
- Questions asked (extracted from messages)
- Verse references (if provided)
- Answers generated (from LM response)
- Metadata (tokens, latency, mode, budget_status)

Uses centralized DSN loader (never os.getenv directly).
Tolerates empty/nonexistent DB (exits 0, writes JSON with ok=false for CI tolerance).
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, UTC, timedelta
from pathlib import Path

# Add project root to path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from scripts.config.env import get_rw_dsn

try:
    import psycopg
except ImportError:
    print(
        "WARN: psycopg not available; skipping BibleScholar reference export (CI empty-DB tolerance).",
        file=sys.stderr,
    )
    # Write empty export for CI tolerance
    output_dir = REPO / "share" / "atlas" / "control_plane"
    output_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now(UTC).isoformat()
    payload = {
        "schema": "biblescholar_reference_v1",
        "generated_at": now,
        "ok": False,
        "connection_ok": False,
        "error": "psycopg not available",
        "questions": [],
        "summary": {
            "total_questions": 0,
            "by_mode": {},
            "by_verse_ref": {},
        },
    }
    (output_dir / "biblescholar_reference.json").write_text(json.dumps(payload, indent=2))
    sys.exit(0)

DSN = get_rw_dsn()
if not DSN:
    print("SKIP: GEMATRIA_DSN not set (empty-DB tolerance).", file=sys.stderr)
    # Write empty export for CI tolerance
    output_dir = REPO / "share" / "atlas" / "control_plane"
    output_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now(UTC).isoformat()
    payload = {
        "schema": "biblescholar_reference_v1",
        "generated_at": now,
        "ok": False,
        "connection_ok": False,
        "error": "DSN not set",
        "questions": [],
        "summary": {
            "total_questions": 0,
            "by_mode": {},
            "by_verse_ref": {},
        },
    }
    (output_dir / "biblescholar_reference.json").write_text(json.dumps(payload, indent=2))
    sys.exit(0)


def extract_question_from_messages(messages: list[dict]) -> str | None:
    """Extract question from messages array (user message content)."""
    if not isinstance(messages, list):
        return None
    for msg in messages:
        if isinstance(msg, dict) and msg.get("role") == "user":
            content = msg.get("content", "")
            if isinstance(content, str) and content.strip():
                # Try to extract just the question part (after "Question: " if present)
                if "Question:" in content:
                    parts = content.split("Question:", 1)
                    if len(parts) > 1:
                        return parts[1].strip()
                return content.strip()
    return None


def extract_verse_ref_from_messages(messages: list[dict]) -> str | None:
    """Extract verse reference from messages (look for OSIS format or common patterns)."""
    if not isinstance(messages, list):
        return None
    for msg in messages:
        if isinstance(msg, dict):
            content = msg.get("content", "")
            if isinstance(content, str):
                # Look for OSIS format (e.g., "Gen.1.1")
                import re

                osis_pattern = r"\b([A-Za-z]+\.\d+\.\d+)\b"
                match = re.search(osis_pattern, content)
                if match:
                    return match.group(1)
                # Look for common Bible reference patterns
                ref_pattern = r"\b([A-Za-z]+)\s+(\d+):(\d+)\b"
                match = re.search(ref_pattern, content)
                if match:
                    book, chapter, verse = match.groups()
                    return f"{book} {chapter}:{verse}"
    return None


def extract_answer_from_result(result_json: dict) -> str | None:
    """Extract answer text from result_json (response content)."""
    if not isinstance(result_json, dict):
        return None
    # Check if response contains choices (OpenAI-style)
    if "response" in result_json:
        response = result_json["response"]
        if isinstance(response, dict):
            if "choices" in response:
                choices = response.get("choices", [])
                if choices and len(choices) > 0:
                    content = choices[0].get("message", {}).get("content", "")
                    if content:
                        return str(content)
            # Check for direct content field
            if "content" in response:
                return str(response["content"])
    return None


def export_biblescholar_references(cur: psycopg.Cursor, window_days: int = 30) -> dict:
    """Export BibleScholar reference questions and answers."""
    try:
        cutoff = datetime.now(UTC) - timedelta(days=window_days)

        # Query agent_run for BibleScholar reference slice calls
        cur.execute(
            """
            SELECT id, args_json, result_json, created_at
            FROM control.agent_run
            WHERE tool = 'lm_studio'
              AND args_json->>'call_site' = 'biblescholar.reference_slice'
              AND created_at >= %s
            ORDER BY created_at DESC
            """,
            (cutoff,),
        )

        rows = cur.fetchall()

        questions: list[dict] = []
        by_mode: dict[str, int] = {}
        by_verse_ref: dict[str, int] = {}

        for row in rows:
            run_id = str(row[0])
            args_json = row[1] or {}
            result_json = row[2] or {}
            created_at = row[3]

            # Extract question
            messages = args_json.get("messages", [])
            question = extract_question_from_messages(messages)
            if not question:
                continue  # Skip if no question found

            # Extract verse reference
            verse_ref = extract_verse_ref_from_messages(messages)

            # Extract answer
            answer = extract_answer_from_result(result_json)

            # Extract metadata
            mode = result_json.get("mode", "unknown")
            latency_ms = result_json.get("latency_ms", 0)
            usage = result_json.get("usage", {})
            tokens_used = usage.get("total_tokens", 0) if isinstance(usage, dict) else 0
            ok = result_json.get("ok", False)

            # Build question entry
            question_entry = {
                "run_id": run_id,
                "question": question,
                "verse_ref": verse_ref,
                "answer": answer,
                "created_at": created_at.isoformat() if hasattr(created_at, "isoformat") else str(created_at),
                "metadata": {
                    "mode": mode,
                    "ok": ok,
                    "latency_ms": latency_ms,
                    "tokens_used": tokens_used,
                },
            }
            questions.append(question_entry)

            # Update summary stats
            by_mode[mode] = by_mode.get(mode, 0) + 1
            if verse_ref:
                by_verse_ref[verse_ref] = by_verse_ref.get(verse_ref, 0) + 1

        return {
            "questions": questions,
            "summary": {
                "total_questions": len(questions),
                "by_mode": by_mode,
                "by_verse_ref": by_verse_ref,
            },
            "window_days": window_days,
        }
    except Exception as e:
        return {
            "questions": [],
            "summary": {
                "total_questions": 0,
                "by_mode": {},
                "by_verse_ref": {},
            },
            "error": str(e),
        }


def main() -> int:
    """Generate BibleScholar reference export."""
    parser = argparse.ArgumentParser(description="Export BibleScholar reference questions and answers")
    parser.add_argument(
        "--window-days",
        type=int,
        default=30,
        help="Time window in days (default: 30)",
    )
    args = parser.parse_args()

    output_dir = REPO / "share" / "atlas" / "control_plane"
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        with psycopg.connect(DSN) as conn, conn.cursor() as cur:
            data = export_biblescholar_references(cur, args.window_days)

            payload = {
                "schema": "biblescholar_reference_v1",
                "generated_at": datetime.now(UTC).isoformat(),
                "ok": True,
                "connection_ok": True,
                **data,
            }

            output_file = output_dir / "biblescholar_reference.json"
            output_file.write_text(json.dumps(payload, indent=2))
            print(f"[control_biblescholar_reference_export] Wrote {output_file}")
            return 0
    except Exception as e:
        # Write error payload
        payload = {
            "schema": "biblescholar_reference_v1",
            "generated_at": datetime.now(UTC).isoformat(),
            "ok": False,
            "connection_ok": False,
            "error": str(e),
            "questions": [],
            "summary": {
                "total_questions": 0,
                "by_mode": {},
                "by_verse_ref": {},
            },
        }
        output_file = output_dir / "biblescholar_reference.json"
        output_file.write_text(json.dumps(payload, indent=2))
        print(f"[control_biblescholar_reference_export] ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
