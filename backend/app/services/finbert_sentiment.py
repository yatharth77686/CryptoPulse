from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    pipeline
)


MODEL_NAME = "ProsusAI/finbert"


tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME
)

model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME,
    use_safetensors=True
)

sentiment_pipeline = pipeline(
    "text-classification",
    model=model,
    tokenizer=tokenizer
)


def analyze_finbert_sentiment(text):
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
        result = analyze_finbert_sentiment(post)

        print(f"Post: {post}")
        print(f"Sentiment: {result['sentiment']}")
        print(f"Confidence: {result['confidence']}")
        print("-" * 60)