import pathlib

import typer

from .logic import (
    run_semantic_inventory,
    run_reunion_plan,
    run_quarantine_candidates,
    create_branch,
    update_branch_from_main,
    safe_merge_to_main,
    cleanup_merged_branches,
    get_branch_status,
)

app = typer.Typer(help="Repository introspection and git workflow commands.")

EVIDENCE_DIR = pathlib.Path("evidence/repo")
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================================
# Repository Introspection Commands
# ============================================================================


@app.command("semantic-inventory")
def semantic_inventory(
    write_share: bool = typer.Option(
        False,
        "--write-share",
        help="Also write share/exports/repo/semantic_inventory.json",
    ),
) -> None:
    """
    Generate a DMS/Layer-4-aligned semantic inventory of the repository.
    """
    run_semantic_inventory(write_share=write_share)


@app.command("reunion-plan")
def reunion_plan(
    write_share: bool = typer.Option(
        False,
        "--write-share",
        help="Also write share/exports/repo/reunion_plan.json",
    ),
) -> None:
    """
    Produce an integration + quarantine plan using the semantic inventory.
    """
    run_reunion_plan(write_share=write_share)


@app.command("quarantine-candidates")
def quarantine_candidates(
    write_share: bool = typer.Option(
        False,
        "--write-share",
        help="Also write share/exports/repo/quarantine_candidates.json",
    ),
) -> None:
    """
    Extract quarantinable file paths ('quarantine island') from the reunion plan.
    """
    run_quarantine_candidates(write_share=write_share)


# ============================================================================
# Git Workflow Commands (Automate Safe Branching)
# ============================================================================


@app.command("branch-create")
def branch_create(
    name: str = typer.Argument(..., help="Name for the new branch"),
    base: str = typer.Option("main", "--base", help="Base branch (default: main)"),
) -> None:
    """
    Create new branch from fresh main (prevents branch drift).

    Automatically fetches latest, checks out main, pulls, then creates new branch.
    """
    result = create_branch(name, base)

    for msg in result["messages"]:
        typer.echo(msg)

    if not result["success"]:
        raise typer.Exit(code=1)


@app.command("branch-update")
def branch_update(
    strategy: str = typer.Option(
        "merge",
        "--strategy",
        help="Update strategy: 'merge' or 'rebase'",
    ),
) -> None:
    """
    Update current branch with latest main (prevents getting behind).

    Fetches latest main and merges or rebases your branch onto it.
    """
    result = update_branch_from_main(strategy)

    for msg in result["messages"]:
        typer.echo(msg)

    if not result["success"]:
        raise typer.Exit(code=1)


@app.command("branch-merge")
def branch_merge(
    force: bool = typer.Option(
        False,
        "--force",
        help="Force merge (skip guard checks - DANGEROUS!)",
    ),
) -> None:
    """
    Safely merge current branch to main (prevents destructive merges).

    Runs guard checks to prevent deleting code, then merges to main.
    """
    result = safe_merge_to_main(force)

    for msg in result["messages"]:
        typer.echo(msg)

    if result.get("guard_checks"):
        typer.echo("\nGuard checks:")
        for k, v in result["guard_checks"].items():
            typer.echo(f"  {k}: {v}")

    if not result["success"]:
        raise typer.Exit(code=1)


@app.command("branch-cleanup")
def branch_cleanup(
    execute: bool = typer.Option(
        False,
        "--execute",
        help="Actually delete branches (default is dry-run)",
    ),
) -> None:
    """
    Delete branches that have been merged to main.

    Default is dry-run. Use --execute to actually delete.
    """
    result = cleanup_merged_branches(dry_run=not execute)

    for msg in result["messages"]:
        typer.echo(msg)

    if not result["success"]:
        raise typer.Exit(code=1)


@app.command("branch-status")
def branch_status() -> None:
    """
    Show status of current branch vs main.

    Shows commits ahead/behind, age, and warnings.
    """
    result = get_branch_status()

    for msg in result["messages"]:
        typer.echo(msg)

    if not result["success"]:
        raise typer.Exit(code=1)
