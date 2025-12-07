#!/usr/bin/env python3
"""
PM Agent CLI - Handoff Commands

Handoff service for generating DMS-grounded context reports.
"""

from __future__ import annotations

import sys
from pathlib import Path

import typer
import subprocess

# Add project root to path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

# Import handoff generation function from existing script
from scripts.prepare_handoff import generate_handoff_content  # noqa: E402

app = typer.Typer(help="Handoff service commands")


@app.command("generate")
def handoff_generate(
    type: str = typer.Option("role", "--type", help="Handoff type (currently only 'role' supported)"),
    role: str = typer.Option(None, "--role", help="Role for handoff (e.g., 'orchestrator')"),
    output: str = typer.Option(None, "--output", "-o", help="Output file path (default: share/handoff_latest.md)"),
) -> None:
    """
    Generate a DMS-grounded handoff report.

    This command produces a structured handoff context report that the PM must use
    before planning new work. The report includes git state, PR information (if applicable),
    and baseline evidence per Rule 051.

    Example:
        pmagent handoff generate --type role --role orchestrator
    """
    # Validate type (for now, only 'role' is supported)
    if type != "role":
        print(
            f"Error: Unsupported handoff type '{type}'. Currently only 'role' is supported.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Generate handoff content using existing function
    try:
        content = generate_handoff_content()

        # Determine output path
        if output:
            output_path = Path(output)
        else:
            output_path = Path("share/handoff_latest.md")

        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write to file
        output_path.write_text(content, encoding="utf-8")

        # Print success message
        print(f"✅ Handoff report generated: {output_path}", file=sys.stderr)
        print(f"   Type: {type}", file=sys.stderr)
        if role:
            print(f"   Role: {role}", file=sys.stderr)
        print(f"   Size: {len(content)} bytes", file=sys.stderr)

        # Also print content to stdout for piping/redirection
        print(content)

        sys.exit(0)

        sys.exit(0)
    except Exception as e:
        print(f"Error generating handoff report: {e}", file=sys.stderr)
        sys.exit(1)


@app.command("kernel")
def handoff_kernel(
    output: bool = typer.Option(True, "--output", help="Write to share/HANDOFF_KERNEL.json (legacy)"),
) -> None:
    """
    Generate share/HANDOFF_KERNEL.json (System Boot Kernel).
    """
    script = ROOT / "scripts" / "pm" / "generate_handoff_kernel.py"
    try:
        # We just call the script logic.
        cmd = [sys.executable, str(script)]
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError:
        print("Failed to generate handoff kernel", file=sys.stderr)
        sys.exit(1)


@app.command("kernel-bundle")
def handoff_kernel_bundle(
    out_dir: Path = typer.Option(ROOT / "share" / "handoff", "--out-dir", help="Output directory under share/"),
) -> None:
    """
    Generate the PM handoff kernel bundle (JSON + summary markdown).
    """
    from pmagent.handoff.kernel import write_kernel_bundle

    try:
        kernel_path, summary_path = write_kernel_bundle(out_dir)
        print(f"Wrote kernel to {kernel_path}")
        print(f"Wrote summary to {summary_path}")
    except Exception as e:
        print(f"Failed to generate kernel bundle: {e}", file=sys.stderr)
        sys.exit(1)


# Phase 26.B: Kernel-Aware Boot Flows (Design Complete — Implementation Pending)
# See: docs/SSOT/PHASE26_PMAGENT_BOOT_SPEC.md


@app.command("status-handoff")
def handoff_status(
    json_output: bool = typer.Option(False, "--json", help="Output JSON"),
) -> None:
    """
    Check handoff kernel health (Phase 26.B).

    Reads PM_KERNEL.json + PM_BOOTSTRAP_STATE.json and emits health status.

    Example:
        pmagent handoff status-handoff --json

    Spec: docs/SSOT/PHASE26_PMAGENT_BOOT_SPEC.md
    """
    from pmagent.handoff.status import (
        load_kernel,
        load_bootstrap,
        load_reality_green,
        check_consistency,
        build_status_envelope,
        format_status_human,
    )

    try:
        # Load surfaces
        kernel = load_kernel()
        bootstrap = load_bootstrap()
        health = load_reality_green()

        # Check consistency
        warnings = check_consistency(kernel, bootstrap)

        # Build envelope
        envelope = build_status_envelope(kernel, bootstrap, health, warnings)

        # Output
        if json_output:
            import json

            print(json.dumps(envelope, indent=2))
        else:
            print(format_status_human(envelope))

        sys.exit(0)

    except FileNotFoundError as e:
        error_envelope = {"ok": False, "error": str(e), "degraded": True}
        if json_output:
            import json

            print(json.dumps(error_envelope, indent=2))
        else:
            print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


@app.command("boot-pm")
def boot_pm(
    mode: str = typer.Option("json", "--mode", help="Output mode: json|seed"),
) -> None:
    """
    Generate PM boot envelope (Phase 26.B).

    Reads kernel + bootstrap and emits boot context for PM chat initialization.

    Example:
        pmagent handoff boot-pm --mode seed

    Spec: docs/SSOT/PHASE26_PMAGENT_BOOT_SPEC.md
    """
    from pmagent.handoff.status import (
        load_kernel,
        load_bootstrap,
        load_reality_green,
        check_consistency,
        build_boot_envelope,
        format_boot_seed,
    )

    try:
        # Load surfaces
        kernel = load_kernel()
        bootstrap = load_bootstrap()
        health = load_reality_green()

        # Check consistency
        warnings = check_consistency(kernel, bootstrap)

        # Build boot envelope
        envelope = build_boot_envelope(kernel, bootstrap, health, warnings)

        # Output
        if mode == "seed":
            print(format_boot_seed(envelope))
        elif mode == "json":
            import json

            print(json.dumps(envelope, indent=2))
        else:
            print(f"❌ Unknown mode: {mode}. Use 'json' or 'seed'.", file=sys.stderr)
            sys.exit(1)

        sys.exit(0)

    except FileNotFoundError as e:
        error_envelope = {"ok": False, "error": str(e), "mode": "DEGRADED"}
        if mode == "json":
            import json

            print(json.dumps(error_envelope, indent=2))
        else:
            print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


@app.command("boot-oa")
def boot_oa(
    mode: str = typer.Option("json", "--mode", help="Output mode: json|seed"),
) -> None:
    """
    Generate OA boot envelope (Phase 26.B — optional).

    Reads kernel + bootstrap and emits boot context for OA initialization.

    Example:
        pmagent handoff boot-oa --mode json

    Implementation: Deferred.
    """
    print("[TODO] pmagent boot oa not yet implemented", file=sys.stderr)
    print("       See: docs/SSOT/PHASE26_PMAGENT_BOOT_SPEC.md", file=sys.stderr)
    sys.exit(1)
