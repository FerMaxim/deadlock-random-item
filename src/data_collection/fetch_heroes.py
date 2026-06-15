import requests
import json

try:
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    r = requests.get('https://api.deadlock-api.com/v1/assets/heroes', headers=headers)
    data = r.json()
    heroes = {h['id']: h['name'] for h in data}
    with open('data/reference/heroes.json', 'w', encoding='utf-8') as f:
        json.dump(heroes, f, ensure_ascii=False, indent=2)
    print("Success. Found", len(heroes), "heroes.")
except Exception as e:
    print("Failed:", e)
    if 'r' in locals():
        print(r.text[:500])
