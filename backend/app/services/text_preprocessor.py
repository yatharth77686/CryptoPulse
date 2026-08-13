import re



def preprocess_tweet(text: str) -> str:
    """
    Clean X/Twitter text while preserving
    sentiment-relevant information.
    """

    # Remove URLs
    text = re.sub(r"https?://\S+|www\.\S+", "", text)

    # Remove HTML tags
    text = re.sub(r"<.*?>", "", text)

    # Normalize mentions but keep the fact that a mention existed
    text = re.sub(r"@\w+", "@user", text)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    # Limit excessive repeated punctuation
    text = re.sub(r"!{3,}", "!!", text)
    text = re.sub(r"\?{3,}", "??", text)

    # Limit excessive repeated characters
    text = re.sub(r"(.)\1{4,}", r"\1\1\1", text)

    return text.strip()


if __name__ == "__main__":

    test_text = (
        "@crypto_user BTC is going 🚀🚀🚀!!! "
        "https://example.com #Bitcoin"
    )

    cleaned = preprocess_tweet(test_text)

    print("Original:")
    print(test_text)

    print("\nProcessed:")
    print(cleaned)