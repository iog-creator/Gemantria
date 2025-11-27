import sys
from sqlalchemy import text
from agentpm.db.loader import get_control_engine


def check_vector():
    try:
        engine = get_control_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM pg_extension WHERE extname = 'vector';"))
            row = result.fetchone()
            if row:
                print("SUCCESS: pgvector extension found!")
                return 0
            else:
                print("FAILURE: pgvector extension NOT found.")
                return 1
    except Exception as e:
        print(f"ERROR: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(check_vector())
