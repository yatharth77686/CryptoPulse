def normalize_tweet(tweet: dict, profiles=None) -> dict:
    """
    Convert a TwitterAPI.io tweet into the
    internal CryptoPulse format.

    Profile data comes from the persistent profile cache.
    """

    profiles = profiles or {}

    user = tweet.get("author", {})

    username = user.get(
        "userName",
        "unknown"
    )

    profile = profiles.get(
        username.lower()
    )

    # --------------------------------------------------
    # Tweet-level data
    # --------------------------------------------------

    result = {
        "tweet_id": tweet.get("id"),
        "text": tweet.get("text", "").strip(),
        "author": username,

        # Tweet-level fallback
        "followers": user.get("followers", 0),
        "likes": tweet.get("likeCount", 0),
        "retweets": tweet.get("retweetCount", 0),

        "timestamp": tweet.get("createdAt"),

        # Profile data
        "account_created_at": None,
        "following": None,
        "total_tweets": None,
        "verified": False,
        "blue_verified": False,
        "profile_data_used": False,
    }

    # --------------------------------------------------
    # Use ProfileResult when available
    # --------------------------------------------------

    if profile is not None and profile.is_known:

        if profile.followers is not None:
            result["followers"] = profile.followers

        result["account_created_at"] = (
            profile.account_created_at
        )

        result["following"] = (
            profile.following
        )

        result["total_tweets"] = (
            profile.statuses_count
        )

        result["verified"] = (
            profile.is_verified
        )

        result["blue_verified"] = (
            profile.is_blue_verified
        )

        result["profile_data_used"] = True

    return result


def normalize_tweets(
    tweets: list[dict],
    profiles=None
) -> list[dict]:

    results = []

    for tweet in tweets:

        normalized = normalize_tweet(
            tweet,
            profiles
        )

        if not normalized["text"]:
            continue

        results.append(normalized)

    return results


if __name__ == "__main__":

    sample_tweet = {
        "id": "123",
        "text": "Bitcoin looks extremely bullish today!",
        "author": {
            "userName": "crypto_user",
            "followers": 125000
        },
        "likeCount": 4200,
        "retweetCount": 850,
        "createdAt": "2026-08-12T00:30:00Z"
    }

    result = normalize_tweet(
        sample_tweet
    )

    print(result)