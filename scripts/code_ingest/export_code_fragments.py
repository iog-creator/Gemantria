#!/usr/bin/env python3
"""
Layer 4 Phase 5: Export Code Fragments to Control-Plane

Exports code fragments and 1024-D embeddings to control-plane tables:
- control.doc_registry (code files)
- control.doc_version (file versions)
- control.doc_fragment (code fragments)
- control.doc_embedding (1024-D vectors)
"""

import json
import hashlib
import sys
from pathlib import Path

from sqlalchemy import text
from pmagent.db.loader import get_control_engine

# Assuming REPO_ROOT is defined elsewhere or can be derived
REPO_ROOT = Path(__file__).resolve().parents[2]


def compute_sha256(content: str) -> str:
    """Compute SHA-256 hash of content."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def export_fragments_to_db(
    input_path: str = "share/code_fragments_embedded.json",
    model_name: str = "code-embedding-hash-1024",
    project_id: int = 1,  # Default project_id
    dry_run: bool = False,
) -> None:
    """
    Export code fragments and embeddings to control-plane database.

    Args:
        input_path: Path to embedded fragments JSON
        model_name: Model name for embeddings
        project_id: Project ID for fragments
        dry_run: If True, print summary without writing to DB
    """
    with open(input_path) as f:
        data = json.load(f)
    fragments_data = data["fragments"]

    if dry_run:
        print(f"[DRY-RUN] Would export {len(fragments_data)} fragments", file=sys.stderr)
        unique_files = len(set(f.get("file_path", "") for f in fragments_data))
        print(f"[DRY-RUN] From {unique_files} unique files", file=sys.stderr)
        return

    engine = get_control_engine()
    with engine.connect() as conn:
        # 1. Register code files in control.doc_registry
        # Group fragments by file_path to get unique files
        unique_files = {}
        for frag in fragments_data:
            file_path = frag["file_path"]
            if file_path not in unique_files:
                # Read file content to compute hash
                full_path = REPO_ROOT / file_path
                if not full_path.exists():
                    print(f"[WARN] Skipping missing file: {file_path}", file=sys.stderr)
                    continue

                file_content = full_path.read_text(encoding="utf-8")
                content_hash = compute_sha256(file_content)

                unique_files[file_path] = {
                    "logical_name": f"CODE::{file_path}",
                    "repo_path": file_path,
                    "doc_role": "code_module",  # Or 'cli_script', 'ui_component' based on classification
                    "is_ssot": True,
                    "enabled": True,
                    "content_hash": content_hash,
                    "size_bytes": len(file_content.encode("utf-8")),
                }

        doc_id_map = {}  # Map repo_path to doc_id
        version_id_map = {}  # Map doc_id to version_id

        for file_path, file_meta in unique_files.items():
            # Upsert into doc_registry (check if exists first, then insert or update)
            result = conn.execute(
                text("""
                    SELECT doc_id FROM control.doc_registry
                    WHERE repo_path = :repo_path
                """),
                {"repo_path": file_meta["repo_path"]},
            ).fetchone()

            if result:
                doc_id = result[0]
                # Update existing
                conn.execute(
                    text("""
                        UPDATE control.doc_registry
                        SET logical_name = :logical_name,
                            role = :doc_role,
                            is_ssot = :is_ssot,
                            enabled = :enabled,
                            updated_at = NOW()
                        WHERE doc_id = :doc_id
                    """),
                    {
                        "doc_id": doc_id,
                        "logical_name": file_meta["logical_name"],
                        "doc_role": file_meta["doc_role"],
                        "is_ssot": file_meta["is_ssot"],
                        "enabled": file_meta["enabled"],
                    },
                )
            else:
                # Insert new
                result = conn.execute(
                    text("""
                        INSERT INTO control.doc_registry (doc_id, logical_name, repo_path, role, is_ssot, enabled)
                        VALUES (gen_random_uuid(), :logical_name, :repo_path, :doc_role, :is_ssot, :enabled)
                        RETURNING doc_id
                    """),
                    {
                        "logical_name": file_meta["logical_name"],
                        "repo_path": file_meta["repo_path"],
                        "doc_role": file_meta["doc_role"],
                        "is_ssot": file_meta["is_ssot"],
                        "enabled": file_meta["enabled"],
                    },
                ).fetchone()
                doc_id = result[0]

            doc_id_map[file_path] = doc_id

            # Insert into doc_version (check if exists first, then insert or retrieve)
            version_result = conn.execute(
                text("""
                    SELECT id FROM control.doc_version
                    WHERE doc_id = :doc_id AND content_hash = :content_hash
                """),
                {
                    "doc_id": doc_id,
                    "content_hash": file_meta["content_hash"],
                },
            ).fetchone()

            if version_result:
                version_id = version_result[0]
            else:
                # Insert new version
                version_result = conn.execute(
                    text("""
                        INSERT INTO control.doc_version (doc_id, content_hash, size_bytes)
                        VALUES (:doc_id, :content_hash, :size_bytes)
                        RETURNING id
                    """),
                    {
                        "doc_id": doc_id,
                        "content_hash": file_meta["content_hash"],
                        "size_bytes": file_meta["size_bytes"],
                    },
                ).fetchone()
                version_id = version_result[0] if version_result else None

            if version_id:
                version_id_map[doc_id] = version_id

        # 2. Export fragments and embeddings
        exported_fragments = 0
        exported_embeddings = 0

        for frag in fragments_data:
            file_path = frag["file_path"]
            doc_id = doc_id_map.get(file_path)
            version_id = version_id_map.get(doc_id) if doc_id else None

            if not doc_id or not version_id:
                print(
                    f"[WARN] Skipping fragment for {file_path} due to missing doc_id or version_id",
                    file=sys.stderr,
                )
                continue

            # Insert into control.doc_fragment (check if exists first, then insert or update)
            fragment_check = conn.execute(
                text("""
                    SELECT id FROM control.doc_fragment
                    WHERE doc_id = :doc_id AND version_id = :version_id AND fragment_index = :fragment_index
                """),
                {
                    "doc_id": doc_id,
                    "version_id": version_id,
                    "fragment_index": frag["start_line"],  # Using start_line as index
                },
            ).fetchone()

            if fragment_check:
                fragment_id = fragment_check[0]
                # Update existing
                conn.execute(
                    text("""
                        UPDATE control.doc_fragment
                        SET fragment_type = :fragment_type,
                            content = :content,
                            updated_at = NOW()
                        WHERE id = :fragment_id
                    """),
                    {
                        "fragment_id": fragment_id,
                        "fragment_type": frag["type"].lower(),
                        "content": frag["content"],
                    },
                )
            else:
                # Insert new
                fragment_result = conn.execute(
                    text("""
                        INSERT INTO control.doc_fragment (
                            doc_id, version_id, fragment_index, fragment_type, content
                        )
                        VALUES (
                            :doc_id, :version_id, :fragment_index, :fragment_type, :content
                        )
                        RETURNING id
                    """),
                    {
                        "doc_id": doc_id,
                        "version_id": version_id,
                        "fragment_index": frag["start_line"],  # Using start_line as index
                        "fragment_type": frag["type"].lower(),
                        "content": frag["content"],
                    },
                ).fetchone()
                fragment_id = fragment_result[0]

            exported_fragments += 1

            # Insert into control.doc_embedding
            embedding_list = frag["embedding"]
            # Verify dimension (should already be 1024)
            if len(embedding_list) != 1024:
                print(
                    f"[ERROR] Fragment {fragment_id} has invalid embedding dimension: {len(embedding_list)} (expected 1024)",
                    file=sys.stderr,
                )
                continue

            embedding_json = json.dumps(embedding_list)

            conn.execute(
                text("""
                    INSERT INTO control.doc_embedding (fragment_id, model_name, embedding)
                    VALUES (:fragment_id, :model_name, CAST(:embedding AS vector))
                    ON CONFLICT (fragment_id, model_name) DO UPDATE SET
                        embedding = EXCLUDED.embedding
                """),
                {
                    "fragment_id": fragment_id,
                    "model_name": model_name,
                    "embedding": embedding_json,
                },
            )
            exported_embeddings += 1

        conn.commit()
        print(
            f"Exported {exported_fragments} fragments and {exported_embeddings} embeddings",
            file=sys.stderr,
        )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Export code fragments and embeddings to control-plane DB.")
    parser.add_argument("--dry-run", action="store_true", help="Perform a dry run without writing to DB.")
    parser.add_argument("--project-id", type=int, default=1, help="Project ID for the fragments.")
    parser.add_argument(
        "--model-name",
        type=str,
        default="code-embedding-hash-1024",
        help="Model name for embeddings.",
    )
    args = parser.parse_args()

    export_fragments_to_db(
        dry_run=args.dry_run,
        project_id=args.project_id,
        model_name=args.model_name,
    )
