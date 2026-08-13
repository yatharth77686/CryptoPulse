import requests
from datetime import datetime, timezone


BASE_URL = "https://api.binance.com"


def get_historical_candles(
    symbol: str,
    start_time: datetime,
    interval: str = "1m",
    limit: int = 60
):
    start_ms = int(start_time.timestamp() * 1000)

    response = requests.get(
        f"{BASE_URL}/api/v3/klines",
        params={
            "symbol": symbol,
            "interval": interval,
            "startTime": start_ms,
            "limit": limit
        },
        timeout=10
    )

    response.raise_for_status()

    return response.json()


if __name__ == "__main__":
    timestamp = datetime(
        2026,
        8,
        10,
        18,
        30,
        tzinfo=timezone.utc
    )

    candles = get_historical_candles(
        "BTCUSDT",
        timestamp,
        interval="1m",
        limit=60
    )

    print(f"Received {len(candles)} candles")

    if candles:
        first = candles[0]

        print("\nFirst candle:")
        print(f"Open time: {first[0]}")
        print(f"Open: {first[1]}")
        print(f"High: {first[2]}")
        print(f"Low: {first[3]}")
        print(f"Close: {first[4]}")
        print(f"Volume: {first[5]}")