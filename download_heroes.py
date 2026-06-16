import json
import os
import urllib.request

heroes_dict = {
    "Infernus": "1",
    "Seven": "2",
    "Vindicta": "3",
    "Lady geist": "4",
    "Abrams": "6",
    "Wraith": "7",
    "Mcginnis": "8",
    "Paradox": "10",
    "Dynamo": "11",
    "Kelvin": "12",
    "Haze": "13",
    "Holliday": "14",
    "Bebop": "15",
    "Calico": "16",
    "Grey talon": "17",
    "Mo & krill": "18",
    "Shiv": "19",
    "Ivy": "20",
    "Kali": "21",
    "Warden": "25",
    "Yamato": "27",
    "Lash": "31",
    "Viscous": "35",
    "The boss": "39",
    "Tokamak": "47",
    "Wrecker": "48",
    "Rutger": "49",
    "Pocket": "50",
    "Thumper": "51",
    "Mirage": "52",
    "Cadence": "54",
    "Bomber": "56",
    "Shield guy": "57",
    "Vyper": "58",
    "Vandal": "59",
    "Sinclair": "60",
    "Trapper": "61",
    "Mina": "63"
}

output_dir = r"d:\CODE\DeadlockRandomItem\DownloadedImages\heroes"
os.makedirs(output_dir, exist_ok=True)

# Fetch heroes list from API
req = urllib.request.Request('https://assets.deadlock-api.com/v2/heroes', headers={'User-Agent': 'Mozilla/5.0'})
print("Fetching heroes data from API...")
try:
    with urllib.request.urlopen(req, timeout=15) as response:
        heroes_data = json.loads(response.read().decode('utf-8'))
except Exception as e:
    print(f"Failed to fetch API: {e}")
    exit(1)

# Map lowercased names to their image URL
api_hero_images = {}
for h in heroes_data:
    name_lower = h['name'].lower()
    # Use icon_hero_card for a nice portrait, or icon_image_small
    img_url = h.get('images', {}).get('icon_hero_card') 
    if not img_url:
         img_url = h.get('images', {}).get('icon_image_small')
    if img_url:
        api_hero_images[name_lower] = img_url

success_count = 0
missing_count = 0

for name, hid in heroes_dict.items():
    name_lower = name.lower()
    img_url = api_hero_images.get(name_lower)
    
    if img_url:
        local_path = os.path.join(output_dir, f"{hid}.png")
        print(f"Downloading {name} -> {hid}.png...")
        try:
            req_img = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req_img, timeout=15) as response:
                content = response.read()
                with open(local_path, 'wb') as out_file:
                    out_file.write(content)
            success_count += 1
        except Exception as e:
            print(f"  Error downloading {name}: {e}")
            missing_count += 1
    else:
        print(f"  Image not found in API for {name}")
        missing_count += 1

print("\n--- STATISTICS ---")
print(f"Successfully downloaded: {success_count}")
print(f"Missing or failed: {missing_count}")
