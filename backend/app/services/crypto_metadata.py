import os
import sqlite3
import requests
from datetime import datetime, timezone

from dotenv import load_dotenv

from backend.app.services.database import get_connection


load_dotenv()

CMC_API_URL = (
    "https://pro-api.coinmarketcap.com"
    "/v1/cryptocurrency/listings/latest"
)

CMC_API_KEY = os.getenv(
    "COINMARKETCAP_API_KEY"
)


def ensure_crypto_metadata_schema(
    connection: sqlite3.Connection
):
    """
    Create the local cryptocurrency metadata table
    if it does not already exist.
    """

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS crypto_metadata (
            cmc_id INTEGER PRIMARY KEY,
            symbol TEXT NOT NULL,
            name TEXT NOT NULL,
            slug TEXT,
            rank INTEGER,
            last_updated TEXT
        )
        """
    )

    connection.commit()


def fetch_crypto_metadata(
    limit: int = 2000
) -> list[dict]:
    """
    Fetch cryptocurrency metadata from CoinMarketCap.

    The data is fetched from CMC and later stored locally.
    """

    if not CMC_API_KEY:
        raise RuntimeError(
            "COINMARKETCAP_API_KEY is not set."
        )

    headers = {
        "X-CMC_PRO_API_KEY": CMC_API_KEY,
        "Accepts": "application/json"
    }

    params = {
        "start": 1,
        "limit": min(limit, 5000),
        "convert": "USD"
    }

    response = requests.get(
        CMC_API_URL,
        headers=headers,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    payload = response.json()

    if payload.get("status", {}).get("error_code", 0) != 0:
        raise RuntimeError(
            payload.get("status", {}).get(
                "error_message",
                "CoinMarketCap API error"
            )
        )

    return payload.get("data", [])


def save_crypto_metadata(
    connection: sqlite3.Connection,
    cryptocurrencies: list[dict]
):
    """
    Store/update cryptocurrency metadata locally.
    """

    for crypto in cryptocurrencies:

        connection.execute(
            """
            INSERT INTO crypto_metadata (
                cmc_id,
                symbol,
                name,
                slug,
                rank,
                last_updated
            )
            VALUES (?, ?, ?, ?, ?, ?)

            ON CONFLICT(cmc_id)
            DO UPDATE SET
                symbol = excluded.symbol,
                name = excluded.name,
                slug = excluded.slug,
                rank = excluded.rank,
                last_updated = excluded.last_updated
            """,
            (
                crypto.get("id"),
                crypto.get("symbol"),
                crypto.get("name"),
                crypto.get("slug"),
                crypto.get("cmc_rank"),
                crypto.get("last_updated")
            )
        )

    connection.commit()


def sync_crypto_metadata(
    limit: int = 2000
):
    """
    Fetch cryptocurrency metadata from CMC
    and synchronize it with the local SQLite database.
    """

    cryptocurrencies = fetch_crypto_metadata(
        limit=limit
    )

    connection = get_connection()

    try:

        ensure_crypto_metadata_schema(
            connection
        )

        save_crypto_metadata(
            connection,
            cryptocurrencies
        )

    finally:

        connection.close()

    print(
        f"Synced {len(cryptocurrencies)} "
        f"cryptocurrencies."
    )


if __name__ == "__main__":

    sync_crypto_metadata(
        limit=2000
    )