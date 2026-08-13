import re

from backend.app.services.database import get_connection


from functools import lru_cache

@lru_cache(maxsize=1)
def load_crypto_metadata():
    """
    Load cryptocurrency metadata once and cache it
    for the lifetime of the process.
    """

    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT symbol, name
            FROM crypto_metadata
            """
        ).fetchall()

    finally:
        connection.close()

    metadata = {}

    for symbol, name in rows:
        symbol = symbol.upper()

        metadata[symbol] = {
            "symbol": symbol,
            "name": name
        }

    return metadata


# --------------------------------------------------------------------
# A small, deliberately short list of high-confidence ticker symbols
# that are safe to detect as a *bare* mention (no "$", no trading
# context, no full name needed) because they are not ordinary English
# words and are overwhelmingly used to refer to the coin.
#
# This is the ONLY place bare-word crypto detection is allowed to
# happen. We do NOT walk the full CMC metadata table looking for any
# symbol that happens to appear as a bare word in text - that's what
# produced false positives like BUY, WOULD, EV, JST, STABLE, AMP.
# Growing an ever-longer EXCLUDED_WORDS denylist to patch each new
# collision doesn't fix the root cause (CMC has thousands of symbols
# and many will always collide with English words); keeping this
# whitelist short and curated does.
# --------------------------------------------------------------------
STRONG_SYMBOLS = frozenset({
    "BTC", "ETH", "SOL", "XRP", "DOGE", "ADA",
    "BNB", "LTC", "XMR", "DOT", "AVAX", "LINK",
    "TRX", "ATOM", "XLM",
})

# A symbol shorter than this is treated as a generic fragment for
# full-name matching purposes unless it's in STRONG_SYMBOLS - see the
# name-matching loop in identify_crypto_detailed for why.
MIN_DISTINCTIVE_SYMBOL_LENGTH = 4

_STRONG_SYMBOL_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(s) for s in STRONG_SYMBOLS) + r")\b",
    flags=re.IGNORECASE
)

_TRADING_ACTION = r"(?:LONG|SHORT|BUY|SELL)"

_TRADING_PATTERNS = [

    # $LQTY LONG / $LQTY - LONG / $LQTY: SHORT
    re.compile(
        rf"\$(?P<sym>[A-Za-z]{{2,15}})\s*[-:]?\s*"
        rf"(?P<action>{_TRADING_ACTION})\b",
        flags=re.IGNORECASE
    ),

    # LONG $LQTY / LONG LQTY
    re.compile(
        rf"\b(?P<action>{_TRADING_ACTION})\s+"
        rf"(?P<dollar>\$)?(?P<sym>[A-Za-z]{{2,15}})\b",
        flags=re.IGNORECASE
    ),

    # LQTY LONG (bare symbol before the action word)
    re.compile(
        rf"\b(?P<sym>[A-Za-z]{{2,15}})\s+"
        rf"(?P<action>{_TRADING_ACTION})\b",
        flags=re.IGNORECASE
    ),
]

_PAIR_PATTERN = re.compile(
    r"\$?(?P<sym>[A-Za-z]{2,15})\s*/\s*"
    r"(?P<quote>USDT|USD|USDC|BTC|ETH)",
    flags=re.IGNORECASE
)


@lru_cache(maxsize=1)
def get_metadata_index():
    """
    Build lookup structures from the cached CoinMarketCap metadata
    ONCE per process, instead of re-scanning every coin for every
    tweet.

        {
            "symbols": {"BTC": {...}, "ETH": {...}, "LQTY": {...}},
            "names": {"bitcoin": ["BTC"], "ethereum": ["ETH"]},
            "name_pattern": <compiled regex matching any distinctive
                              full name, or None if there are none>,
        }

    "names" and "name_pattern" only contain coins that pass the exact
    same "distinctive full name" checks previously applied inline,
    per-tweet, inside the detection loop (see identify_crypto_detailed
    docstring: STRONG_SYMBOLS, MIN_DISTINCTIVE_SYMBOL_LENGTH, and the
    "name is just the symbol restated" check). Moving those checks
    here changes *when* they run, not *what* they decide, so detection
    behavior is unchanged - this is purely an indexing optimization.
    """

    metadata = load_crypto_metadata()

    names_index = {}
    name_patterns = []

    for symbol, coin in metadata.items():

        name = (coin.get("name") or "").strip()

        if len(name) < 3:
            continue

        if symbol not in STRONG_SYMBOLS:

            # See identify_crypto_detailed for the rationale behind
            # these two checks - unchanged from before, just moved
            # here so they only run once per coin, not once per coin
            # per tweet.
            if len(symbol) < MIN_DISTINCTIVE_SYMBOL_LENGTH:
                continue

            if name.upper() == symbol:
                continue

        key = name.lower()

        names_index.setdefault(key, []).append(symbol)
        name_patterns.append(key)

    name_pattern = None

    if name_patterns:

        # Longer names first so that if one distinctive name happens
        # to be a substring of another, the longer (more specific)
        # one still gets a chance to match starting at that position.
        name_patterns.sort(key=len, reverse=True)

        alternation = "|".join(re.escape(p) for p in name_patterns)

        name_pattern = re.compile(
            rf"(?<![a-z0-9])(?:{alternation})(?![a-z0-9])"
        )

    # The original implementation looped over metadata.items() in
    # metadata-dict order, so whichever symbol came first in that
    # dict got added to the results pool first (this affects which
    # symbol ends up as primary_asset when several are mentioned).
    # The single-regex approach below instead finds matches in TEXT
    # order, which isn't the same thing - so we record each symbol's
    # original dict position once here, and re-sort any name matches
    # found in a tweet back into that same order before adding them.
    symbol_rank = {symbol: i for i, symbol in enumerate(metadata.keys())}

    return {
        "symbols": metadata,
        "names": names_index,
        "name_pattern": name_pattern,
        "symbol_rank": symbol_rank,
    }


def identify_crypto(text: str) -> list[str]:
    """
    Backward-compatible function.

    Returns all cryptocurrency assets mentioned in the text.
    """

    detailed = identify_crypto_detailed(text)

    assets = []

    primary = detailed["primary_asset"]

    if primary:
        assets.append(primary)

    for asset in detailed["mentioned_assets"]:
        if asset not in assets:
            assets.append(asset)

    return assets


def identify_crypto_detailed(text: str) -> dict:
    """
    Identify the primary cryptocurrency and other mentioned assets.

    CMC metadata is the source of truth for whether a symbol *exists*,
    but existing in the metadata table is NOT sufficient on its own to
    treat a bare word as crypto - most of CMC's ~10k+ symbols are
    short, arbitrary strings and many collide with ordinary English
    words (BUY, WOULD, EV, JST, STABLE, AMP, ...).

    Detection is prioritized as:

        1. Explicit "$TICKER" tags        - accept if in metadata
        2. Trading pairs ("SOL/USDT")     - accept if in metadata
        3. Explicit trading context       - accept if in metadata,
           ("SOL LONG", "LONG SOL")         with a light guard so the
                                             action word itself, or a
                                             random lowercase word
                                             next to it, can't be
                                             mistaken for the symbol
        4. Full cryptocurrency name       - accept if it's a genuine,
           ("Bitcoin", "Ethereum")          distinctive project name
        5. A small whitelist of very      - accept as a bare mention
           well-known symbols (BTC, ETH,
           SOL, XRP, DOGE, ADA, ...)
        6. Everything else                - NOT treated as crypto,
                                             no matter what the CMC
                                             metadata table contains
    """

    if not text:
        return {
            "primary_asset": None,
            "mentioned_assets": []
        }

    index = get_metadata_index()
    metadata = index["symbols"]
    names_index = index["names"]
    name_pattern = index["name_pattern"]
    symbol_rank = index["symbol_rank"]

    text_lower = text.lower()

    mentioned_assets = []

    def add_asset(symbol: str) -> None:
        symbol = symbol.upper()

        if symbol not in metadata:
            return

        if symbol not in mentioned_assets:
            mentioned_assets.append(symbol)

    # --------------------------------------------------
    # 1. Explicit $TICKER detection (strongest signal - the
    #    user deliberately tagged this as a ticker)
    # --------------------------------------------------

    for raw_symbol in re.findall(r"\$([A-Za-z]{2,15})", text):
        add_asset(raw_symbol)

    # --------------------------------------------------
    # 2. Full cryptocurrency name detection
    #
    #    Trusted for genuine, distinctive project names
    #    ("Bitcoin", "Ethereum", "Liquity"). The eligibility
    #    checks (short/generic symbols, names that are just the
    #    symbol restated, etc.) were already applied once, up
    #    front, when the index was built - see get_metadata_index.
    #    Here we just run a single pre-compiled regex over the
    #    tweet instead of looping over every coin in the metadata
    #    table.
    # --------------------------------------------------

    if name_pattern is not None:

        matched_symbols = set()

        for match in name_pattern.finditer(text_lower):

            for symbol in names_index.get(match.group(0), ()):
                matched_symbols.add(symbol)

        for symbol in sorted(
            matched_symbols,
            key=lambda s: symbol_rank.get(s, 0)
        ):
            add_asset(symbol)

    # --------------------------------------------------
    # 3. Well-known strong symbols (bare mention, no $ needed)
    # --------------------------------------------------

    for match in _STRONG_SYMBOL_PATTERN.findall(text):
        add_asset(match)

    # --------------------------------------------------
    # 4. Explicit trading signal
    #
    #    Only the "sym" capture group is ever checked against
    #    the metadata table - the action word (LONG/SHORT/BUY/
    #    SELL) is never itself a candidate symbol. A bare (non-$)
    #    symbol is only trusted when it's in the high-confidence
    #    STRONG_SYMBOLS whitelist. Being written in caps is NOT
    #    sufficient on its own - arbitrary CMC symbols shouldn't
    #    become crypto just because someone capitalized a word -
    #    so "likely buy back", "STABLE LONG", etc. are never
    #    mistaken for a ticker unless $-tagged or whitelisted.
    # --------------------------------------------------

    for compiled_pattern in _TRADING_PATTERNS:

        for match in compiled_pattern.finditer(text):

            groups = match.groupdict()

            raw_symbol = groups.get("sym")

            if not raw_symbol:
                continue

            symbol = raw_symbol.upper()

            if symbol not in metadata:
                continue

            has_dollar = bool(groups.get("dollar")) or match.group(0).startswith("$")

            is_trusted_bare = (
                has_dollar
                or symbol in STRONG_SYMBOLS
            )

            if not is_trusted_bare:
                continue

            return {
                "primary_asset": symbol,
                "mentioned_assets": [
                    asset
                    for asset in mentioned_assets
                    if asset != symbol
                ]
            }

    # --------------------------------------------------
    # 5. Trading pair
    # --------------------------------------------------

    pair_match = _PAIR_PATTERN.search(text)

    if pair_match:

        symbol = pair_match.group("sym").upper()

        if symbol in metadata:

            return {
                "primary_asset": symbol,
                "mentioned_assets": [
                    asset
                    for asset in mentioned_assets
                    if asset != symbol
                ]
            }

    # --------------------------------------------------
    # 6. Only one asset
    # --------------------------------------------------

    if len(mentioned_assets) == 1:

        return {
            "primary_asset": mentioned_assets[0],
            "mentioned_assets": []
        }

    # --------------------------------------------------
    # 7. Fallback
    # --------------------------------------------------

    if mentioned_assets:

        return {
            "primary_asset": mentioned_assets[0],
            "mentioned_assets": mentioned_assets[1:]
        }

    return {
        "primary_asset": None,
        "mentioned_assets": []
    }


def is_crypto_related(text: str) -> bool:
    return identify_crypto(text) != []


if __name__ == "__main__":

    test_posts = [

        "Bitcoin could become increasingly important.",

        "Ethereum and Bitcoin are both bullish.",

        "$LQTY — LONG Entry: 0.2164 TP1: 0.2215",

        "$BTC $ETH $SOL",

        "LQTY/USDT looks ready for a breakout.",

        "LONG $SOL while Bitcoin remains strong.",

        "The stock market was stable today.",

        "What would you do if you had to choose between potentially "
        "losing everything or selling some btc you will likely buy "
        "back later?",

        "Interesting to see various tech, bitcoin companies expanding "
        "into new markets this year.",
    ]

    for post in test_posts:

        result = identify_crypto_detailed(post)

        print("\nPost:", post)
        print(
            "Primary asset:",
            result["primary_asset"]
        )
        print(
            "Mentioned assets:",
            result["mentioned_assets"]
        )