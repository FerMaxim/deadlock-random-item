import json
import os
import urllib.request
import re

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

with open('api_response.json', 'r', encoding='utf-8') as f:
    raw_data = json.load(f)

base_dir = os.path.join(os.getcwd(), 'DownloadedImages')
os.makedirs(base_dir, exist_ok=True)

total_items = 0
success_count = 0
missing_items = []

for item in raw_data:
    if not item.get('shopable', False):
        continue
    
    cost = item.get('cost', 0)
    if cost not in [800, 1600, 3200, 6400]:
        continue
        
    slot_type = item.get('item_slot_type', '').capitalize()
    if slot_type not in ['Weapon', 'Vitality', 'Spirit']:
        continue
        
    name = item.get('name', 'Unknown')
    remote_img = item.get('shop_image') or item.get('image')
    
    if remote_img:
        cat_dir = os.path.join(base_dir, slot_type)
        os.makedirs(cat_dir, exist_ok=True)
        
        safe_name = sanitize_filename(name)
        ext = remote_img.split('.')[-1]
        local_path = os.path.join(cat_dir, f"{safe_name}.{ext}")
        
        total_items += 1
        
        # Check if file exists and has content (not 0 bytes)
        if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
            success_count += 1
            continue
            
        try:
            print(f"Downloading {name} ({slot_type})...")
            req = urllib.request.Request(remote_img, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as response:
                content = response.read()
                with open(local_path, 'wb') as out_file:
                    out_file.write(content)
            success_count += 1
        except Exception as e:
            print(f"Error downloading {name}: {e}")
            missing_items.append(f"{name} ({slot_type})")
            if os.path.exists(local_path):
                os.remove(local_path) # cleanup empty file
    else:
        total_items += 1
        missing_items.append(f"{name} ({slot_type}) - NO URL IN API")

print("\n--- STATISTICS ---")
print(f"Total valid items found in API: {total_items}")
print(f"Successfully downloaded/exist: {success_count}")
print(f"Missing or failed: {len(missing_items)}")

if missing_items:
    print("\n--- MISSING ITEMS ---")
    for m in missing_items:
        print(f"- {m}")
