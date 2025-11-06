#!/usr/bin/env python3
"""
Unified UI envelope generator.

Creates a unified envelope with schema, books, artifacts, evidence (sha256_12),
and model manifest for UI consumption.

Usage:
    python scripts/create_ui_envelope.py --output exports/ui_envelope.json

Related Rules: Rule-039 (Execution Contract), Rule-022 (Visualization Contract Sync)
Related ADRs: ADR-019 (Data Contracts), ADR-023 (Visualization API Spec)
"""

import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from src.infra.env_loader import ensure_env_loaded
from src.infra.runs_ledger import get_model_versions, get_schema_version

# Load environment
ensure_env_loaded()


def load_artifact(file_path: Path) -> dict[str, Any] | None:
    """Load an artifact file if it exists."""
    if not file_path.exists():
        return None
    try:
        content = file_path.read_text(encoding="utf-8")
        return json.loads(content)
    except Exception:
        return None


def compute_sha256_12_for_file(file_path: Path) -> str | None:
    """Compute sha256_12 hash for a file."""
    if not file_path.exists():
        return None
    try:
        content = file_path.read_bytes()
        return hashlib.sha256(content).hexdigest()[:12]
    except Exception:
        return None


def create_unified_envelope(
    books: list[str] | None = None,
    output_path: Path | None = None,
    include_artifacts: bool = True,
) -> dict[str, Any]:
    """
    Create unified UI envelope with all artifacts and evidence.

    Args:
        books: List of books processed (or None to infer from exports)
        output_path: Optional output path for the envelope
        include_artifacts: Whether to include full artifact data

    Returns:
        Unified envelope dictionary
    """
    exports_dir = Path("exports")
    share_dir = Path("share/exports")

    # Collect all artifacts
    artifacts = {}
    evidence = []

    # Graph data
    graph_file = exports_dir / "graph_latest.json"
    if graph_file.exists():
        graph_data = load_artifact(graph_file)
        if graph_data:
            artifacts["graph"] = graph_data if include_artifacts else {"path": str(graph_file)}
            sha256_12 = compute_sha256_12_for_file(graph_file)
            if sha256_12:
                evidence.append({"type": "graph", "sha256_12": sha256_12})

    # Stats
    stats_file = exports_dir / "graph_stats.json"
    if stats_file.exists():
        stats_data = load_artifact(stats_file)
        if stats_data:
            artifacts["stats"] = stats_data if include_artifacts else {"path": str(stats_file)}
            sha256_12 = compute_sha256_12_for_file(stats_file)
            if sha256_12:
                evidence.append({"type": "stats", "sha256_12": sha256_12})

    # Patterns
    patterns_file = share_dir / "graph_patterns.json"
    if patterns_file.exists():
        patterns_data = load_artifact(patterns_file)
        if patterns_data:
            artifacts["patterns"] = patterns_data if include_artifacts else {"path": str(patterns_file)}
            sha256_12 = compute_sha256_12_for_file(patterns_file)
            if sha256_12:
                evidence.append({"type": "patterns", "sha256_12": sha256_12})

    # Temporal patterns
    temporal_file = share_dir / "temporal_patterns.json"
    if temporal_file.exists():
        temporal_data = load_artifact(temporal_file)
        if temporal_data:
            artifacts["temporal"] = temporal_data if include_artifacts else {"path": str(temporal_file)}
            sha256_12 = compute_sha256_12_for_file(temporal_file)
            if sha256_12:
                evidence.append({"type": "temporal", "sha256_12": sha256_12})

    # Forecast
    forecast_file = share_dir / "pattern_forecast.json"
    if forecast_file.exists():
        forecast_data = load_artifact(forecast_file)
        if forecast_data:
            artifacts["forecast"] = forecast_data if include_artifacts else {"path": str(forecast_file)}
            sha256_12 = compute_sha256_12_for_file(forecast_file)
            if sha256_12:
                evidence.append({"type": "forecast", "sha256_12": sha256_12})

    # Edge class counts
    edge_counts_file = Path("share/eval/edges/edge_class_counts.json")
    if edge_counts_file.exists():
        edge_counts_data = load_artifact(edge_counts_file)
        if edge_counts_data:
            artifacts["edge_counts"] = edge_counts_data if include_artifacts else {"path": str(edge_counts_file)}

    # Infer books from graph if not provided
    if not books:
        if "graph" in artifacts:
            graph = artifacts["graph"] if include_artifacts else load_artifact(graph_file)
            if graph:
                # Try to extract books from graph metadata or nodes
                nodes = graph.get("nodes", [])
                books_set = set()
                for node in nodes:
                    if "book" in node:
                        books_set.add(node["book"])
                books = list(books_set) if books_set else ["unknown"]

    # Get model versions
    models_used = get_model_versions()

    # Create envelope
    envelope = {
        "schema": "gemantria/ui-envelope.v1",
        "book" if len(books) == 1 else "books": books[0] if len(books) == 1 else books,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "artifacts": artifacts,
        "evidence": {
            "models_used": models_used,
            "sha256_12": evidence,
        },
        "schema_version": get_schema_version(),
    }

    # Write to output if specified
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(envelope, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Unified envelope written to {output_path}")

    return envelope


def generate_model_manifest() -> dict[str, Any]:
    """Generate MODEL_MANIFEST.json excerpt with version stamps."""
    import subprocess

    models = get_model_versions()
    schema_version = get_schema_version()

    # Get git version info for release automation
    git_version = "unknown"
    git_commit = "unknown"
    git_branch = "unknown"
    try:
        git_version = subprocess.check_output(["git", "describe", "--tags", "--dirty", "--always"], text=True).strip()
        git_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
        git_branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], text=True).strip()
    except Exception:
        pass

    manifest = {
        "schema": "gemantria/model-manifest.v1",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "models": models,
        "schema_version": schema_version,
        "git": {
            "version": git_version,
            "commit": git_commit,
            "branch": git_branch,
        },
    }

    manifest_file = Path("exports/MODEL_MANIFEST.json")
    manifest_file.parent.mkdir(parents=True, exist_ok=True)
    manifest_file.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Model manifest written to {manifest_file}")

    return manifest


def generate_report_md(envelope: dict[str, Any]) -> str:
    """Generate machine-first Markdown report with version stamps."""
    import subprocess

    books = envelope.get("book") or envelope.get("books", [])
    if isinstance(books, str):
        books = [books]

    artifacts = envelope.get("artifacts", {})
    evidence = envelope.get("evidence", {})

    # Get git version info for release automation
    git_version = "unknown"
    git_commit = "unknown"
    try:
        git_version = subprocess.check_output(["git", "describe", "--tags", "--dirty", "--always"], text=True).strip()
        git_commit = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
    except Exception:
        pass

    report = f"""# Gemantria Pipeline Report

**Generated:** {envelope.get("generated_at")}
**Schema:** {envelope.get("schema")}
**Schema Version:** {envelope.get("schema_version")}
**Git Version:** {git_version}
**Git Commit:** {git_commit}

## Books Processed

{chr(10).join(f"- {book}" for book in books)}

## Artifacts

"""
    for artifact_type, artifact_data in artifacts.items():
        if isinstance(artifact_data, dict) and "path" in artifact_data:
            report += f"- **{artifact_type}**: {artifact_data['path']}\n"
        elif isinstance(artifact_data, dict):
            # Check for version stamps in artifact
            version_info = ""
            if "schema_version" in artifact_data:
                version_info += f" (schema: {artifact_data['schema_version']})"
            if "export_timestamp" in artifact_data:
                version_info += f" (exported: {artifact_data['export_timestamp']})"
            report += f"- **{artifact_type}**: Present{version_info}\n"
        else:
            report += f"- **{artifact_type}**: Present\n"

    report += """
## Evidence

**Models Used:**
"""
    for model_name, model_version in evidence.get("models_used", {}).items():
        report += f"- {model_name}: {model_version}\n"

    report += "\n**Artifact Hashes (sha256_12):**\n"
    for item in evidence.get("sha256_12", []):
        report += f"- {item['type']}: {item['sha256_12']}\n"

    # Add summary statistics if available
    if "stats" in artifacts:
        stats = artifacts["stats"] if isinstance(artifacts["stats"], dict) else {}
        if isinstance(stats, dict):
            report += "\n## Summary Statistics\n\n"
            if "nodes" in stats:
                report += f"- **Nodes:** {stats['nodes']}\n"
            if "edges" in stats:
                report += f"- **Edges:** {stats['edges']}\n"
            if "clusters" in stats:
                report += f"- **Clusters:** {stats['clusters']}\n"
            if "density" in stats:
                report += f"- **Density:** {stats['density']:.4f}\n"

    return report


def main():
    parser = argparse.ArgumentParser(description="Create unified UI envelope")
    parser.add_argument("--output", default="exports/ui_envelope.json", help="Output envelope file path")
    parser.add_argument("--books", help="Comma-separated list of books")
    parser.add_argument("--include-artifacts", action="store_true", help="Include full artifact data in envelope")
    parser.add_argument("--report", help="Output report.md file path")

    args = parser.parse_args()

    books = [b.strip() for b in args.books.split(",")] if args.books else None

    # Create envelope
    envelope = create_unified_envelope(
        books=books,
        output_path=Path(args.output),
        include_artifacts=args.include_artifacts,
    )

    # Generate model manifest
    generate_model_manifest()

    # Generate report if requested
    if args.report:
        report = generate_report_md(envelope)
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report, encoding="utf-8")
        print(f"Report written to {report_path}")
    else:
        # Print report to stdout
        report = generate_report_md(envelope)
        print("\n" + "=" * 60)
        print(report)
        print("=" * 60)


if __name__ == "__main__":
    main()
