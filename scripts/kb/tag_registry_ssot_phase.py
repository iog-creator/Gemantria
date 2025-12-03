#!/usr/bin/env python3
"""
Tag SSOT Phase Documents in KB Registry

Scans docs/SSOT/ for PHASE*.md files and ensures they're properly tagged
in the KB registry with phase + importance metadata.

This script:
1. Discovers all PHASE*.md files in docs/SSOT/
2. Extracts phase numbers (e.g., PHASE_10_4 -> phase 10.4)
3. Updates or creates registry entries with proper tags
4. Sets importance based on file name patterns (diagnostic, plan, status = high)
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

# Add project root to path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from pmagent.kb.registry import (
    KBDocument,
    KBDocumentRegistry,
    REGISTRY_PATH,
    load_registry,
    save_registry,
)

SSOT_DIR = ROOT / "docs" / "SSOT"

# Phase file pattern: PHASE[_]?(\d+)(?:_(\d+))?.*\.md
PHASE_PATTERN = re.compile(r"PHASE[_]?(\d+)(?:_(\d+))?[_.]", re.IGNORECASE)


def extract_phase_number(filename: str) -> tuple[int, int | None] | None:
    """Extract phase number from filename.
    
    Returns (phase, sub_phase) or None if not a phase file.
    Examples:
        PHASE10_WIRING.md -> (10, None)
        PHASE_14_SEMANTIC_RECORD.md -> (14, None)
        PHASE_10_4_ID_FIX.md -> (10, 4)
    """
    match = PHASE_PATTERN.match(filename.upper())
    if not match:
        return None
    phase = int(match.group(1))
    sub_phase = int(match.group(2)) if match.group(2) else None
    return (phase, sub_phase)


def determine_importance(filename: str) -> str:
    """Determine importance based on filename patterns.
    
    High importance: diagnostic, plan, status, wiring, complete, structural
    Medium: recon, spec, wave
    Low: other
    """
    filename_lower = filename.lower()
    high_keywords = [
        "diagnostic",
        "plan",
        "status",
        "wiring",
        "complete",
        "structural",
        "gap",
        "correction",
        "self_assessment",
    ]
    medium_keywords = ["recon", "spec", "wave", "alignment"]
    
    if any(kw in filename_lower for kw in high_keywords):
        return "high"
    elif any(kw in filename_lower for kw in medium_keywords):
        return "medium"
    else:
        return "low"


def discover_phase_files() -> dict[str, dict[str, Any]]:
    """Discover all PHASE*.md files in docs/SSOT/ and extract metadata."""
    phase_files = {}
    
    if not SSOT_DIR.exists():
        print(f"[tag_registry] WARNING: {SSOT_DIR} does not exist", file=sys.stderr)
        return phase_files
    
    for file_path in SSOT_DIR.glob("PHASE*.md"):
        filename = file_path.name
        rel_path = file_path.relative_to(ROOT)
        
        phase_info = extract_phase_number(filename)
        if not phase_info:
            continue
        
        phase, sub_phase = phase_info
        phase_key = f"{phase}.{sub_phase}" if sub_phase else str(phase)
        
        importance = determine_importance(filename)
        
        # Build tags
        tags = ["ssot"]
        tags.append(f"phase-{phase}")
        if sub_phase:
            tags.append(f"phase-{phase}.{sub_phase}")
        
        # Add semantic tags based on filename
        if "diagnostic" in filename.lower():
            tags.append("diagnostic")
        if "plan" in filename.lower():
            tags.append("plan")
        if "wiring" in filename.lower():
            tags.append("wiring")
        if "status" in filename.lower():
            tags.append("status")
        
        phase_files[str(rel_path)] = {
            "path": str(rel_path),
            "filename": filename,
            "phase": phase,
            "sub_phase": sub_phase,
            "phase_key": phase_key,
            "importance": importance,
            "tags": tags,
        }
    
    return phase_files


def update_registry(registry: KBDocumentRegistry, phase_files: dict[str, dict[str, Any]], dry_run: bool = False) -> int:
    """Update registry with phase file metadata."""
    updated = 0
    created = 0
    
    for rel_path, metadata in phase_files.items():
        # Generate document ID
        doc_id = f"ssot::phase-{metadata['phase_key']}::{metadata['filename'].replace('.md', '')}"
        
        # Check if document already exists
        existing = registry.get_by_path(rel_path)
        
        if existing:
            # Update existing document
            needs_update = False
            
            # Update tags if missing phase tags
            existing_tags = set(existing.tags)
            required_tags = set(metadata["tags"])
            if not required_tags.issubset(existing_tags):
                existing.tags = list(set(existing.tags) | required_tags)
                needs_update = True
            
            # Update provenance if missing phase info
            if "phase" not in existing.provenance:
                existing.provenance["phase"] = metadata["phase"]
                if metadata["sub_phase"]:
                    existing.provenance["sub_phase"] = metadata["sub_phase"]
                existing.provenance["phase_key"] = metadata["phase_key"]
                needs_update = True
            
            # Update importance if not set or lower
            if "dominant_importance" not in existing.provenance or existing.provenance.get("dominant_importance") != metadata["importance"]:
                existing.provenance["dominant_importance"] = metadata["importance"]
                needs_update = True
            
            if needs_update:
                # Note: Pydantic models are mutable, so we can update in place
                # The registry will reflect changes when saved
                updated += 1
                print(f"[tag_registry] Updated: {rel_path} (phase {metadata['phase_key']}, importance {metadata['importance']})")
        else:
            # Create new document
            doc = KBDocument(
                id=doc_id,
                title=f"SSOT: {metadata['filename']}",
                path=rel_path,
                type="ssot",
                tags=metadata["tags"],
                owning_subsystem="docs",
                provenance={
                    "phase": metadata["phase"],
                    "phase_key": metadata["phase_key"],
                    "dominant_importance": metadata["importance"],
                    "is_ssot": True,
                    "enabled": True,
                },
            )
            
            if not dry_run:
                registry.add_document(doc)
            created += 1
            print(f"[tag_registry] Created: {rel_path} (phase {metadata['phase_key']}, importance {metadata['importance']})")
    
    return updated + created


def main() -> int:
    parser = argparse.ArgumentParser(description="Tag SSOT phase documents in KB registry")
    parser.add_argument("--dry-run", action="store_true", help="Print changes without writing")
    args = parser.parse_args()
    
    # Discover phase files
    print(f"[tag_registry] Scanning {SSOT_DIR} for PHASE*.md files...")
    phase_files = discover_phase_files()
    print(f"[tag_registry] Found {len(phase_files)} phase files")
    
    if not phase_files:
        print("[tag_registry] No phase files found", file=sys.stderr)
        return 1
    
    # Load registry
    try:
        registry = load_registry()
    except FileNotFoundError:
        print(f"[tag_registry] Creating new registry at {REGISTRY_PATH}")
        registry = KBDocumentRegistry(version="1.0", documents=[])
    
    # Update registry
    count = update_registry(registry, phase_files, dry_run=args.dry_run)
    
    if args.dry_run:
        print(f"\n[tag_registry] DRY RUN: Would update/create {count} documents")
        return 0
    
    # Save registry
    if count > 0:
        save_registry(registry, allow_ci_write=False)
        print(f"\n[tag_registry] Updated registry: {count} documents tagged")
    else:
        print("\n[tag_registry] No changes needed")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

