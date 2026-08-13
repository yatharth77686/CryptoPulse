import json
from pathlib import Path

from crypto_detector import is_crypto_related
from crypto_identifer import identify_crypto


def load_posts():
    data_path = Path(__file__).resolve().parents[3] / "data" / "sample_posts.json"

    with open(data_path, "r", encoding="utf-8") as file:
        posts = json.load(file)

    return posts


if __name__ == "__main__":
    posts = load_posts()

    print(f"Loaded {len(posts)} posts\n")

    for post in posts:
        crypto_related = is_crypto_related(post["text"])

        print(f"@{post['author']}")
        print(f"Post: {post['text']}")
        print(f"Crypto-related: {crypto_related}")

        if crypto_related:
            assets = identify_crypto(post["text"])
            print(f"Detected assets: {assets}")

        print("-" * 50)