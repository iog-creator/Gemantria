from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
WEBPROOF_PATH = REPO_ROOT / "docs" / "atlas" / "webproof" / "knowledge_mcp.html"
EVIDENCE_DIR = REPO_ROOT / "evidence"
VERDICT_PATH = EVIDENCE_DIR / "guard_control_knowledge_mcp_webproof_backlinks.json"


@dataclass
class BacklinkCheck:
    name: str
    present: bool
    errors: list[str]


@dataclass
class WebproofGuardVerdict:
    ok: bool
    checks: list[BacklinkCheck]
    errors: list[str]


def _load_html(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _check_snippet(label: str, html: str, snippet: str) -> BacklinkCheck:
    errors: list[str] = []
    present = snippet in html
    if not present:
        errors.append(f"missing snippet: {snippet!r}")
    return BacklinkCheck(name=label, present=present, errors=errors)


def run_guard() -> WebproofGuardVerdict:
    checks: list[BacklinkCheck] = []
    errors: list[str] = []

    if not WEBPROOF_PATH.exists():
        errors.append("knowledge_mcp.html webproof page is missing")
        return WebproofGuardVerdict(ok=False, checks=[], errors=errors)

    html = _load_html(WEBPROOF_PATH)

    snippets: list[tuple[str, str]] = [
        ("back-to-atlas", 'data-testid="link-back-to-atlas"'),
        ("mcp_catalog-json", 'data-testid="link-mcp_catalog-json"'),
        ("capability_rules-json", 'data-testid="link-capability_rules-json"'),
        ("agent_runs_7d-json", 'data-testid="link-agent_runs_7d-json"'),
        (
            "guard-control-knowledge-mcp-exports",
            'data-testid="link-guard-control-knowledge-mcp-exports-json"',
        ),
    ]

    for label, snippet in snippets:
        check = _check_snippet(label, html, snippet)
        checks.append(check)
        errors.extend(f"{label}: {e}" for e in check.errors)

    ok = not errors
    return WebproofGuardVerdict(ok=ok, checks=checks, errors=errors)


def main() -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    verdict = run_guard()
    VERDICT_PATH.write_text(
        json.dumps(asdict(verdict), indent=2, sort_keys=True),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
