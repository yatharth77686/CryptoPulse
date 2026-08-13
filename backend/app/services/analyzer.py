import json
from pathlib import Path

from crypto_detector import is_crypto_related
from crypto_identifer import identify_crypto
from crypto_sentiment import analyze_crypto_sentiment
from finbert_sentiment import analyze_finbert_sentiment
from market_data import calculate_price_reaction


DATA_PATH = (
    Path(__file__).resolve().parents[3]
    / "data"
    / "sample_posts.json"
)

RESULTS_PATH = (
    Path(__file__).resolve().parents[3]
    / "data"
    / "analysis_results.json"
)


def load_posts():
    with open(DATA_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def normalize_finbert(label):
    mapping = {
        "positive": "bullish",
        "negative": "bearish",
        "neutral": "neutral"
    }

    return mapping.get(label.lower(), label.lower())


def analyze_post(post):
    text = post["text"]

    # Step 1: Check whether the post is crypto-related
    if not is_crypto_related(text):
        return None

    # Step 2: Identify cryptocurrency
    assets = identify_crypto(text)

    if not assets:
        return None

    # Step 3: Run both sentiment models
    cryptobert = analyze_crypto_sentiment(text)
    finbert = analyze_finbert_sentiment(text)

    cryptobert_sentiment = cryptobert["sentiment"].lower()
    finbert_sentiment = normalize_finbert(
        finbert["sentiment"]
    )

    # Step 4: Analyze market reaction
    market_reactions = {}

    for asset in assets:
        reaction = calculate_price_reaction(
            asset,
            post["created_at"]
        )

        market_reactions[asset] = reaction

    return {
        "post_id": post["id"],
        "author": post["author"],
        "text": text,
        "timestamp": post["created_at"],
        "assets": assets,
        "sentiment": {
            "cryptobert": {
                "label": cryptobert_sentiment,
                "confidence": cryptobert["confidence"]
            },
            "finbert": {
                "label": finbert_sentiment,
                "confidence": finbert["confidence"]
            }
        },
        "market_reaction": market_reactions
    }

def save_results(results):
    with open(RESULTS_PATH, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=2)

    print(f"\nResults saved to: {RESULTS_PATH}")


if __name__ == "__main__":
    posts = load_posts()

    results = []

    print("=" * 70)
    print("CRYPTOPULSE INTELLIGENCE PIPELINE")
    print("=" * 70)

    for post in posts:
        result = analyze_post(post)

        if result is not None:
            results.append(result)

    save_results(results)

    print("\n" + "=" * 70)
    print(f"Analyzed {len(results)} crypto-related posts")
    print("=" * 70)