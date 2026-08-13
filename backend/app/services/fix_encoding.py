from backend.app.services.database import get_connection


def fix_encoding():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, text
        FROM tweet_analysis
        WHERE text IS NOT NULL
        """
    )

    rows = cursor.fetchall()

    fixed = 0

    for row_id, text in rows:
        try:
            repaired = text.encode("latin1").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            continue

        if repaired != text:
            cursor.execute(
                """
                UPDATE tweet_analysis
                SET text = ?
                WHERE id = ?
                """,
                (repaired, row_id)
            )

            fixed += 1

    connection.commit()
    connection.close()

    print(f"Fixed {fixed} tweet(s).")


if __name__ == "__main__":
    fix_encoding()