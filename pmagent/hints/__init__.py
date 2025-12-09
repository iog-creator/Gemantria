"""CLI commands for hint management."""

import json
import typer

# Note: Full hint generation functions (analyze_error_and_generate_hint, etc.)
# are not yet implemented in pmagent.hints. These are stub implementations
# for CLI compatibility. Full implementation pending Phase-4 hint automation.


def analyze_error_and_generate_hint(error: str, context: dict, auto_insert: bool = False) -> dict:
    """Stub: Generate hint from error (not yet implemented)."""
    return {
        "hint_metadata": {
            "logical_name": "stub_hint",
            "kind": "SUGGESTED",
        },
        "hint_payload": {
            "title": "Hint generation not yet implemented",
            "severity": "info",
        },
    }


def batch_generate_hints_from_session(
    session_file: str, filter_scope: str | None = None, auto_insert: bool = False
) -> list:
    """Stub: Batch generate hints (not yet implemented)."""
    return []


from pmagent.hints.registry import list_all_hints


def list_hints(scope: str | None = None, kind: str | None = None, flow: str | None = None) -> list:
    """List hints from registry."""
    return list_all_hints(scope=scope, kind=kind, flow=flow)


def export_hints_to_docs(output_dir: str) -> dict:
    """Stub: Export hints to docs (not yet implemented)."""
    return {"total": 0, "exported": 0, "errors": 0}


app = typer.Typer(help="Hint generation and management")


@app.command("generate")
def generate_hint(
    error: str = typer.Argument(..., help="Error message to analyze"),
    flow: str = typer.Option(..., "--flow", help="Flow/operation name"),
    scope: str = typer.Option("general", "--scope", help="Scope category"),
    title: str = typer.Option(None, "--title", help="Hint title"),
    fix: str = typer.Option(None, "--fix", help="Known fix"),
    code_ref: str = typer.Option(None, "--code-ref", help="Code reference"),
    auto_insert: bool = typer.Option(False, "--insert", help="Auto-insert to registry"),
    json_only: bool = typer.Option(False, "--json-only", help="Output JSON only"),
):
    """Generate a hint from an error message and context."""
    context = {
        "flow": flow,
        "scope": scope,
    }

    if title:
        context["title"] = title
    if fix:
        context["fix"] = fix
    if code_ref:
        context["code_ref"] = code_ref

    result = analyze_error_and_generate_hint(error, context, auto_insert=auto_insert)

    if json_only:
        typer.echo(json.dumps(result, indent=2))
    else:
        typer.echo(f"Generated hint: {result['hint_metadata']['logical_name']}")
        typer.echo(f"Severity: {result['hint_payload']['severity']}")
        typer.echo(f"Kind: {result['hint_metadata']['kind']}")
        if auto_insert:
            typer.echo("✓ Inserted to control.hint_registry")


@app.command("batch")
def batch_generate(
    session_file: str = typer.Argument(..., help="Path to session error log JSON"),
    scope: str = typer.Option(None, "--scope", help="Filter by scope"),
    auto_insert: bool = typer.Option(False, "--insert", help="Auto-insert all hints"),
    json_only: bool = typer.Option(False, "--json-only", help="Output JSON only"),
):
    """Batch-generate hints from a session error log."""
    hints = batch_generate_hints_from_session(
        session_file,
        filter_scope=scope,
        auto_insert=auto_insert,
    )

    if json_only:
        typer.echo(json.dumps(hints, indent=2))
    else:
        typer.echo(f"Generated {len(hints)} hints")
        for hint in hints:
            typer.echo(f"  • {hint['hint_metadata']['logical_name']}: {hint['hint_payload']['title']}")
        if auto_insert:
            typer.echo(f"\n✓ Inserted {len(hints)} hints to control.hint_registry")


@app.command("list")
def list_command(
    scope: str = typer.Option(None, "--scope", help="Filter by scope"),
    kind: str = typer.Option(None, "--kind", help="Filter by kind (REQUIRED/SUGGESTED/DEBUG)"),
    flow: str = typer.Option(None, "--flow", help="Filter by flow"),
    json_only: bool = typer.Option(False, "--json-only", help="Output JSON only"),
):
    """List hints from the registry."""
    hints = list_hints(scope=scope, kind=kind, flow=flow)

    if json_only:
        typer.echo(json.dumps(hints, indent=2))
    else:
        typer.echo(f"Found {len(hints)} hints:\n")
        for hint in hints:
            payload = hint["payload"]
            typer.echo(f"{hint['logical_name']}")
            typer.echo(f"  Scope: {hint['scope']} | Kind: {hint['kind']} | Priority: {hint['priority']}")
            typer.echo(f"  {payload.get('title', 'No title')}")
            typer.echo()


@app.command("export")
def export_command(
    output_dir: str = typer.Option("docs/hints", "--output", help="Output directory"),
    json_only: bool = typer.Option(False, "--json-only", help="Output JSON only"),
):
    """Export all hints to markdown documentation."""
    stats = export_hints_to_docs(output_dir)

    if json_only:
        typer.echo(json.dumps(stats, indent=2))
    else:
        typer.echo(f"Exported {stats['exported']}/{stats['total']} hints to {output_dir}")
        if stats["errors"] > 0:
            typer.echo(f"⚠ {stats['errors']} errors occurred")


if __name__ == "__main__":
    app()
