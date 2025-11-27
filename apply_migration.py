import sys
from sqlalchemy import text
from agentpm.db.loader import get_control_engine


def apply_migration():
    try:
        engine = get_control_engine()
        with open("migrations/049_control_kb_embedding.sql") as f:
            sql = f.read()

        with engine.connect() as conn:
            # Split by semicolon to handle multiple statements if needed,
            # but SQLAlchemy execute() can often handle blocks.
            # For safety with BEGIN/COMMIT, we execute as one block.
            conn.execute(text(sql))
            conn.commit()
            print("SUCCESS: Migration 049 applied.")
            return 0
    except Exception as e:
        print(f"ERROR: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(apply_migration())
