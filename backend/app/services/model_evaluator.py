import json
from pathlib import Path

from sklearn.metrics import accuracy_score, precision_recall_fscore_support

from crypto_sentiment import analyze_crypto_sentiment
from finbert_sentiment import analyze_finbert_sentiment


DATA_PATH = (
    Path(__file__).resolve().parents[3]
    / "data"
    / "sentiment_test.json"
)


def load_test_data():
    with open(DATA_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def normalize_cryptobert(label):
    label = label.lower()

    mapping = {
        "bullish": "bullish",
        "neutral": "neutral",
        "bearish": "bearish"
    }

    return mapping.get(label, label)


def normalize_finbert(label):
    label = label.lower()

    mapping = {
        "positive": "bullish",
        "neutral": "neutral",
        "negative": "bearish"
    }

    return mapping.get(label, label)


def evaluate_model(y_true, y_pred):
    accuracy = accuracy_score(y_true, y_pred)

    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true,
        y_pred,
        average="weighted",
        zero_division=0
    )

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1
    }


if __name__ == "__main__":
    test_data = load_test_data()

    actual = []

    cryptobert_predictions = []
    finbert_predictions = []

    print(f"Evaluating {len(test_data)} posts...\n")

    for item in test_data:
        text = item["text"]
        actual_sentiment = item["actual_sentiment"]

        crypto_result = analyze_crypto_sentiment(text)
        finbert_result = analyze_finbert_sentiment(text)

        crypto_prediction = normalize_cryptobert(
            crypto_result["sentiment"]
        )

        finbert_prediction = normalize_finbert(
            finbert_result["sentiment"]
        )

        actual.append(actual_sentiment)
        cryptobert_predictions.append(crypto_prediction)
        finbert_predictions.append(finbert_prediction)

        print(f"Post: {text}")
        print(f"Actual:      {actual_sentiment}")
        print(f"CryptoBERT:  {crypto_prediction}")
        print(f"FinBERT:     {finbert_prediction}")
        print("-" * 70)

    cryptobert_metrics = evaluate_model(
        actual,
        cryptobert_predictions
    )

    finbert_metrics = evaluate_model(
        actual,
        finbert_predictions
    )

    print("\nMODEL COMPARISON")
    print("=" * 70)

    print("\nCryptoBERT")
    print(f"Accuracy:  {cryptobert_metrics['accuracy']:.3f}")
    print(f"Precision: {cryptobert_metrics['precision']:.3f}")
    print(f"Recall:    {cryptobert_metrics['recall']:.3f}")
    print(f"F1 Score:  {cryptobert_metrics['f1']:.3f}")

    print("\nFinBERT")
    print(f"Accuracy:  {finbert_metrics['accuracy']:.3f}")
    print(f"Precision: {finbert_metrics['precision']:.3f}")
    print(f"Recall:    {finbert_metrics['recall']:.3f}")
    print(f"F1 Score:  {finbert_metrics['f1']:.3f}")

    if cryptobert_metrics["f1"] > finbert_metrics["f1"]:
        winner = "CryptoBERT"
        winner_f1 = cryptobert_metrics["f1"]

    elif finbert_metrics["f1"] > cryptobert_metrics["f1"]:
        winner = "FinBERT"
        winner_f1 = finbert_metrics["f1"]

    else:
        winner = "Tie"
        winner_f1 = cryptobert_metrics["f1"]

    print("\nMODEL SELECTION")
    print("=" * 70)

    if winner == "Tie":
        print("Result: Both models have the same F1 score.")
    else:
        print(f"Selected model: {winner}")
        print(f"F1 Score: {winner_f1:.3f}")
    