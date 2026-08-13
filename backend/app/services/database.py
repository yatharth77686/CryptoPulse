import sqlite3
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "cryptopulse.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def initialize_database():
    
    connection = get_connection()
    cursor = connection.cursor()

    # --------------------------------------------------
    # Tweet analysis table
    # --------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tweet_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tweet_id TEXT UNIQUE,
            author TEXT,
            text TEXT,
            timestamp TEXT,
            assets TEXT,
            cryptobert_label TEXT,
            cryptobert_confidence REAL,
            finbert_label TEXT,
            finbert_confidence REAL,
            influence_score REAL,
            followers INTEGER,
            likes INTEGER,
            retweets INTEGER,
            market_reaction TEXT
        )
    """)

    # --------------------------------------------------
    # Persistent Twitter profile cache
    # --------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profile_cache (
            username TEXT PRIMARY KEY,
            profile_json TEXT,
            fetched_at REAL NOT NULL,
            status TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()

def update_market_reaction(
    tweet_id: str,
    market_reaction: dict
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE tweet_analysis
        SET market_reaction = ?
        WHERE tweet_id = ?
        """,
        (
            json.dumps(market_reaction),
            tweet_id
        )
    )

    connection.commit()
    connection.close()


def get_pending_market_reactions():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT tweet_id, timestamp, assets
        FROM tweet_analysis
        WHERE market_reaction LIKE '%pending%'
        ORDER BY id ASC
        """
    )

    rows = cursor.fetchall()

    connection.close()

    return rows

def add_signal_strength_column():
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            ALTER TABLE tweet_analysis
            ADD COLUMN signal_strength REAL
            """
        )
        connection.commit()

    except Exception as error:
        if "duplicate column name" not in str(error).lower():
            raise

    finally:
        connection.close()


def get_all_analyses():
    connection = get_connection()
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM tweet_analysis
        ORDER BY id DESC
        """
    )

    rows = cursor.fetchall()
    connection.close()

    return [dict(row) for row in rows]    


def tweet_exists(tweet_id: str) -> bool:
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT 1
        FROM tweet_analysis
        WHERE tweet_id = ?
        LIMIT 1
        """,
        (tweet_id,)
    )

    exists = cursor.fetchone() is not None

    connection.close()

    return exists


def save_analysis(result: dict):
    connection = get_connection()
    cursor = connection.cursor()

    tweet = result["tweet"]
    sentiment = result["sentiment"]
    influence = result["social_influence"]

    cursor.execute(
        """
        INSERT OR REPLACE INTO tweet_analysis (
            tweet_id,
            author,
            text,
            timestamp,
            assets,
            cryptobert_label,
            cryptobert_confidence,
            finbert_label,
            finbert_confidence,
            influence_score,
            signal_strength,
            followers,
            likes,
            retweets,
            market_reaction
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)
        """,
        (
            tweet["tweet_id"],
            tweet["author"],
            tweet["text"],
            tweet["timestamp"],
            json.dumps(result["assets"]),
            sentiment["cryptobert"]["sentiment"],
            sentiment["cryptobert"]["confidence"],
            sentiment["finbert"]["sentiment"],
            sentiment["finbert"]["confidence"],
            influence["score"],
            result["signal_strength"],
            influence["followers"],
            influence["likes"],
            influence["retweets"],
            json.dumps(result["market_reaction"]),
        )
    )

    connection.commit()
    connection.close()


if __name__ == "__main__":

    initialize_database()

    test_result = {
        "tweet": {
            "tweet_id": "test_001",
            "author": "test_user",
            "text": "Bitcoin looks bullish!",
            "timestamp": "2026-08-12T00:00:00Z"
        },
        "assets": ["BTC"],
        "sentiment": {
            "cryptobert": {
                "sentiment": "Bullish",
                "confidence": 0.85
            },
            "finbert": {
                "sentiment": "positive",
                "confidence": 0.80
            }
        },
        "social_influence": {
            "score": 65.5,
            "followers": 10000,
            "likes": 500,
            "retweets": 100
        },
        "market_reaction": {}
    }

    save_analysis(test_result)

    print("CryptoPulse database initialized.")
    print("Test analysis saved successfully.")
    print(f"Database: {DB_PATH}")