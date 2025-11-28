import psycopg


def test_connection():
    conn_str = "postgresql://postgres:postgres@localhost:5432/bible_db"
    try:
        print(f"Connecting to {conn_str}...")
        conn = psycopg.connect(conn_str)
        print("Connected!")
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM bible.greek_nt_words")
        count = cur.fetchone()[0]
        print(f"Greek words count: {count}")

        # Check Mark 1:1
        cur.execute(
            "SELECT * FROM bible.greek_nt_words WHERE verse_id = (SELECT id FROM bible.verses WHERE book_name='Mark' AND chapter_num=1 AND verse_num=1 AND translation_source='TAGNT')"
        )
        rows = cur.fetchall()
        print(f"Mark 1:1 words: {len(rows)}")

        conn.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test_connection()
