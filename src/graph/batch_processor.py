from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from src.graph.nodes.validation import validate_noun

__all__ = [
    "BatchAbortError",
    "BatchConfig",
    "BatchProcessor",
    "BatchResult",
    "process_batch",
]

DEFAULT_BATCH_SIZE = 50


@dataclass
class BatchConfig:
    batch_size: int = DEFAULT_BATCH_SIZE
    allow_partial: bool = False
    partial_reason: str | None = None

    @classmethod
    def from_env(cls) -> BatchConfig:
        """Load configuration from environment variables."""
        batch_size = int(os.getenv("BATCH_SIZE", DEFAULT_BATCH_SIZE))
        allow_partial_str = os.getenv("ALLOW_PARTIAL", "0")
        allow_partial = allow_partial_str.strip().lower() in {"1", "true", "yes"}
        partial_reason = os.getenv("PARTIAL_REASON", "").strip() or None

        return cls(
            batch_size=batch_size,
            allow_partial=allow_partial,
            partial_reason=partial_reason,
        )


@dataclass
class BatchResult:
    batch_id: str
    config: BatchConfig
    nouns_processed: int
    results: list[dict[str, Any]]
    manifest: dict[str, Any]
    created_at: datetime

    def to_dict(self) -> dict[str, Any]:
        return {
            "batch_id": self.batch_id,
            "config": {
                "batch_size": self.config.batch_size,
                "allow_partial": self.config.allow_partial,
                "partial_reason": self.config.partial_reason,
            },
            "nouns_processed": self.nouns_processed,
            "results": self.results,
            "manifest": self.manifest,
            "created_at": self.created_at.isoformat(),
        }


class BatchAbortError(RuntimeError):
    """Raised when batch processing is aborted due to insufficient nouns."""

    def __init__(self, nouns_available: int, batch_size: int, review_file: Path):
        self.nouns_available = nouns_available
        self.batch_size = batch_size
        self.review_file = review_file
        super().__init__(
            f"Insufficient nouns for batch: {nouns_available}/{batch_size}. "
            f"Review written to {review_file}. "
            f"Set ALLOW_PARTIAL=1 to override."
        )


class BatchProcessor:
    def __init__(self, config: BatchConfig | None = None):
        self.config = config or BatchConfig.from_env()

    def validate_batch_size(self, nouns: list[dict] | list[str]) -> None:
        """Validate that we have enough nouns for processing."""
        n = len(nouns)
        if n < self.config.batch_size:
            if self.config.allow_partial:
                # Log-but-allow; downstream guards keep SSOT integrity (AGENTS.md batch rules)
                print(
                    f"HINT: proceeding with partial batch {n}/{self.config.batch_size} "
                    f"(ALLOW_PARTIAL=1 reason={self.config.partial_reason!r})"
                )
                return
            raise BatchAbortError(n, self.config.batch_size, Path("review.ndjson"))

    def process_nouns(self, nouns: list[dict] | list[str]) -> BatchResult:
        """Process a batch of nouns through validation pipeline."""
        self.validate_batch_size(nouns)

        batch_id = self._generate_batch_id(nouns)
        results = []
        processed_count = 0

        for noun in nouns:
            try:
                result = validate_noun(noun)
                results.append(result)
                processed_count += 1
            except Exception as e:
                # Log error but continue processing
                results.append(
                    {
                        "surface": noun,
                        "error": str(e),
                        "gematria": None,
                        "db": None,
                        "llm": None,
                    }
                )

        manifest = self._create_manifest(batch_id, nouns, results)

        return BatchResult(
            batch_id=batch_id,
            config=self.config,
            nouns_processed=processed_count,
            results=results,
            manifest=manifest,
            created_at=datetime.now(UTC),
        )

    def _generate_batch_id(self, nouns: list[dict] | list[str]) -> str:
        """Generate a deterministic batch ID based on noun content."""
        combined_hash = hashlib.sha256()
        # Sort nouns deterministically - handle both dict and str types
        if nouns and isinstance(nouns[0], dict):
            # For dict nouns, sort by surface/hebrew field
            def sort_key(n):
                return n.get("surface", n.get("hebrew", str(n)))

            sorted_nouns = sorted(nouns, key=sort_key)
        else:
            # For string nouns, sort directly
            sorted_nouns = sorted(nouns)

        for noun in sorted_nouns:
            if isinstance(noun, dict):
                # Convert dict to stable string representation
                noun_str = json.dumps(noun, sort_keys=True, ensure_ascii=False)
            else:
                noun_str = str(noun)
            combined_hash.update(noun_str.encode("utf-8"))
        return combined_hash.hexdigest()[:16]  # Short ID for readability

    def _create_manifest(
        self, batch_id: str, input_nouns: list[dict] | list[str], results: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Create manifest with hash proofs and processing metadata."""
        input_hashes = []
        for noun in input_nouns:
            if isinstance(noun, dict):
                noun_str = json.dumps(noun, sort_keys=True, ensure_ascii=False)
            else:
                noun_str = str(noun)
            input_hashes.append(hashlib.sha256(noun_str.encode("utf-8")).hexdigest())
        result_hashes = [hashlib.sha256(json.dumps(r, sort_keys=True).encode("utf-8")).hexdigest() for r in results]  # noqa: E501

        return {
            "batch_id": batch_id,
            "input_count": len(input_nouns),
            "processed_count": len(results),
            "input_hashes": input_hashes,
            "result_hashes": result_hashes,
            "allow_partial": self.config.allow_partial,
            "partial_reason": self.config.partial_reason,
            "batch_size": self.config.batch_size,
            "validation": "deterministic_hash_proof",
        }


def process_batch(nouns: list[str], config: BatchConfig | None = None) -> BatchResult:
    """Convenience function for batch processing."""
    processor = BatchProcessor(config)
    return processor.process_nouns(nouns)
