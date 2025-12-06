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
    check_branch_protection,
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


@app.command("alignment-guard")
def alignment_guard(
    strict: bool = typer.Option(
        False,
        "--strict",
        help="STRICT mode: fail on violations (default: HINT mode, warnings only)",
    ),
) -> None:
    """
    Check Layer 4 plan vs implementation alignment (detect drift).

    Compares expected code paths from LAYER4_CODE_INGESTION_PLAN.md with actual
    code locations in the repository. Detects integration islands like scripts/code_ingest/.

    Modes:
    - HINT (default): Emit warnings only, exit 0
    - STRICT (--strict): Fail closed on violations, exit 1
    """
    import subprocess

    guard_script = pathlib.Path("scripts/guards/guard_repo_layer4_alignment.py")
    if not guard_script.exists():
        typer.echo(f"Error: Guard script not found: {guard_script}", err=True)
        raise typer.Exit(code=1)

    args = ["python", str(guard_script)]
    if strict:
        args.append("--strict")

    result = subprocess.run(args)
    raise typer.Exit(code=result.returncode)


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
    force: bool = typer.Option(
        False,
        "--force",
        help="Force delete branches (use -D instead of -d)",
    ),
) -> None:
    """
    Delete branches that have been merged to main.

    Default is dry-run. Use --execute to actually delete.
    Use --force for branches that aren't fully merged upstream.
    """
    result = cleanup_merged_branches(dry_run=not execute, force=force)

    for msg in result["messages"]:
        typer.echo(msg)

    # Show summary if executed
    if not result["dry_run"] and result.get("summary"):
        summary = result["summary"]
        typer.echo("\n📊 Summary:")
        typer.echo(f"  Local deleted: {summary['local_deleted']}")
        typer.echo(f"  Remote deleted: {summary['remote_deleted']}")
        typer.echo(f"  Failed: {summary['failed']}")
        typer.echo(f"  Total cleaned: {summary['total_cleaned']}")

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


@app.command("guard-branch")
def guard_branch(
    allow_release: bool = typer.Option(
        False,
        "--allow-release",
        help="Allow running on protected branch (e.g. for release tags)",
    ),
) -> None:
    """
    Guard against direct work on protected branches (main).

    Returns exit code 1 if on a protected branch, 0 otherwise.
    Use in pre-commit hooks or scripts to enforce branch policy.
    """
    result = check_branch_protection(allow_release=allow_release)

    for msg in result["messages"]:
        typer.echo(msg)

    if not result["success"]:
        if result.get("error"):
            typer.echo(f"\n{result['error']}")
        raise typer.Exit(code=1)
