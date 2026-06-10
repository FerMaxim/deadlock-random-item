import json
import urllib.parse
import os
import urllib.request

# Create images directory
img_dir = os.path.join('randomizer', 'static', 'randomizer', 'images', 'items')
os.makedirs(img_dir, exist_ok=True)

with open('api_response.json', 'r') as f:
    raw_data = json.load(f)

processed = []

for item in raw_data:
    if not item.get('shopable', False):
        continue
    
    cost = item.get('cost', 0)
    if cost not in [800, 1600, 3200, 6400]:
        continue
        
    slot_type = item.get('item_slot_type', '').capitalize()
    if slot_type not in ['Weapon', 'Vitality', 'Spirit']:
        continue
        
    desc_lines = []
    props = item.get('properties', {})
    for prop_name, prop_data in props.items():
        if isinstance(prop_data, dict) and 'label' in prop_data and 'value' in prop_data and prop_data['value'] != "0" and prop_data['value'] != "-1":
            prefix = prop_data.get('prefix', '').replace('{s:sign}', '+')
            postfix = prop_data.get('postfix', '')
            val = prop_data['value']
            label = prop_data['label']
            desc_lines.append(f"{prefix}{val}{postfix} {label}")
            
    desc = " | ".join(desc_lines) if desc_lines else "No specific description."

    name = item.get('name', 'Unknown')
    item_id = item.get('id')
    
    # Get correct shop image from API
    remote_img = item.get('shop_image') or item.get('image')
    img_url = ""
    
    if remote_img:
        local_img_path = os.path.join(img_dir, f"{item_id}.png")
        if not os.path.exists(local_img_path):
            try:
                print(f"Downloading {name}...")
                req = urllib.request.Request(remote_img, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req) as response:
                    with open(local_img_path, 'wb') as out_file:
                        out_file.write(response.read())
            except Exception as e:
                print(f"Failed to download image for {name}: {e}")
        
        # Whether it downloaded or already existed, point to the local file
        img_url = f"/static/randomizer/images/items/{item_id}.png"
    else:
        # Fallback to placehold.co
        text_encoded = urllib.parse.quote(name.replace(" ", "\\n"))
        if slot_type == "Weapon":
            img_url = f"https://placehold.co/200x250/2b2519/d3783a?text={text_encoded}"
        elif slot_type == "Vitality":
            img_url = f"https://placehold.co/200x250/192b1a/5ebd40?text={text_encoded}"
        else:
            img_url = f"https://placehold.co/200x250/271d2b/b976d9?text={text_encoded}"

    activation = item.get('activation', 'passive')
    is_active = activation in ['press', 'instant_cast_toggle', 'instant_cast']

    processed.append({
        "id": item_id,
        "name": name,
        "price": cost,
        "category": slot_type,
        "description": desc,
        "image": img_url,
        "isActive": is_active
    })

# Write to data.json locally
out_json_path = os.path.join('randomizer', 'static', 'randomizer', 'data.json')
with open(out_json_path, 'w') as f:
    json.dump(processed, f, indent=2)

print(f"Successfully processed {len(processed)} items with local images.")
