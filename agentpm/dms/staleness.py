#!/usr/bin/env python3
"""
DMS Phase 2: Currency & Staleness Enforcement

This module extends the existing KB metrics with database-backed lifecycle
and phase validation using the new schema from migration 053.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

try:
    import psycopg
    from psycopg.rows import dict_row

    PSYCOPG_AVAILABLE = True
except ImportError:
    PSYCOPG_AVAILABLE = False

from scripts.config.env import get_rw_dsn


@dataclass
class StalenessMetrics:
    """DMS Phase 2 staleness metrics."""

    total_docs: int
    active_docs: int
    deprecated_docs: int
    archived_docs: int
    draft_docs: int

    # Age-based staleness
    docs_over_90_days: int
    docs_over_180_days: int

    # Phase-based staleness
    current_phase: int | None
    docs_for_old_phases: int  # Docs for phases < current - 1
    phase_misaligned_docs: list[dict[str, Any]]

    # Deprecated tracking
    deprecated_needs_archive: int  # Deprecated >30 days

    # Canonical tracking
    canonical_docs: int
    topics_with_multiple_canonicals: list[str]

    # Warnings
    warnings: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "lifecycle_breakdown": {
                "total": self.total_docs,
                "active": self.active_docs,
                "deprecated": self.deprecated_docs,
                "archived": self.archived_docs,
                "draft": self.draft_docs,
            },
            "age_staleness": {
                "over_90_days": self.docs_over_90_days,
                "over_180_days": self.docs_over_180_days,
            },
            "phase_currency": {
                "current_phase": self.current_phase,
                "docs_for_old_phases": self.docs_for_old_phases,
                "phase_misaligned": self.phase_misaligned_docs,
            },
            "deprecated_tracking": {
                "count": self.deprecated_docs,
                "needs_archive_count": self.deprecated_needs_archive,
            },
            "canonical_tracking": {
                "canonical_docs": self.canonical_docs,
                "topics_with_duplicates": self.topics_with_multiple_canonicals,
            },
            "warnings": self.warnings,
        }


def get_current_phase_from_master_plan() -> int | None:
    """Extract current phase number from MASTER_PLAN.md."""
    try:
        from pathlib import Path
        import re

        repo_root = Path(__file__).resolve().parents[2]
        master_plan = repo_root / "docs" / "SSOT" / "MASTER_PLAN.md"

        if not master_plan.exists():
            return None

        content = master_plan.read_text()

        # Look for "Current phase: 12" or similar patterns
        match = re.search(r"current.*phase[:\s]+(\d+)", content, re.IGNORECASE)
        if match:
            return int(match.group(1))

        # Alternative: look for highest phase mentioned
        phases = re.findall(r"phase[:\s]*(\d+)", content, re.IGNORECASE)
        if phases:
            return max(int(p) for p in phases)

        return None
    except Exception:
        return None


def compute_dms_staleness_metrics() -> dict[str, Any]:
    """Compute DMS Phase 2 staleness metrics from database.

    Returns:
        Dictionary with staleness metrics:
        {
            "available": bool,
            "source": "database" | "error",
            "metrics": StalenessMetrics.to_dict()
        }
    """
    if not PSYCOPG_AVAILABLE:
        return {
            "available": False,
            "source": "error",
            "error": "psycopg not available",
        }

    dsn = get_rw_dsn()
    if not dsn:
        return {
            "available": False,
            "source": "error",
            "error": "ATLAS_DSN_RW not configured",
        }

    warnings = []

    try:
        conn = psycopg.connect(dsn)
        cur = conn.cursor(row_factory=dict_row)

        # Get total count first
        cur.execute("SELECT COUNT(*) as total FROM control.kb_document")
        total_row = cur.fetchone()
        total_docs = total_row["total"] if total_row else 0

        # Check if new columns exist by trying to query them
        try:
            cur.execute("SELECT lifecycle_stage FROM control.kb_document LIMIT 1")
            has_lifecycle = True
        except Exception:
            has_lifecycle = False
            conn.rollback()

        if not has_lifecycle:
            # Migration 053 not applied yet - return minimal metrics
            warnings.append("Migration 053 (DMS lifecycle) not yet applied - using basic metrics only")

            # Get age-based staleness using mtime (existing column)
            cur.execute("""
                SELECT 
                    COUNT(*) FILTER (WHERE mtime < now() - interval '90 days') as over_90,
                    COUNT(*) FILTER (WHERE mtime < now() - interval '180 days') as over_180
                FROM control.kb_document
            """)
            age_row = cur.fetchone()
            docs_over_90 = age_row["over_90"] if age_row else 0
            docs_over_180 = age_row["over_180"] if age_row else 0

            # Get canonical count (is_canonical exists)
            cur.execute("SELECT COUNT(*) as count FROM control.kb_document WHERE is_canonical = true")
            canonical_row = cur.fetchone()
            canonical_docs = canonical_row["count"] if canonical_row else 0

            cur.close()
            conn.close()

            metrics = StalenessMetrics(
                total_docs=total_docs,
                active_docs=total_docs,  # Assume all active if no lifecycle
                deprecated_docs=0,
                archived_docs=0,
                draft_docs=0,
                docs_over_90_days=docs_over_90,
                docs_over_180_days=docs_over_180,
                current_phase=get_current_phase_from_master_plan(),
                docs_for_old_phases=0,
                phase_misaligned_docs=[],
                deprecated_needs_archive=0,
                canonical_docs=canonical_docs,
                topics_with_multiple_canonicals=[],
                warnings=warnings,
            )

            return {
                "available": True,
                "source": "database_partial",
                "metrics": metrics.to_dict(),
            }

        # Full Phase 2 metrics (migration 053 applied)
        cur.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE lifecycle_stage = 'active') as active,
                COUNT(*) FILTER (WHERE lifecycle_stage = 'deprecated') as deprecated,
                COUNT(*) FILTER (WHERE lifecycle_stage = 'archived') as archived,
                COUNT(*) FILTER (WHERE lifecycle_stage = 'draft') as draft
            FROM control.kb_document
        """)
        lifecycle_row = cur.fetchone()

        active_docs = lifecycle_row["active"] if lifecycle_row else 0
        deprecated_docs = lifecycle_row["deprecated"] if lifecycle_row else 0
        archived_docs = lifecycle_row["archived"] if lifecycle_row else 0
        draft_docs = lifecycle_row["draft"] if lifecycle_row else 0

        # Get age-based staleness using mtime
        cur.execute("""
            SELECT 
                COUNT(*) FILTER (WHERE mtime < now() - interval '90 days') as over_90,
                COUNT(*) FILTER (WHERE mtime < now() - interval '180 days') as over_180
            FROM control.kb_document
            WHERE lifecycle_stage = 'active'
        """)
        age_row = cur.fetchone()
        docs_over_90 = age_row["over_90"] if age_row else 0
        docs_over_180 = age_row["over_180"] if age_row else 0

        # Get current phase
        current_phase = get_current_phase_from_master_plan()

        # Phase-based staleness
        phase_misaligned_docs = []
        docs_for_old_phases = 0

        if current_phase is not None:
            # Find docs for phases older than current - 1
            cur.execute(
                """
                SELECT id, path, phase_number, lifecycle_stage
                FROM control.kb_document
                WHERE phase_number IS NOT NULL
                  AND phase_number < %s
                  AND lifecycle_stage IN ('active', 'draft')
            """,
                (current_phase - 1,),
            )

            old_phase_docs = cur.fetchall()
            docs_for_old_phases = len(old_phase_docs)

            for doc in old_phase_docs:
                phase_misaligned_docs.append(
                    {
                        "id": str(doc["id"]),
                        "path": doc["path"],
                        "phase": doc["phase_number"],
                        "current_phase": current_phase,
                        "lifecycle": doc["lifecycle_stage"],
                    }
                )

            if docs_for_old_phases > 0:
                warnings.append(
                    f"{docs_for_old_phases} doc(s) are for old phases (< Phase {current_phase - 1}) but still active"
                )

        # Deprecated docs needing archive (deprecated >30 days)
        cur.execute("""
            SELECT COUNT(*) as cnt
            FROM control.kb_document
            WHERE lifecycle_stage = 'deprecated'
              AND deprecated_at < now() - interval '30 days'
        """)
        result = cur.fetchone()
        deprecated_needs_archive = result["cnt"] if result else 0

        if deprecated_needs_archive > 0:
            warnings.append(f"{deprecated_needs_archive} deprecated doc(s) older than 30 days should be archived")

        # Canonical tracking
        cur.execute("""
            SELECT COUNT(*) as cnt
            FROM control.kb_document
            WHERE is_canonical = true
              AND lifecycle_stage = 'active'
        """)
        result = cur.fetchone()
        canonical_docs = result["cnt"] if result else 0

        # Find topics with multiple canonicals (violation)
        cur.execute("""
            SELECT topic_key, COUNT(*) as count
            FROM control.kb_document
            WHERE is_canonical = true
              AND lifecycle_stage = 'active'
              AND topic_key IS NOT NULL
            GROUP BY topic_key
            HAVING COUNT(*) > 1
        """)

        duplicate_canonicals = [row["topic_key"] for row in cur.fetchall()]

        if duplicate_canonicals:
            warnings.append(
                f"{len(duplicate_canonicals)} topic(s) have multiple canonical docs: {', '.join(duplicate_canonicals)}"
            )

        cur.close()
        conn.close()

        metrics = StalenessMetrics(
            total_docs=total_docs,
            active_docs=active_docs,
            deprecated_docs=deprecated_docs,
            archived_docs=archived_docs,
            draft_docs=draft_docs,
            docs_over_90_days=docs_over_90,
            docs_over_180_days=docs_over_180,
            current_phase=current_phase,
            docs_for_old_phases=docs_for_old_phases,
            phase_misaligned_docs=phase_misaligned_docs,
            deprecated_needs_archive=deprecated_needs_archive,
            canonical_docs=canonical_docs,
            topics_with_multiple_canonicals=duplicate_canonicals,
            warnings=warnings,
        )

        return {
            "available": True,
            "source": "database",
            "metrics": metrics.to_dict(),
        }

    except Exception as e:
        return {
            "available": False,
            "source": "error",
            "error": f"Failed to compute staleness metrics: {e!s}",
        }
