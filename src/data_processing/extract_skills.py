import json
import duckdb
import pandas as pd

# Загружаем словарь предметов
with open('data/reference/items.json', 'r', encoding='utf-8') as f:
    items_data = json.load(f)

# Создаем маппинг ID абилок -> Название
ability_map = {}
for item in items_data:
    if item.get('type') == 'ability' and item.get('heroes'):
        ability_map[item['id']] = item['class_name']

print(f"Loaded {len(ability_map)} hero abilities.")

con = duckdb.connect()
file_path = "data/raw/match_player_86.parquet"

# Берем 5 матчей
df = con.query(f"SELECT match_id, hero_id, \"items.item_id\" as item_ids, \"items.upgrade_id\" as upgrade_ids FROM '{file_path}' LIMIT 5").df()

for idx, row in df.iterrows():
    seq = []
    ability_counts = {}
    
    for item_id, upg_id in zip(row['item_ids'], row['upgrade_ids']):
        item_id = int(item_id) if hasattr(item_id, 'item') else item_id
        if item_id in ability_map:
            ab_name = ability_map[item_id]
            ability_counts[ab_name] = ability_counts.get(ab_name, 0) + 1
            lvl = ability_counts[ab_name]
            seq.append(f"{ab_name}_lvl{lvl}")
            
    print(f"Match {row['match_id']} | Hero {row['hero_id']}:")
    print(seq)
    print("-" * 50)
