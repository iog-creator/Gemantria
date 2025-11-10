import os

os.environ["DISABLE_DOTENV"] = "1"
from contextlib import contextmanager
from importlib import reload
import scripts.config.env as env


@contextmanager
def temp_env(**pairs):
    # Save all DSN-related env vars
    dsn_keys = [
        "GEMATRIA_DSN",
        "RW_DSN",
        "AI_AUTOMATION_DSN",
        "ATLAS_DSN_RW",
        "ATLAS_DSN",
        "BIBLE_RO_DSN",
        "RO_DSN",
        "ATLAS_DSN_RO",
        "BIBLE_DB_DSN",
    ]
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


def test_rw_precedence_prefers_gematria_dsn():
    """GEMATRIA_DSN takes precedence over RW_DSN."""
    with temp_env(
        GEMATRIA_DSN="postgresql://u:p@h:5432/gem",
        RW_DSN="postgresql://u:p@h:5432/rw",
        AI_AUTOMATION_DSN=None,
        ATLAS_DSN_RW=None,
        ATLAS_DSN=None,
    ):
        assert env.get_rw_dsn() == "postgresql://u:p@h:5432/gem"


def test_rw_precedence_falls_back_to_rw_dsn():
    """RW_DSN is used when GEMATRIA_DSN is not set."""
    with temp_env(
        GEMATRIA_DSN=None,
        RW_DSN="postgresql://u:p@h:5432/rw",
        AI_AUTOMATION_DSN=None,
        ATLAS_DSN_RW=None,
        ATLAS_DSN=None,
    ):
        assert env.get_rw_dsn() == "postgresql://u:p@h:5432/rw"


def test_rw_precedence_falls_back_to_ai_automation_dsn():
    """AI_AUTOMATION_DSN is used when GEMATRIA_DSN and RW_DSN are not set."""
    with temp_env(
        GEMATRIA_DSN=None,
        RW_DSN=None,
        AI_AUTOMATION_DSN="postgresql://u:p@h:5432/ai",
        ATLAS_DSN_RW=None,
        ATLAS_DSN=None,
    ):
        assert env.get_rw_dsn() == "postgresql://u:p@h:5432/ai"


def test_rw_precedence_falls_back_to_atlas_dsn_rw():
    """ATLAS_DSN_RW is used when earlier options are not set."""
    with temp_env(
        GEMATRIA_DSN=None,
        RW_DSN=None,
        AI_AUTOMATION_DSN=None,
        ATLAS_DSN_RW="postgresql://u:p@h:5432/atlasrw",
        ATLAS_DSN=None,
    ):
        assert env.get_rw_dsn() == "postgresql://u:p@h:5432/atlasrw"


def test_ro_precedence_prefers_atlas_dsn():
    """ATLAS_DSN takes precedence over RW fallback."""
    with temp_env(
        ATLAS_DSN="postgresql://u:p@h:5432/atlasro",
        GEMATRIA_DSN="postgresql://u:p@h:5432/gem",
        RW_DSN=None,
        AI_AUTOMATION_DSN=None,
        ATLAS_DSN_RW=None,
    ):
        assert env.get_ro_dsn() == "postgresql://u:p@h:5432/atlasro"


def test_ro_precedence_falls_back_to_rw():
    """RO falls back to RW when ATLAS_DSN is not set."""
    with temp_env(
        ATLAS_DSN=None,
        GEMATRIA_DSN="postgresql://u:p@h:5432/gem",
        RW_DSN=None,
        AI_AUTOMATION_DSN=None,
        ATLAS_DSN_RW=None,
    ):
        assert env.get_ro_dsn() == "postgresql://u:p@h:5432/gem"


def test_bible_db_dsn_precedence_prefers_bible_ro_dsn():
    """BIBLE_RO_DSN takes precedence over RO_DSN."""
    with temp_env(
        BIBLE_RO_DSN="postgresql://u:p@h:5432/biblero",
        RO_DSN="postgresql://u:p@h:5432/ro",
        ATLAS_DSN_RO=None,
        ATLAS_DSN=None,
    ):
        assert env.get_bible_db_dsn() == "postgresql://u:p@h:5432/biblero"


def test_bible_db_dsn_precedence_falls_back_to_ro_dsn():
    """RO_DSN is used when BIBLE_RO_DSN is not set."""
    with temp_env(BIBLE_RO_DSN=None, RO_DSN="postgresql://u:p@h:5432/ro", ATLAS_DSN_RO=None, ATLAS_DSN=None):
        assert env.get_bible_db_dsn() == "postgresql://u:p@h:5432/ro"


def test_bible_db_dsn_precedence_falls_back_to_atlas_dsn_ro():
    """ATLAS_DSN_RO is used when earlier options are not set."""
    with temp_env(BIBLE_RO_DSN=None, RO_DSN=None, ATLAS_DSN_RO="postgresql://u:p@h:5432/atlasro", ATLAS_DSN=None):
        assert env.get_bible_db_dsn() == "postgresql://u:p@h:5432/atlasro"


def test_bible_db_dsn_none_when_unset():
    """get_bible_db_dsn returns None when not set."""
    with temp_env(BIBLE_RO_DSN=None, RO_DSN=None, ATLAS_DSN_RO=None, ATLAS_DSN=None):
        assert env.get_bible_db_dsn() is None
