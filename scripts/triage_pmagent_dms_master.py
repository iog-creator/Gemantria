#!/usr/bin/env python3
"""
Triage for pmagent + DMS master test.

- Reads:  evidence/system/pmagent_dms_master_report.json
- If all checks PASS: prints a summary and exits 0.
- If any checks FAIL/ERROR:
    - Summarizes failures
    - Calls local LM (LM Studio at http://127.0.0.1:1234/v1/chat/completions)
    - Writes a triage report to:
         evidence/system/pmagent_dms_master_triage.md
    - Prints path to triage report and exits 1.

This is the first step toward "when the master test reveals an issue,
pmagent uses an LLM to decide what to do."
"""

import datetime
import json
import os
import sys
import textwrap
import urllib.request
from pathlib import Path
from typing import Any, Dict, List


MASTER_REPORT_PATH = Path("evidence/system/pmagent_dms_master_report.json")
TRIAGE_REPORT_PATH = Path("evidence/system/pmagent_dms_master_triage.md")

# LM Studio endpoint - can be overridden via TRIAGE_LM_ENDPOINT env var
LM_ENDPOINT = os.getenv("TRIAGE_LM_ENDPOINT", "http://127.0.0.1:1234/v1/chat/completions")
# Model name - can be overridden via TRIAGE_LM_MODEL env var
# Defaults to a general-purpose model; adjust to your LM Studio model name
LM_MODEL = os.getenv("TRIAGE_LM_MODEL", "local-pmagent-triage")


def load_master_report() -> Dict[str, Any]:
    """Load the master test report JSON."""
    if not MASTER_REPORT_PATH.exists():
        print(f"[TRIAGE] Master report not found at {MASTER_REPORT_PATH}", file=sys.stderr)
        sys.exit(1)
    try:
        return json.loads(MASTER_REPORT_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[TRIAGE] Failed to parse master report JSON: {e}", file=sys.stderr)
        sys.exit(1)


def collect_failed_checks(report: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Collect all checks with status FAIL or ERROR."""
    results = report.get("results") or []
    failed = [r for r in results if isinstance(r, dict) and r.get("status") in ("FAIL", "ERROR")]
    return failed


def build_llm_prompt(report: Dict[str, Any], failed: List[Dict[str, Any]]) -> str:
    """Build the prompt to send to the LM for triage."""
    run_id = report.get("run_id")
    timestamp = report.get("timestamp")

    lines = []
    lines.append("You are a senior PM/OPS assistant for the Gemantria system.")
    lines.append("You are triaging failures from the pmagent + DMS master verification test.")
    lines.append("")
    lines.append(f"Master test run_id: {run_id}")
    lines.append(f"Timestamp (UTC): {timestamp}")
    lines.append("")
    lines.append("Each failure below comes from a structured check in the master test.")
    lines.append("For each failing check, you MUST:")
    lines.append("  1. Classify the issue type (e.g., BUG, MISSING_FEATURE, TEST_OUT_OF_DATE, CONFIG, DESIGN_GAP).")
    lines.append("  2. Explain likely root cause in 1-3 sentences.")
    lines.append("  3. Propose concrete next actions for the pmagent/DMS team (bulleted list).")
    lines.append("  4. Note any dependencies or preconditions (if any).")
    lines.append("")
    lines.append("At the end, produce a short overall summary:")
    lines.append("  - Overall risk level (LOW/MEDIUM/HIGH).")
    lines.append("  - Whether the system is safe to use for Phase 15 work.")
    lines.append("")
    lines.append("Here are the failing checks:\n")

    for r in failed:
        cid = r.get("id")
        name = r.get("name")
        category = r.get("category")
        status = r.get("status")
        error = r.get("error")
        details = r.get("details")

        # Keep details trimmed to avoid overwhelming the LM
        trimmed_details = details or ""
        if len(trimmed_details) > 2000:
            trimmed_details = trimmed_details[:2000] + "\n[... trimmed ...]"

        block = f"""
=== CHECK: {cid} ===
Name: {name}
Category: {category}
Status: {status}

Error:
{error}

Details (trimmed):
{trimmed_details}
"""
        lines.append(textwrap.dedent(block).strip())
        lines.append("")

    return "\n".join(lines)


def call_local_lm(prompt: str) -> str:
    """Call the local LM Studio endpoint with a chat-style request."""
    req_body = {
        "model": LM_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are a precise, structured PM/OPS triage assistant. "
                "You respect the Gemantria PM contract and DMS-first governance.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        "temperature": 0.1,
    }

    data = json.dumps(req_body).encode("utf-8")
    req = urllib.request.Request(
        LM_ENDPOINT,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            resp_data = resp.read().decode("utf-8")
    except Exception as e:
        return f"[TRIAGE] ERROR: Failed to call local LM: {e}"

    try:
        parsed = json.loads(resp_data)
    except Exception as e:
        return f"[TRIAGE] ERROR: Failed to parse LM response JSON: {e}\nRaw: {resp_data}"

    # Expect OpenAI-style shape: choices[0].message.content
    try:
        choices = parsed.get("choices") or []
        if not choices:
            return f"[TRIAGE] ERROR: LM response has no choices.\nRaw: {parsed}"
        msg = choices[0].get("message") or {}
        content = msg.get("content")
        if not content:
            return f"[TRIAGE] ERROR: LM choice has no content.\nRaw: {parsed}"
        return content
    except Exception as e:
        return f"[TRIAGE] ERROR: Unexpected LM response shape: {e}\nRaw: {parsed}"


def write_triage_report(prompt: str, lm_response: str) -> None:
    """Write the triage report to markdown file."""
    TRIAGE_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.datetime.now(datetime.UTC).isoformat()

    body = [
        "# pmagent + DMS Master Test Triage Report",
        "",
        f"- Generated at: {now}",
        f"- Source report: {MASTER_REPORT_PATH}",
        "",
        "## Input Summary (Prompt to LM)",
        "",
        "```text",
        prompt,
        "```",
        "",
        "## LM Triage Response",
        "",
        lm_response,
        "",
    ]
    TRIAGE_REPORT_PATH.write_text("\n".join(body), encoding="utf-8")


def main() -> int:
    """Main triage function."""
    report = load_master_report()
    failed = collect_failed_checks(report)

    total = len(report.get("results") or [])
    print(f"[TRIAGE] Master test had {total} checks, {len(failed)} failures.")

    if not failed:
        print("[TRIAGE] All checks passed. No triage needed.")
        return 0

    prompt = build_llm_prompt(report, failed)
    print("[TRIAGE] Calling local LM for triage...")
    lm_response = call_local_lm(prompt)

    write_triage_report(prompt, lm_response)
    print(f"[TRIAGE] Triage report written to: {TRIAGE_REPORT_PATH}")

    # Non-zero exit: indicates there WERE failures
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
