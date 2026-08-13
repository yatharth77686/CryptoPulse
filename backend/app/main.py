from fastapi import FastAPI, HTTPException
import json
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.app.schemas import (
    APIStatus,
    SentimentSummary,
    CryptoAnalysisResponse,
    MarketReactionResponse,
    AnalyzeRequest,
    AnalyzeResponse,
)
from backend.app.services.live_analyzer import (
    analyze_live_tweets,
    fetch_tweets_with_pagination,
)

from backend.app.services.crypto_detector import (
    is_crypto_related
)

from backend.app.services.crypto_identifer import (
    identify_crypto
)

from backend.app.services.crypto_sentiment import (
    analyze_crypto_sentiment
)

from backend.app.services.finbert_sentiment import (
    analyze_finbert_sentiment
)

from backend.app.services.market_data import (
    calculate_price_reaction
)

from backend.app.services.social_influence import (
    calculate_social_influence,
    calculate_signal_strength,
)

from backend.app.services.database import (
    get_all_analyses,
    initialize_database,
    tweet_exists,
)


INGESTION_INTERVAL = 600  # 10 minutes


async def continuous_ingestion():
    """
    Background CryptoPulse ingestion worker.

    Runs immediately when the backend starts and then
    every 10 minutes.
    """

    query = (
        "(Bitcoin OR BTC OR Ethereum OR ETH "
        "OR Solana OR SOL OR XRP OR Dogecoin OR DOGE "
        "OR Cardano OR ADA) "
        "lang:en -filter:replies"
    )

    print("=" * 70)
    print("CryptoPulse live ingestion worker started")
    print("Interval: 10 minutes")
    print("=" * 70)

    while True:

        try:

            print("\n[INGESTION] Fetching latest tweets...")

            tweets = fetch_tweets_with_pagination(
                query=query,
                target_count=20,
            )

            new_tweets = []

            for tweet in tweets:

                tweet_id = tweet.get("id")

                if not tweet_id:
                    continue

                if tweet_exists(str(tweet_id)):
                    continue

                new_tweets.append(tweet)

            print(
                f"[INGESTION] "
                f"Fetched={len(tweets)} "
                f"New={len(new_tweets)}"
            )

            if new_tweets:

                await asyncio.to_thread(
                    analyze_live_tweets,
                    query,
                    len(new_tweets),
                    new_tweets,
                )

                print(
                    f"[INGESTION] "
                    f"Analyzed {len(new_tweets)} new tweets."
                )

            else:

                print(
                    "[INGESTION] No new tweets."
                )

        except Exception as error:

            print(
                f"[INGESTION] Error: {error}"
            )

        print(
            "[INGESTION] Sleeping for 10 minutes..."
        )

        await asyncio.sleep(
            INGESTION_INTERVAL
        )

# ============================================================
# FastAPI application
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    initialize_database()

    ingestion_task = asyncio.create_task(
        continuous_ingestion()
    )

    try:

        yield

    finally:

        ingestion_task.cancel()

        try:
            await ingestion_task
        except asyncio.CancelledError:
            pass


app = FastAPI(
    title="CryptoPulse API",
    description="AI-powered social media crypto intelligence system",
    version="1.0.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Helpers
# ============================================================

def parse_json_field(value, default=None):
    """
    Safely parse JSON fields coming from SQLite.
    """

    if value is None:
        return default if default is not None else {}

    if isinstance(value, (dict, list)):
        return value

    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return default if default is not None else {}


def format_analysis_result(result: dict) -> dict:
    """
    Convert the raw SQLite analysis record into the
    clean API structure used by the frontend.
    """

    assets = parse_json_field(
        result.get("assets"),
        {}
    )

    market_reaction = parse_json_field(
        result.get("market_reaction"),
        {}
    )

    # Normalize assets into a consistent structure
    if isinstance(assets, dict):
        asset_info = {
            "primary": assets.get("primary"),
            "mentioned": assets.get("mentioned", []),
        }

    elif isinstance(assets, list):
        asset_info = {
            "primary": assets[0] if assets else None,
            "mentioned": assets[1:] if len(assets) > 1 else [],
        }

    else:
        asset_info = {
            "primary": None,
            "mentioned": [],
        }

    return {
        "id": result.get("id"),

        "tweet_id": result.get(
            "tweet_id"
        ),

        "author": result.get(
            "author"
        ),

        "text": result.get(
            "text"
        ),

        "timestamp": result.get(
            "timestamp"
        ),
        "assets": asset_info,
        "sentiment": {
            "cryptobert": {
                "label": result.get(
                    "cryptobert_label"
                ),
                "confidence": result.get(
                    "cryptobert_confidence"
                )
            },

            "finbert": {
                "label": result.get(
                    "finbert_label"
                ),
                "confidence": result.get(
                    "finbert_confidence"
                )
            }
        },

        "social_influence": {
            "score": result.get(
                "influence_score"
            ),

            "followers": result.get(
                "followers",
                0
            ),

            "likes": result.get(
                "likes",
                0
            ),

            "retweets": result.get(
                "retweets",
                0
            )
        },

        "signal_strength": result.get(
            "signal_strength"
        ),

        "market_reaction": market_reaction
    }    


def load_database_results():
    """
    Load analysis records from SQLite and convert
    them into the clean API representation.
    """

    results = get_all_analyses()

    return [
        format_analysis_result(result)
        for result in results
    ]

# ============================================================
# Root
# ============================================================

@app.get(
    "/",
    response_model=APIStatus
)
def root():

    return {
        "message": "CryptoPulse API is running",
        "status": "online"
    }


# ============================================================
# All analyses
# ============================================================

@app.get("/analysis")
def get_analysis():

    results = load_database_results()

    return {
        "count": len(results),
        "results": results
    }


# ============================================================
# Manual text analysis
# ============================================================

@app.post(
    "/analyze",
    response_model=AnalyzeResponse
)
def analyze_text(
    request: AnalyzeRequest
):

    text = request.text

    # --------------------------------------------------------
    # Crypto relevance check
    # --------------------------------------------------------

    if not is_crypto_related(text):

        raise HTTPException(
            status_code=400,
            detail=(
                "The provided text does not appear "
                "to be crypto-related."
            )
        )


    # --------------------------------------------------------
    # Identify cryptocurrencies
    # --------------------------------------------------------

    assets = identify_crypto(text)

    if not assets:

        raise HTTPException(
            status_code=400,
            detail="No cryptocurrency could be identified."
        )


    # --------------------------------------------------------
    # Sentiment
    # --------------------------------------------------------

    cryptobert = analyze_crypto_sentiment(text)

    finbert = analyze_finbert_sentiment(text)


    # --------------------------------------------------------
    # Social influence
    # --------------------------------------------------------

    social_score = calculate_social_influence(
    followers=request.followers,
    likes=request.likes,
    retweets=request.retweets
)



    
    # --------------------------------------------------------
# Signal strength
# --------------------------------------------------------
    signal_strength_score = calculate_signal_strength(
    social_score,
    cryptobert.get("confidence", 0.0)
)

   



    # --------------------------------------------------------
    # Market reaction
    #
    # Manual analysis currently calculates the reaction
    # immediately because a timestamp is supplied.
    # --------------------------------------------------------

    market_reaction = {}

    for asset in assets:

     try:
        reaction = calculate_price_reaction(
            asset,
            request.timestamp.isoformat()
        )

        market_reaction[asset] = reaction

     except (ValueError, Exception) as error:

        market_reaction[asset] = {
            "status": "unavailable",
            "message": str(error)
        }


    # --------------------------------------------------------
    # Return
    # --------------------------------------------------------

    return {
    "text": text,

    "assets": {
        "primary": assets[0] if assets else None,
        "mentioned": assets[1:] if len(assets) > 1 else []
    },

    "sentiment": {
        "cryptobert": {
            "label": cryptobert["sentiment"],
            "confidence": cryptobert["confidence"]
        },

        "finbert": {
            "label": finbert["sentiment"],
            "confidence": finbert["confidence"]
        }
    },

    "social_influence": {
        "score": social_score,
        "followers": request.followers,
        "likes": request.likes,
        "retweets": request.retweets
    },

    "signal_strength": signal_strength_score,

    "market_reaction": market_reaction
}


# ============================================================
# Cryptocurrency analysis
# ============================================================

@app.get(
    "/crypto/{symbol}",
    response_model=CryptoAnalysisResponse
)
def get_crypto(
    symbol: str
):

    symbol = symbol.upper()

    results = load_database_results()

    matching_posts = []


    for result in results:

        assets = result.get(
            "assets",
            {}
        )


        # Current live analyzer stores:
        #
        # {
        #     "primary": "BTC",
        #     "mentioned": ["ETH"]
        # }

        if isinstance(assets, dict):

            primary = assets.get(
                "primary"
            )

            mentioned = assets.get(
                "mentioned",
                []
            )

            if (
                primary == symbol
                or symbol in mentioned
            ):
                matching_posts.append(result)


        # Also support a simple list if an older
        # record exists.

        elif isinstance(assets, list):

            if symbol in assets:
                matching_posts.append(result)


    if not matching_posts:

        raise HTTPException(
            status_code=404,
            detail=f"No analysis found for {symbol}"
        )


    return {
        "symbol": symbol,
        "count": len(matching_posts),
        "results": matching_posts
    }


# ============================================================
# Sentiment summary
# ============================================================

@app.get(
    "/sentiment",
    response_model=SentimentSummary
)
def get_sentiment_summary():

    results = load_database_results()


    summary = {
        "bullish": 0,
        "bearish": 0,
        "neutral": 0
    }


    for result in results:

        # Current database stores the label directly
        # in cryptobert_label.

        label = result.get(
            "cryptobert_label"
        )


        if not label:
            continue


        label = label.lower()


        if label in summary:
            summary[label] += 1


    return {

        "model": "CryptoBERT",

        "summary": summary,

        "total_posts": len(results)

    }


# ============================================================
# Market reaction
# ============================================================

@app.get(
    "/market/{symbol}",
    response_model=MarketReactionResponse
)
def get_market_reaction(
    symbol: str
):

    symbol = symbol.upper()

    results = load_database_results()

    reactions = []


    for result in results:
        market_data = result.get(
            "market_reaction",
            {}
        )

        # Handle JSON stored as a string in SQLite
        if isinstance(market_data, str):
            try:
                market_data = json.loads(market_data)
            except json.JSONDecodeError:
                continue

        reaction = market_data.get(symbol)

        if reaction is None:
            continue

        reactions.append({
            "post_id": result.get("tweet_id"),
            "timestamp": result.get("timestamp"),
            "sentiment": result.get("sentiment", {}),
            "reaction": reaction,
            "social_influence": result.get("influence_score"),
            "signal_strength": result.get("signal_strength")
        })

    if not reactions:
        raise HTTPException(
            status_code=404,
            detail=(
                f"No market reaction found for {symbol}"
            )
        )

    return {
        "symbol": symbol,
        "count": len(reactions),
        "reactions": reactions
    }