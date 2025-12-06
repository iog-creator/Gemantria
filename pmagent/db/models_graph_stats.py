#!/usr/bin/env python3
"""
Phase-3A Graph Stats DB Model — SQLAlchemy table definition for graph statistics snapshots.

Stores graph statistics metrics (nodes, edges, clusters, density, centrality) as rows
in the control schema, with one row per metric per snapshot.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, ClassVar
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Float, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for SQLAlchemy ORM models."""

    pass


class GraphStatsSnapshot(Base):
    """
    Graph statistics snapshot table.

    Stores individual metrics from graph_stats.json exports as rows.
    Each snapshot has a unique snapshot_id and timestamp.
    """

    __tablename__: ClassVar[str] = "graph_stats_snapshots"
    __table_args__: ClassVar[dict] = {"schema": "gematria"}

    # Primary key
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=func.gen_random_uuid(),
    )

    # Snapshot metadata
    snapshot_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="Groups all metrics from a single graph_stats.json import",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
        comment="When this metric row was inserted",
    )

    # Metric data
    metric_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Metric name (e.g., 'nodes', 'edges', 'density', 'centrality.avg_degree')",
    )
    metric_value: Mapped[float | int | None] = mapped_column(
        Float,
        nullable=True,
        comment="Numeric value for the metric (null for object metrics stored in metric_json)",
    )
    metric_json: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="JSON value for complex metrics (e.g., centrality object)",
    )

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<GraphStatsSnapshot(id={self.id}, snapshot_id={self.snapshot_id}, "
            f"metric_name={self.metric_name}, metric_value={self.metric_value})>"
        )
