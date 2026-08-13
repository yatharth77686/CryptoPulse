import os
import requests
from dotenv import load_dotenv

load_dotenv()

TWITTERAPI_IO_KEY = os.getenv("TWITTERAPI_IO_KEY")

BASE_URL = "https://api.twitterapi.io"


def search_tweets(
    query: str,
    query_type: str = "Latest",
    cursor: str | None = None,
):
    """
    Search tweets using TwitterAPI.io Advanced Search.

    TwitterAPI.io returns up to 20 tweets per page and provides
    a cursor for fetching additional pages.

    The cursor is optional. The first request is made without it;
    subsequent requests can provide next_cursor returned by the API.
    """

    if not TWITTERAPI_IO_KEY:
        raise ValueError(
            "TWITTERAPI_IO_KEY is not set in .env"
        )

    if query_type.lower() == "popular":
        query_type = "Top"
    else:
        query_type = "Latest"

    params = {
        "query": query,
        "queryType": query_type,
    }

    if cursor:
        params["cursor"] = cursor

    response = requests.get(
        f"{BASE_URL}/twitter/tweet/advanced_search",
        headers={
            "X-API-Key": TWITTERAPI_IO_KEY,
        },
        params=params,
        timeout=15,
    )

    response.raise_for_status()

    data = response.json()

    tweets = []

    for tweet in data.get("tweets", []):

        author = tweet.get("author") or {}

        converted_tweet = {
            "id": tweet.get("id"),

            "text": tweet.get(
                "text",
                ""
            ),

            "author": {
                "userName": author.get(
                    "userName",
                    "unknown"
                ),

                "followers": author.get(
                    "followers",
                    0
                ),

                "following": author.get(
                    "following",
                    0
                ),

                "statusesCount": author.get(
                    "statusesCount",
                    0
                ),

                "createdAt": author.get(
                    "createdAt"
                ),

                "isVerified": author.get(
                    "isVerified",
                    False
                ),

                "isBlueVerified": author.get(
                    "isBlueVerified",
                    False
                ),
            },

            "likeCount": tweet.get(
                "likeCount",
                0
            ),

            "retweetCount": tweet.get(
                "retweetCount",
                0
            ),

            "createdAt": tweet.get(
                "createdAt"
            ),
        }

        tweets.append(
            converted_tweet
        )

    return {
        "tweets": tweets,

        "next_cursor": data.get(
            "next_cursor"
        ),

        "has_next_page": data.get(
            "has_next_page",
            False
        ),
    }


# ============================================================
# Direct API test
# ============================================================

if __name__ == "__main__":

    results = search_tweets(
        "Bitcoin OR BTC lang:en",
        "Latest"
    )

    tweets = results.get(
        "tweets",
        []
    )

    print(
        f"Retrieved {len(tweets)} tweets"
    )

    print(
        "Has next page:",
        results.get("has_next_page")
    )

    print(
        "Next cursor:",
        bool(results.get("next_cursor"))
    )

    for tweet in tweets[:5]:

        print("\n---")

        print(
            "ID:",
            tweet.get("id")
        )

        print(
            "Author:",
            tweet.get(
                "author",
                {}
            ).get(
                "userName"
            )
        )

        print(
            "Text:",
            tweet.get(
                "text",
                ""
            )
        )

        print(
            "Likes:",
            tweet.get(
                "likeCount",
                0
            )
        )

        print(
            "Retweets:",
            tweet.get(
                "retweetCount",
                0
            )
        )

        print(
            "Timestamp:",
            tweet.get(
                "createdAt"
            )
        )