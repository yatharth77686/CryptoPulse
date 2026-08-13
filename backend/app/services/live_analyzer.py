import time
from datetime import datetime, timezone



from backend.app.services.twitter_api import search_tweets
from backend.app.services.tweet_processor import normalize_tweets

from backend.app.services.crypto_sentiment import analyze_crypto_sentiment
from backend.app.services.finbert_sentiment import analyze_finbert_sentiment

from backend.app.services.social_influence import (
    calculate_social_influence,
    calculate_signal_strength
)

from backend.app.services.crypto_detector import identify_crypto_detailed

from backend.app.services.market_data import calculate_price_reaction
from backend.app.services.text_preprocessor import preprocess_tweet

from backend.app.services.database import (
    initialize_database,
    save_analysis,
    get_connection,
    tweet_exists
)

from backend.app.services.twitter_profile import (
    ensure_schema,
    get_profiles_for_authors
)


def parse_tweet_timestamp(timestamp_str: str) -> datetime:
    """
    Parse TwitterAPI.io timestamp into a timezone-aware datetime.
    """

    try:
        timestamp = datetime.strptime(
            timestamp_str,
            "%a %b %d %H:%M:%S %z %Y"
        )

        return timestamp

    except ValueError:

        timestamp = datetime.fromisoformat(
            timestamp_str.replace("Z", "+00:00")
        )

        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(
                tzinfo=timezone.utc
            )

        return timestamp


# ============================================================
# Fetch multiple pages from TwitterAPI.io
# ============================================================

def fetch_tweets_with_pagination(
    query: str,
    target_count: int = 200,
):
    """
    Fetch multiple pages from TwitterAPI.io until we have
    approximately target_count unique tweets or there are
    no more pages.

    TwitterAPI.io currently returns up to 20 tweets per page.
    """

    all_tweets = []
    seen_ids = set()

    cursor = None
    page_number = 0

    while len(all_tweets) < target_count:

        page_number += 1

        print(
            f"\nFetching Twitter page {page_number}..."
        )

        response = search_tweets(
            query=query,
            query_type="Latest",
            cursor=cursor,
        )

        tweets = response.get(
            "tweets",
            []
        )

        if not tweets:
            print(
                "No more tweets returned."
            )
            break

        new_count = 0

        for tweet in tweets:

            tweet_id = tweet.get("id")

            if not tweet_id:
                continue

            if tweet_id in seen_ids:
                continue

            seen_ids.add(tweet_id)
            all_tweets.append(tweet)
            new_count += 1

            if len(all_tweets) >= target_count:
                break

        print(
            f"Page returned {len(tweets)} tweets | "
            f"new: {new_count} | "
            f"total collected: {len(all_tweets)}"
        )

        if len(all_tweets) >= target_count:
            break

        if not response.get(
            "has_next_page",
            False
        ):
            print(
                "TwitterAPI.io reports no more pages."
            )
            break

        next_cursor = response.get(
            "next_cursor"
        )

        if not next_cursor:
            print(
                "No next cursor returned."
            )
            break

        cursor = next_cursor

    return all_tweets


# ============================================================
# Analyze live / collected tweets
# ============================================================

def analyze_live_tweets(
    query: str,
    limit: int = 200,
    tweets_override=None,
):

    # --------------------------------------------------
    # 1. Fetch enough tweets
    # --------------------------------------------------

    if tweets_override is not None:
        tweets = tweets_override
    else:
        tweets = fetch_tweets_with_pagination(
            query=query,
            target_count=limit,
    )
    print(
        f"\nCollected {len(tweets)} unique tweets."
    )

    if not tweets:
        return []

    # --------------------------------------------------
    # 2. Resolve all unique author profiles in one batch
    # --------------------------------------------------

    authors = [
        tweet["author"]["userName"]
        for tweet in tweets
        if (
            isinstance(tweet.get("author"), dict)
            and tweet["author"].get("userName")
        )
    ]

    connection = get_connection()

    try:

        ensure_schema(connection)

        profiles = get_profiles_for_authors(
            authors,
            connection
        )

        # --------------------------------------------------
        # 3. Normalize tweets
        # --------------------------------------------------

        tweets = normalize_tweets(
            tweets,
            profiles
        )

        results = []

        # --------------------------------------------------
        # 4. Analyze each tweet
        # --------------------------------------------------

        for index, tweet in enumerate(tweets, start=1):

            print(
                f"\nAnalyzing tweet "
                f"{index}/{len(tweets)}..."
            )

            raw_text = tweet["text"]

            # --------------------------------------------------
            # Clean tweet text before ML processing
            # --------------------------------------------------

            text = preprocess_tweet(
                raw_text
            )

            # --------------------------------------------------
            # Crypto detection
            # --------------------------------------------------

            crypto_result = identify_crypto_detailed(
                text
            )

            primary_asset = crypto_result[
                "primary_asset"
            ]

            mentioned_assets = crypto_result[
                "mentioned_assets"
            ]

            # Skip non-crypto posts

            if not primary_asset:

                print(
                    "Skipped: no primary crypto asset."
                )

                continue

            # --------------------------------------------------
            # Sentiment analysis
            # --------------------------------------------------

            cryptobert = analyze_crypto_sentiment(
                text
            )

            finbert = analyze_finbert_sentiment(
                text
            )

            # --------------------------------------------------
            # Profile lookup
            # --------------------------------------------------

            author_val = tweet.get(
                "author",
                ""
            )

            if isinstance(
                author_val,
                str
            ):

                username = author_val.lower()

            else:

                username = author_val.get(
                    "userName",
                    ""
                ).lower()

            profile = profiles.get(
                username
            )

            # --------------------------------------------------
            # Account creation time
            # --------------------------------------------------

            account_created_at = None
            raw_creation_time = None

            if (
                profile is not None
                and getattr(
                    profile,
                    "account_created_at",
                    None
                )
            ):

                raw_creation_time = (
                    profile.account_created_at
                )

            elif tweet.get(
                "account_created_at"
            ):

                raw_creation_time = tweet[
                    "account_created_at"
                ]

            if raw_creation_time:

                try:

                    account_created_at = (
                        parse_tweet_timestamp(
                            raw_creation_time
                        )
                    )

                except ValueError:

                    print(
                        f"Could not parse account "
                        f"creation time for "
                        f"@{username}"
                    )

            # --------------------------------------------------
            # Social influence
            # --------------------------------------------------

            if (
                profile is not None
                and getattr(
                    profile,
                    "is_known",
                    False
                )
            ):

                social_score = (
                    calculate_social_influence(
                        followers=tweet.get(
                            "followers",
                            0
                        ),

                        likes=tweet.get(
                            "likes",
                            0
                        ),

                        retweets=tweet.get(
                            "retweets",
                            0
                        ),

                        account_created_at=(
                            account_created_at
                        ),

                        following=getattr(
                            profile,
                            "following",
                            0
                        ),

                        total_tweets=getattr(
                            profile,
                            "statuses_count",
                            0
                        ),

                        is_verified=getattr(
                            profile,
                            "is_verified",
                            False
                        )
                    )
                )

                profile_data_used = True

            else:

                social_score = (
                    calculate_social_influence(
                        followers=tweet.get(
                            "followers",
                            0
                        ),

                        likes=tweet.get(
                            "likes",
                            0
                        ),

                        retweets=tweet.get(
                            "retweets",
                            0
                        ),

                        is_verified=tweet.get(
                            "verified",
                            False
                        )
                    )
                )

                profile_data_used = False

            # --------------------------------------------------
            # Signal strength
            # --------------------------------------------------

            signal_strength_score = (
                calculate_signal_strength(
                    social_score,
                    cryptobert.get(
                        "confidence",
                        0.0
                    )
                )
            )

            # --------------------------------------------------
            # Parse tweet timestamp
            # --------------------------------------------------

            timestamp = parse_tweet_timestamp(
                tweet["timestamp"]
            )

            # --------------------------------------------------
            # Calculate tweet age
            # --------------------------------------------------

            age_minutes = (
                datetime.now(
                    timezone.utc
                ) - timestamp
            ).total_seconds() / 60

            # --------------------------------------------------
            # Market reaction
            # --------------------------------------------------

            market_reaction = {}

            if age_minutes >= 60:

                try:

                    reaction = (
                        calculate_price_reaction(
                            primary_asset,
                            tweet["timestamp"]
                        )
                    )

                    market_reaction[
                        primary_asset
                    ] = reaction

                except Exception as error:

                    market_reaction[
                        primary_asset
                    ] = {
                        "status": "unavailable",
                        "error": str(error)
                    }

            else:

                market_reaction = {
                    primary_asset: {
                        "status": "pending",
                        "message": (
                            "Market reaction will be "
                            "available after 1 hour."
                        )
                    }
                }

            # --------------------------------------------------
            # Build complete analysis result
            # --------------------------------------------------

            analysis_result = {

                "tweet": tweet,

                "processed_text": text,

                "assets": {
                    "primary": primary_asset,
                    "mentioned": mentioned_assets
                },

                "sentiment": {

                    "cryptobert": cryptobert,

                    "finbert": finbert

                },

                "social_influence": {

                    "score": social_score,

                    "signal_strength": (
                        signal_strength_score
                    ),

                    "followers": tweet.get(
                        "followers",
                        0
                    ),

                    "likes": tweet.get(
                        "likes",
                        0
                    ),

                    "retweets": tweet.get(
                        "retweets",
                        0
                    ),

                    "following": getattr(
                        profile,
                        "following",
                        tweet.get(
                            "following"
                        )
                    ),

                    "total_tweets": getattr(
                        profile,
                        "statuses_count",
                        tweet.get(
                            "total_tweets"
                        )
                    ),

                    "account_created_at": (
                        account_created_at.isoformat()
                        if account_created_at
                        else tweet.get(
                            "account_created_at"
                        )
                    ),

                    "verified": getattr(
                        profile,
                        "is_verified",
                        tweet.get(
                            "verified",
                            False
                        )
                    ),

                    "blue_verified": tweet.get(
                        "blue_verified",
                        False
                    ),

                    "profile_data_used": (
                        profile_data_used
                    )
                },

                "signal_strength": (
                    signal_strength_score
                ),

                "market_reaction": (
                    market_reaction
                )
            }

            # --------------------------------------------------
            # Save analysis to SQLite
            # --------------------------------------------------

            save_analysis(
                analysis_result
            )

            # --------------------------------------------------
            # Add to returned results
            # --------------------------------------------------

            results.append(
                analysis_result
            )

            print(
                f"Saved: "
                f"@{username} | "
                f"{primary_asset} | "
                f"Signal "
                f"{signal_strength_score:.2f}"
            )

        print(
            f"\nFinished analysis."
        )

        print(
            f"Successfully analyzed and saved: "
            f"{len(results)} posts"
        )

        return results

    finally:

        connection.close()


def run_continuous_ingestion(
    interval_seconds: int = 600,
    batch_size: int = 20,
):
    """
    Continuously fetch and analyze new crypto tweets.

    interval_seconds=600 means every 10 minutes.
    """

    initialize_database()

    query = (
        "(Bitcoin OR BTC OR Ethereum OR ETH "
        "OR Solana OR SOL OR XRP OR Dogecoin OR DOGE "
        "OR Cardano OR ADA) "
        "lang:en -filter:replies"
    )

    print("=" * 70)
    print("CryptoPulse continuous ingestion started")
    print("Interval: 10 minutes")
    print("=" * 70)

    while True:

        try:

            print("\n" + "=" * 70)
            print("Fetching latest crypto tweets...")
            print("=" * 70)

            tweets = fetch_tweets_with_pagination(
                query=query,
                target_count=batch_size,
            )

            # --------------------------------------------------
            # Remove tweets already stored in SQLite
            # --------------------------------------------------

            new_tweets = []

            for tweet in tweets:

                tweet_id = tweet.get("id")

                if not tweet_id:
                    continue

                if tweet_exists(str(tweet_id)):
                    continue

                new_tweets.append(tweet)

            print(
                f"Fetched: {len(tweets)} tweets"
            )

            print(
                f"New tweets: {len(new_tweets)}"
            )

            if new_tweets:

                # --------------------------------------------------
                # Analyze only NEW tweets
                # --------------------------------------------------

                analyze_live_tweets(
    query=query,
    tweets_override=new_tweets,
)

            else:

                print(
                    "No new tweets to analyze."
                )

            print(
                "\nNext ingestion in 10 minutes..."
            )

            time.sleep(
                interval_seconds
            )

        except KeyboardInterrupt:

            print(
                "\nContinuous ingestion stopped."
            )

            break

        except Exception as error:

            print(
                "\nIngestion error:"
            )

            print(
                str(error)
            )

            print(
                "Retrying in 10 minutes..."
            )

            time.sleep(
                interval_seconds
            )        


# ============================================================
# Backfill test / database population
# ============================================================

if __name__ == "__main__":
    initialize_database()

    query = (
        "(Bitcoin OR BTC OR Ethereum OR ETH "
        "OR Solana OR SOL OR XRP OR Dogecoin OR DOGE "
        "OR Cardano OR ADA) "
        "lang:en -filter:replies"
    )

    results = analyze_live_tweets(
        query,
        limit=200
    )