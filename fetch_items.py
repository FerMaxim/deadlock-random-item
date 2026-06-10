import requests
import json
import urllib.request

urls = [
    "https://api.deadlock-api.com/v1/items",
    "https://assets.deadlock-api.com/v1/items",
    "https://api.deadlock-api.com/v1/assets/items"
]

for url in urls:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            print(f"SUCCESS {url}: got {len(data)} items")
            with open("api_response.json", "w") as f:
                json.dump(data, f)
            break
    except Exception as e:
        print(f"FAIL {url}: {e}")
