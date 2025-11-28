"""Gematria word cache module (Phase 14 PR 14.2).

Cache gematria values in gemantria.word_cache table for performance.
Uses writable GEMATRIA_DSN (not read-only bible_db).

Governance:
- Cache location: gemantria DB (writable), NOT bible_db (read-only)
- Ketiv priority: Calculations use Ketiv (written) form
- Correctness Priority 1: Code > DB > LLM (DB seeds authoritative)
"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError

from agentpm.db.loader import DbUnavailableError, get_control_engine


@dataclass
class CachedGematriaValue:
    """A cached gematria value from gemantria.word_cache.

    Attributes:
        language: Language code ('HE' or 'GR').
        strongs_id: Strong's number (e.g., 'H430', 'G2316').
        surface_form: Surface form of the word (Ketiv for Hebrew).
        system: Gematria system name ('mispar_hechrachi', 'mispar_gadol', 'isopsephy').
        gematria_value: Calculated numeric value.
        calc_version: Algorithm version for auditability (e.g., 'v1.0').
    """

    language: str
    strongs_id: str
    surface_form: str
    system: str
    gematria_value: int
    calc_version: str


class GematriaCache:
    """Gematria value cache adapter for gemantria.word_cache table.

    This adapter provides caching for gematria calculations to improve performance.
    All operations are against the writable gemantria database.

    Attributes:
        _engine: SQLAlchemy engine (lazy-initialized).
        _db_available: Whether database is available.
    """

    def __init__(self) -> None:
        """Initialize the cache adapter (lazy engine initialization)."""
        self._engine = None
        self._db_available = False

    def _ensure_engine(self) -> bool:
        """Ensure database engine is available.

        Returns:
            True if engine is available, False if DB is off/unavailable.
        """
        if self._engine is not None:
            return self._db_available

        try:
            self._engine = get_control_engine()
            self._db_available = True
            return True
        except DbUnavailableError:
            self._db_available = False
            return False
        except (OperationalError, ProgrammingError):
            self._db_available = False
            return False

    def get(
        self, language: str, strongs_id: str, surface: str, system: str
    ) -> int | None:
        """Get cached gematria value.

        Args:
            language: Language code ('HE' or 'GR').
            strongs_id: Strong's number.
            surface: Surface form of the word (Ketiv for Hebrew).
            system: Gematria system name.

        Returns:
            Cached gematria value if found, None if not cached or DB unavailable.
        """
        if not self._ensure_engine():
            return None

        try:
            query = text(
                """
                SELECT gematria_value
                FROM gematria.word_cache
                WHERE language = :language
                  AND strongs_id = :strongs_id
                  AND surface_form = :surface_form
                  AND system = :system
                LIMIT 1
                """
            )
            with self._engine.connect() as conn:
                result = conn.execute(
                    query,
                    {
                        "language": language,
                        "strongs_id": strongs_id,
                        "surface_form": surface,
                        "system": system,
                    },
                )
                row = result.fetchone()
                return row[0] if row else None
        except (OperationalError, ProgrammingError):
            self._db_available = False
            return None

    def set(
        self,
        language: str,
        strongs_id: str,
        surface: str,
        system: str,
        value: int,
        version: str = "v1.0",
    ) -> bool:
        """Cache a gematria value.

        Uses INSERT ... ON CONFLICT DO NOTHING for idempotent upsert.

        Args:
            language: Language code ('HE' or 'GR').
            strongs_id: Strong's number.
            surface: Surface form of the word (Ketiv for Hebrew).
            system: Gematria system name.
            value: Calculated gematria value.
            version: Algorithm version (default: 'v1.0').

        Returns:
            True if value was cached, False if DB unavailable or constraint violation.
        """
        if not self._ensure_engine():
            return False

        try:
            query = text(
                """
                INSERT INTO gematria.word_cache
                    (language, strongs_id, surface_form, system, gematria_value, calc_version)
                VALUES
                    (:language, :strongs_id, :surface_form, :system, :value, :version)
                ON CONFLICT (language, strongs_id, surface_form, system)
                DO NOTHING
                """
            )
            with self._engine.connect() as conn:
                conn.execute(
                    query,
                    {
                        "language": language,
                        "strongs_id": strongs_id,
                        "surface_form": surface,
                        "system": system,
                        "value": value,
                        "version": version,
                    },
                )
                conn.commit()
                return True
        except (OperationalError, ProgrammingError):
            self._db_available = False
            return False

    def batch_populate(
        self, source: str, system: str = "mispar_hechrachi", limit: int | None = None
    ) -> dict:
        """Batch populate cache from hebrew_ot_words or greek_nt_words.

        Args:
            source: Source table ('hebrew_ot_words' or 'greek_nt_words').
            system: Gematria system to use (default: 'mispar_hechrachi').
            limit: Optional limit on number of words to process.

        Returns:
            Dict with keys: 'processed', 'cached', 'skipped', 'errors'.
        """
        if not self._ensure_engine():
            return {
                "processed": 0,
                "cached": 0,
                "skipped": 0,
                "errors": 1,
                "error_msg": "DB unavailable",
            }

        # Determine language and source table
        if source == "hebrew_ot_words":
            language = "HE"
            source_table = "bible.hebrew_ot_words"
        elif source == "greek_nt_words":
            language = "GR"
            source_table = "bible.greek_nt_words"
        else:
            return {
                "processed": 0,
                "cached": 0,
                "skipped": 0,
                "errors": 1,
                "error_msg": f"Unknown source: {source}",
            }

        # Import gematria calculation functions
        from agentpm.modules.gematria.core import gematria_value
        from src.core.ids import normalize_hebrew

        stats = {"processed": 0, "cached": 0, "skipped": 0, "errors": 0}

        try:
            # Query source table for distinct words
            query_text = f"""
                SELECT DISTINCT word_text, strongs_id
                FROM {source_table}
                WHERE word_text IS NOT NULL
                  AND word_text != ''
                  AND strongs_id IS NOT NULL
                  AND strongs_id != ''
            """
            if limit:
                query_text += f" LIMIT {limit}"

            query = text(query_text)

            with self._engine.connect() as conn:
                result = conn.execute(query)

                for row in result:
                    surface = row[0]
                    strongs = row[1]
                    stats["processed"] += 1

                    # Check if already cached
                    cached = self.get(language, strongs, surface, system)
                    if cached is not None:
                        stats["skipped"] += 1
                        continue

                    # Calculate gematria (using Ketiv form)
                    try:
                        # Normalize to get letters only (removes diacritics)
                        normalized = normalize_hebrew(surface)
                        value = gematria_value(normalized, system=system)

                        # Cache the value
                        if self.set(language, strongs, surface, system, value):
                            stats["cached"] += 1
                        else:
                            stats["errors"] += 1
                    except Exception:
                        stats["errors"] += 1
                        continue

            return stats

        except (OperationalError, ProgrammingError) as e:
            self._db_available = False
            return {
                "processed": stats["processed"],
                "cached": stats["cached"],
                "skipped": stats["skipped"],
                "errors": stats["errors"] + 1,
                "error_msg": str(e),
            }
