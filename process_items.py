import json
import urllib.parse

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
    
    # Generate placehold.co URL based on category
    text_encoded = urllib.parse.quote(name.replace(" ", "\\n"))
    
    if slot_type == "Weapon":
        img_url = f"https://placehold.co/200x250/2b2519/d3783a?text={text_encoded}"
    elif slot_type == "Vitality":
        img_url = f"https://placehold.co/200x250/192b1a/5ebd40?text={text_encoded}"
    else: # Spirit
        img_url = f"https://placehold.co/200x250/271d2b/b976d9?text={text_encoded}"

    processed.append({
        "id": item.get('id'),
        "name": name,
        "price": cost,
        "category": slot_type,
        "description": desc,
        "image": img_url
    })

# Write to data.json
with open('data.json', 'w') as f:
    json.dump(processed, f, indent=2)

print(f"Successfully processed {len(processed)} items with placehold images.")
