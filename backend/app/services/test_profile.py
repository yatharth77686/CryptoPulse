import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("TWITTERAPI_IO_KEY")

username = "H2theizzo_28"

response = requests.get(
    "https://api.twitterapi.io/twitter/user/info",
    headers={
        "X-API-Key": API_KEY
    },
    params={
        "userName": username
    },
    timeout=10
)

response.raise_for_status()

profile = response.json()

print("\nPROFILE RESPONSE")
print("=" * 70)

print(profile)