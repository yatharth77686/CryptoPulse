from transformers import pipeline


MODEL_NAME = "ElKulako/cryptobert"


sentiment_pipeline = pipeline(
    "text-classification",
    model=MODEL_NAME,
    tokenizer=MODEL_NAME
)


def analyze_crypto_sentiment(text):
    result = sentiment_pipeline(
    text,
    truncation=True,
    max_length=512
)[0]


    return {
        "sentiment": result["label"],
        "confidence": round(result["score"], 4)
    }

if __name__ == "__main__":
    test_posts = [
        "Bitcoin is breaking resistance and this could be a huge move!",
        "The crypto market is collapsing and investors are extremely worried.",
        "Bitcoin traded sideways today with very little movement.",
        "Dogecoin adoption could increase significantly this year."
    ]

    for post in test_posts:
        result = analyze_crypto_sentiment(post)

        print(f"Post: {post}")
        print(f"Sentiment: {result['sentiment']}")
        print(f"Confidence: {result['confidence']}")
        print("-" * 60)