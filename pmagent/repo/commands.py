import pathlib

import typer

from .logic import (
    run_semantic_inventory,
    run_reunion_plan,
    run_quarantine_candidates,
)

app = typer.Typer(help="Repository introspection commands.")

EVIDENCE_DIR = pathlib.Path("evidence/repo")
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)


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
