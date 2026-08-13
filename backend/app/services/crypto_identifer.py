import re

from backend.app.services.database import get_connection


# ============================================================
# Cache
# ============================================================

_CRYPTO_CACHE = None


# ============================================================
# Common English words that can also appear as crypto symbols
# ============================================================

AMBIGUOUS_SYMBOLS = {
    "ONE",
    "NEAR",
    "LINK",
    "ATOM",
    "UNI",
    "DOT",
    "TON",
    "OP",
    "IN",
    "GAS",
    "APE",
    "FIL",
    "VET",
    "ETC",
    "ARB",
    "SOL",
    "SUI",
    "SEI",
    "ADA",
    "MKR",
    "POL",
}

LOWERCASE_SAFE_SYMBOLS = {
    "BTC",
    "ETH",
    "DOGE",
    "XRP",
    "STX",
    "BNB",
    "LTC",
    "BCH",
    "XLM",
    "HBAR",
    "SHIB",
    "PEPE",
    "AAVE",
    "RENDER",
    "KAS",
    "XMR",
    "ZEC",
}

# ============================================================
# High-confidence crypto name aliases
# ============================================================

CORE_CRYPTO_ALIASES = {
    "bitcoin": "BTC",
    "ethereum": "ETH",
    "dogecoin": "DOGE",
    "solana": "SOL",
    "cardano": "ADA",
    "ripple": "XRP",
    "litecoin": "LTC",
    "bitcoin cash": "BCH",
    "binance coin": "BNB",
    "avalanche": "AVAX",
    "polkadot": "DOT",
    "chainlink": "LINK",
    "stellar": "XLM",
    "cosmos": "ATOM",
    "uniswap": "UNI",
    "tron": "TRX",
    "near protocol": "NEAR",
    "aptos": "APT",
    "arbitrum": "ARB",
    "optimism": "OP",
    "filecoin": "FIL",
    "hedera": "HBAR",
    "vechain": "VET",
    "stacks": "STX",
    "shiba inu": "SHIB",
    "pepe": "PEPE",
    "monero": "XMR",
    "zcash": "ZEC",
    "kaspa": "KAS",
}

COMMON_FALSE_POSITIVE_SYMBOLS = {
    "BUY",
}


# ============================================================
# Load CMC metadata from existing SQLite cache
# ============================================================

def load_crypto_metadata():
    """
    Load cryptocurrency names and symbols from the existing
    crypto_metadata SQLite table.

    Returns two dictionaries:

        names:
            bitcoin -> BTC
            ethereum -> ETH

        symbols:
            btc -> BTC
            eth -> ETH
    """

    global _CRYPTO_CACHE

    if _CRYPTO_CACHE is not None:
        return _CRYPTO_CACHE

    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT symbol, name
            FROM crypto_metadata
            WHERE symbol IS NOT NULL
              AND name IS NOT NULL
            """
        ).fetchall()

    finally:
        connection.close()

    names = {}
    symbols = {}

    for row in rows:

        symbol = str(row[0]).strip().upper()
        name = str(row[1]).strip().lower()

        if not symbol or not name:
            continue

        # Name -> symbol
        #
        # Example:
        # bitcoin -> BTC
        # ethereum -> ETH
        #
        # Keep the first valid occurrence.
        if name not in names:
            names[name] = symbol

        # Symbol -> symbol
        #
        # Example:
        # btc -> BTC
        # eth -> ETH
        #
        if symbol.lower() not in symbols:
            symbols[symbol.lower()] = symbol

    _CRYPTO_CACHE = {
        "names": names,
        "symbols": symbols,
    }

    return _CRYPTO_CACHE


# ============================================================
# Refresh cache
# ============================================================

def refresh_crypto_metadata_cache():
    """
    Clear the in-memory cache.

    The next call to identify_crypto() will reload the
    current crypto_metadata table.
    """

    global _CRYPTO_CACHE

    _CRYPTO_CACHE = None


# ============================================================
# Word matching
# ============================================================

def find_exact_word(text: str, word: str) -> bool:

    pattern = (
        r"(?<![A-Za-z0-9_])"
        + re.escape(word)
        + r"(?![A-Za-z0-9_])"
    )

    return re.search(
        pattern,
        text,
        flags=re.IGNORECASE
    ) is not None


# ============================================================
# Crypto identification
# ============================================================

def identify_crypto(text: str) -> list[str]:
    """
    Identify cryptocurrencies mentioned in text.

    Uses the existing CoinMarketCap metadata stored in SQLite.

    Supports:

        Bitcoin
        bitcoin
        BTC
        btc
        $BTC
        #BTC
        Bitcoin and Ethereum
        BTC/ETH

    Returns:

        ["BTC", "ETH"]
    """

    if not text:
        return []

    cache = load_crypto_metadata()

    names = cache["names"]
    symbols = cache["symbols"]

    detected = []

    # ========================================================
    # 1. Explicit ticker notation
    #
    # $BTC
    # #BTC
    # ========================================================

    explicit_tickers = re.findall(
        r"[$#]([A-Za-z][A-Za-z0-9]{1,14})",
        text
    )

    for ticker in explicit_tickers:

        symbol = ticker.upper()

        if symbol in COMMON_FALSE_POSITIVE_SYMBOLS:
            continue

        if symbol in symbols.values():

            if symbol not in detected:
                detected.append(symbol)

    # ========================================================
    # 2. Cryptocurrency names
    # ========================================================
    COMMON_WORD_NAMES = {
        "momentum",
        "maker",
        "near",
        "link",
        "one",
        "atom",
        "ton",
        "gas",
        "ape",
        "render",
        "injective",
        "immutable",
        "optimism",
        "polygon",
        "stellar",
        "cosmos",
        "maker",
    }

    # High-confidence cryptocurrency names.
    #
    # These are unambiguous enough to identify directly.
    HIGH_CONFIDENCE_NAMES = {
        "bitcoin",
        "ethereum",
        "dogecoin",
        "solana",
        "cardano",
        "ripple",
        "binance coin",
        "avalanche",
        "chainlink",
        "polkadot",
        "litecoin",
        "bitcoin cash",
        "stellar",
        "cosmos",
        "uniswap",
        "toncoin",
        "tron",
        "near protocol",
        "internet computer",
        "aptos",
        "arbitrum",
        "injective",
        "filecoin",
        "algorand",
        "hedera",
        "vechain",
        "stacks",
        "pepe",
        "shiba inu",
        "render token",
        "kaspa",
        "monero",
        "zcash",
        "ethereum classic",
        "celestia",
        "immutable",
    }


        # ========================================================
    # 2A. Core cryptocurrency aliases
    #
    # These do not depend on the SQLite metadata cache.
    # This guarantees that common assets such as Bitcoin
    # and Ethereum are detected from their names.
    # ========================================================

    for name, symbol in CORE_CRYPTO_ALIASES.items():

        if find_exact_word(text, name):

            if symbol not in detected:
                detected.append(symbol)

    for name in HIGH_CONFIDENCE_NAMES:

        if name not in names:
            continue

        if find_exact_word(text, name):

            symbol = names[name]

            if symbol not in detected:
                detected.append(symbol)

    # ========================================================
    # 3. Bare ticker symbols
    #
    # BTC
    # ETH
    # STX
    #
    # We intentionally require uppercase for ambiguous symbols.
    # ========================================================

    for symbol_lower, symbol in symbols.items():

        if symbol in COMMON_FALSE_POSITIVE_SYMBOLS:
            continue

        # Don't process symbols that are too long.
        if len(symbol) > 15:
            continue

        # Find occurrences.
        pattern = (
            r"(?<![A-Za-z0-9_$#])"
            + re.escape(symbol)
            + r"(?![A-Za-z0-9_])"
        )

        matches = re.finditer(
            pattern,
            text,
            
        )

        for match in matches:

            actual_text = match.group(0)

            # ----------------------------------------------
            # Explicit notation already handled above
            # ----------------------------------------------

            if match.start() > 0:

                previous = text[match.start() - 1]

                if previous in "$#":
                    continue

            # ----------------------------------------------
            # Ambiguous symbols
            #
            # LINK:
            #
            # "click the link"
            #       -> reject
            #
            # "LINK is bullish"
            #       -> accept
            #
            # ----------------------------------------------

            if symbol in AMBIGUOUS_SYMBOLS:

                if actual_text != symbol:
                    continue

                elif actual_text != symbol:

                     if symbol not in LOWERCASE_SAFE_SYMBOLS:
                        continue

            # ----------------------------------------------
            # Non-ambiguous symbols
            #
            # Accept uppercase or lowercase.
            # ----------------------------------------------

            if symbol not in detected:
                detected.append(symbol)

    return detected


# ============================================================
# Tests
# ============================================================

if __name__ == "__main__":

    refresh_crypto_metadata_cache()

    test_posts = [

        # Should detect
        "Bitcoin is gaining momentum.",
        "bitcoin is gaining momentum.",
        "BTC is looking strong.",
        "btc always finds a way.",
        "$BTC is breaking resistance.",
        "#BTC and #ETH are moving.",
        "Ethereum and Bitcoin are both interesting.",
        "Dogecoin could see increased adoption.",
        "BTC and ETH are both bullish.",
        "I like SOL and AVAX.",
        "STX/BTC looks interesting.",
        "Bitcoin vs Ethereum.",
        "Solana, XRP and Cardano are moving.",

        # Should NOT detect
        "What would you do if you had to choose?",
        "What would you BUY?",
        "The stock market was stable today.",
        "Everyone is watching the market.",
        "This is a very good asset.",
        "We should buy some stocks.",
        "The event was interesting.",
        "I would never buy this.",
        "The company reported strong earnings.",
        "Click the link to read more.",
        "Near the market there is a new store.",
        "The maker released a new product.",
    ]

    print("=" * 70)
    print("CRYPTO IDENTIFIER TEST")
    print("=" * 70)

    cache = load_crypto_metadata()

    print(
        f"\nLoaded {len(cache['names'])} cryptocurrency names."
    )

    print(
        f"Loaded {len(cache['symbols'])} cryptocurrency symbols."
    )

    for post in test_posts:

        assets = identify_crypto(post)

        print()
        print("TEXT:", post)
        print("ASSETS:", assets)