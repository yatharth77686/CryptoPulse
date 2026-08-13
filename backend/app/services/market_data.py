from datetime import datetime, timezone, timedelta

from .binance_market import get_historical_candles


def calculate_price_reaction(
    symbol: str,
    post_timestamp: str
):
    timestamp = datetime.fromisoformat(
        post_timestamp.replace("Z", "+00:00")
    )

    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(
            tzinfo=timezone.utc
        )

    # --------------------------------------------------
    # Fetch one minute before the tweet timestamp.
    #
    # This ensures the candle containing the tweet
    # is available for base-candle selection.
    # --------------------------------------------------

    candle_start = timestamp - timedelta(minutes=1)

    candles = get_historical_candles(
        f"{symbol}USDT",
        candle_start,
        interval="1m",
        limit=62
    )

    if not candles:
        raise ValueError(
            f"No market data found for {symbol}"
        )

    # Binance candle:
    # [open_time, open, high, low, close, volume, ...]

    prices = {}

    for candle in candles:
        open_time = int(candle[0])
        close_price = float(candle[4])

        prices[open_time] = close_price

    post_time_ms = int(
        timestamp.timestamp() * 1000
    )

    # --------------------------------------------------
    # Find the latest candle whose OPEN time is
    # at or before the tweet timestamp.
    # --------------------------------------------------

    eligible_candles = [
        candle
        for candle in candles
        if int(candle[0]) <= post_time_ms
    ]

    if not eligible_candles:
        raise ValueError(
            f"No candle at or before tweet time "
            f"for {symbol}"
        )

    base_candle = max(
        eligible_candles,
        key=lambda candle: int(candle[0])
    )

    base_time = int(
        base_candle[0]
    )

    base_price = float(
        base_candle[4]
    )

    # --------------------------------------------------
    # Get future prices
    # --------------------------------------------------

    def get_future_price(minutes):
        target_time = (
            base_time
            + minutes * 60 * 1000
        )

        if target_time in prices:
            return prices[target_time]

        closest = min(
            prices.keys(),
            key=lambda t: abs(
                t - target_time
            )
        )

        return prices[closest]

    # --------------------------------------------------
    # Calculate percentage change
    # --------------------------------------------------

    def calculate_change(price):
        return round(
            (
                (price - base_price)
                / base_price
            ) * 100,
            3
        )

    price_5m = get_future_price(5)
    price_15m = get_future_price(15)
    price_60m = get_future_price(60)

    return {
        "symbol": symbol,
        "post_timestamp": timestamp.isoformat(),

        "base_price": base_price,

        "5m": {
            "price": price_5m,
            "change_percent": calculate_change(
                price_5m
            )
        },

        "15m": {
            "price": price_15m,
            "change_percent": calculate_change(
                price_15m
            )
        },

        "1h": {
            "price": price_60m,
            "change_percent": calculate_change(
                price_60m
            )
        }
    }


if __name__ == "__main__":

    result = calculate_price_reaction(
        "BTC",
        "2026-08-10T18:30:00Z"
    )

    print(result)