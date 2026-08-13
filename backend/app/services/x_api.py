import os
import requests
from dotenv import load_dotenv

load_dotenv()

BEARER_TOKEN = os.getenv("X_BEARER_TOKEN")

url = "https://api.x.com/2/users/by/username/elonmusk"

headers = {
    "Authorization": f"Bearer {BEARER_TOKEN}"
}

response = requests.get(url, headers=headers)

print("Status:", response.status_code)
print(response.json())