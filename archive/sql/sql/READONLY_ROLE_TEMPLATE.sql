-- Gemantria Read-Only Role Template (fill placeholders, run with a privileged DSN)

-- Replace: :ro_user, :ro_password, :db_name, and adjust schemas if needed.

DO $$

BEGIN

  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = ':ro_user') THEN

    CREATE ROLE :ro_user LOGIN PASSWORD ':ro_password' NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT;

  END IF;

END $$;



GRANT CONNECT ON DATABASE :db_name TO :ro_user;



-- Typical read paths in this project (adjust as needed)

GRANT USAGE ON SCHEMA public TO :ro_user;

GRANT USAGE ON SCHEMA gematria TO :ro_user;



GRANT SELECT ON ALL TABLES IN SCHEMA public TO :ro_user;

GRANT SELECT ON ALL TABLES IN SCHEMA gematria TO :ro_user;



ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO :ro_user;

ALTER DEFAULT PRIVILEGES IN SCHEMA gematria GRANT SELECT ON TABLES TO :ro_user;

