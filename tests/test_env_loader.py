import os
from contextlib import contextmanager
from importlib import reload
import scripts.config.env as env


@contextmanager
def temp_env(**pairs):
    # Save all DSN-related env vars
    dsn_keys = ["ATLAS_DSN_RW", "GEMATRIA_DSN", "ATLAS_DSN", "BIBLE_DB_DSN"]
    old = {k: os.environ.get(k) for k in dsn_keys}
    try:
        # Clear all DSN env vars first to avoid .env interference
        for k in dsn_keys:
            os.environ.pop(k, None)
        # Set only the ones we want
        for k, v in pairs.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        # Force reload to clear cached values
        if hasattr(env, "_LOADED"):
            env._LOADED = False
        reload(env)
        yield
    finally:
        # Restore original values
        for k in dsn_keys:
            os.environ.pop(k, None)
        for k, v in old.items():
            if v is not None:
                os.environ[k] = v
        # Force reload
        if hasattr(env, "_LOADED"):
            env._LOADED = False
        reload(env)


def test_rw_precedence_prefers_atlas_dsn_rw():
    """ATLAS_DSN_RW takes precedence over GEMATRIA_DSN."""
    with temp_env(ATLAS_DSN_RW="postgresql://u:p@h:5432/atlasrw", GEMATRIA_DSN="postgresql://u:p@h:5432/gem"):
        assert env.get_rw_dsn() == "postgresql://u:p@h:5432/atlasrw"


def test_rw_precedence_falls_back_to_gematria_dsn():
    """GEMATRIA_DSN is used when ATLAS_DSN_RW is not set."""
    with temp_env(ATLAS_DSN_RW=None, GEMATRIA_DSN="postgresql://u:p@h:5432/gem"):
        assert env.get_rw_dsn() == "postgresql://u:p@h:5432/gem"


def test_ro_precedence_prefers_atlas_dsn():
    """ATLAS_DSN takes precedence over RW fallback."""
    with temp_env(
        ATLAS_DSN="postgresql://u:p@h:5432/atlasro", ATLAS_DSN_RW=None, GEMATRIA_DSN="postgresql://u:p@h:5432/gem"
    ):
        assert env.get_ro_dsn() == "postgresql://u:p@h:5432/atlasro"


def test_ro_precedence_falls_back_to_rw():
    """RO falls back to RW when ATLAS_DSN is not set."""
    with temp_env(ATLAS_DSN=None, ATLAS_DSN_RW=None, GEMATRIA_DSN="postgresql://u:p@h:5432/gem"):
        assert env.get_ro_dsn() == "postgresql://u:p@h:5432/gem"


def test_bible_db_dsn():
    """BIBLE_DB_DSN is returned directly."""
    with temp_env(BIBLE_DB_DSN="postgresql://u:p@h:5432/bible"):
        assert env.get_bible_db_dsn() == "postgresql://u:p@h:5432/bible"


def test_bible_db_dsn_none_when_unset():
    """BIBLE_DB_DSN returns None when not set."""
    with temp_env(BIBLE_DB_DSN=None):
        assert env.get_bible_db_dsn() is None
