import json
from datetime import datetime, timezone

from backend.app.services.database import (
    get_pending_market_reactions,
    update_market_reaction,
)

from backend.app.services.market_data import (
    calculate_price_reaction,
)


def parse_timestamp(timestamp_str: str) -> datetime:
    """
    Parse Twitter/Sorsa or ISO timestamp.
    """

    # Twitter/Sorsa format:
    # Wed Aug 12 11:53:05 +0000 2026
    try:
        timestamp = datetime.strptime(
            timestamp_str,
            "%a %b %d %H:%M:%S %z %Y"
        )

    except ValueError:
        # ISO format:
        # 2026-08-12T11:53:05+00:00
        timestamp = datetime.fromisoformat(
            timestamp_str.replace("Z", "+00:00")
        )

    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(
            tzinfo=timezone.utc
        )

    return timestamp


def extract_assets(assets_json: str) -> list[str]:
    """
    Supports both historical and current asset formats.

    Old:
        ["BTC", "ETH"]

    New:
        {
            "primary": "BTC",
            "mentioned": ["ETH"]
        }
    """

    assets_data = json.loads(assets_json)

    # ----------------------------------------------
    # Old format
    # ----------------------------------------------

    if isinstance(assets_data, list):

        return [
            asset
            for asset in assets_data
            if asset
        ]

    # ----------------------------------------------
    # New format
    # ----------------------------------------------

    if isinstance(assets_data, dict):

        assets = []

        primary = assets_data.get(
            "primary"
        )

        if primary:
            assets.append(primary)

        mentioned = assets_data.get(
            "mentioned",
            []
        )

        if isinstance(mentioned, list):

            assets.extend(
                asset
                for asset in mentioned
                if asset
            )

        return assets

    return []


def update_pending_reactions():

    rows = get_pending_market_reactions()

    updated = 0

    for tweet_id, timestamp_str, assets_json in rows:

        # ------------------------------------------
        # Validate timestamp
        # ------------------------------------------

        if not timestamp_str:
            continue

        try:

            timestamp = parse_timestamp(
                timestamp_str
            )

        except (ValueError, TypeError) as error:

            print(
                f"Skipping {tweet_id}: "
                f"invalid timestamp: {error}"
            )

            continue

        # ------------------------------------------
        # Check tweet age
        # ------------------------------------------

        age_minutes = (
            datetime.now(timezone.utc)
            - timestamp
        ).total_seconds() / 60

        # Wait until 1 hour has passed
        if age_minutes < 60:
            continue

        # ------------------------------------------
        # Extract assets
        # ------------------------------------------

        try:

            assets = extract_assets(
                assets_json
            )

        except (
            TypeError,
            json.JSONDecodeError,
        ) as error:

            print(
                f"Skipping {tweet_id}: "
                f"invalid assets JSON: {error}"
            )

            continue

        if not assets:

            print(
                f"Skipping {tweet_id}: "
                "no assets found"
            )

            continue

        # ------------------------------------------
        # Calculate market reaction
        # ------------------------------------------

        market_reaction = {}

        for asset in assets:

            try:

                reaction = calculate_price_reaction(
                    asset,
                    timestamp.isoformat()
                )

                market_reaction[asset] = reaction

            except Exception as error:

                market_reaction[asset] = {
                    "status": "unavailable",
                    "error": str(error)
                }

        # ------------------------------------------
        # Save result
        # ------------------------------------------

        update_market_reaction(
            tweet_id,
            market_reaction
        )

        updated += 1

        print(
            f"Updated market reaction: {tweet_id}"
        )

    return updated


if __name__ == "__main__":

    updated = update_pending_reactions()

    print(
        f"Updated {updated} market reactions."
    )