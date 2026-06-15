import pandas as pd
import json
import ast
import os

def load_item_metadata():
    items_path = "data/reference/items.json"
    if not os.path.exists(items_path):
        import requests
        print("Скачиваю справочник предметов с API...")
        data = requests.get('https://api.deadlock-api.com/v1/assets/items').json()
        os.makedirs(os.path.dirname(items_path), exist_ok=True)
        with open(items_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    else:
        with open(items_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

    item_map = {}
    for item in data:
        if 'id' in item and 'item_slot_type' in item and 'cost' in item:
            item_map[item['id']] = {
                'cost': item['cost'],
                'type': item['item_slot_type'], # 'weapon', 'armor', 'tech'
                'name': item.get('name', str(item['id']))
            }
    return item_map

def build_bebop_matrix():
    item_map = load_item_metadata()
    print(f"Загружено {len(item_map)} предметов из базы.")

    csv_path = "data/processed/match_player_88.csv"
    print(f"Чтение данных матчей из {csv_path}...")
    
    # Читаем нужные колонки
    cols = ['match_id', 'account_id', 'hero_id', 'items.item_id', 'items.sold_time_s', 'net_worth', 'match_outcome', 'average_badge_team0', 'average_badge_team1']
    df = pd.read_csv(csv_path, usecols=cols)

    # Фильтруем Bebop (ID 15)
    df_bebop = df[df['hero_id'] == 15].copy()
    print(f"Найдено {len(df_bebop)} записей для Bebop.")

    weapon_souls = []
    armor_souls = []
    tech_souls = []
    
    # Опционально: можно трекать конкретные предметы (Mystic Burst = 100002 etc)
    # Пока просто считаем инвестиции по категориям
    
    for idx, row in df_bebop.iterrows():
        try:
            # Парсим списки из строк
            item_ids = ast.literal_eval(row['items.item_id'])
            sold_times = ast.literal_eval(row['items.sold_time_s'])
        except Exception:
            item_ids = []
            sold_times = []

        w_souls = 0
        a_souls = 0
        t_souls = 0
        
        for i_id, s_time in zip(item_ids, sold_times):
            # Если s_time == 0, предмет не был продан (или был продан и это как-то иначе отмечается, но обычно 0 = не продан)
            if s_time == 0 and i_id in item_map:
                category = item_map[i_id]['type']
                cost = item_map[i_id]['cost']
                
                if category == 'weapon': w_souls += cost
                elif category == 'vitality': a_souls += cost
                elif category == 'spirit': t_souls += cost
                
        weapon_souls.append(w_souls)
        armor_souls.append(a_souls)
        tech_souls.append(t_souls)

    df_bebop['weapon_souls'] = weapon_souls
    df_bebop['vitality_souls'] = armor_souls
    df_bebop['spirit_souls'] = tech_souls
    
    # Считаем средний бейдж лобби
    df_bebop['lobby_badge'] = df_bebop[['average_badge_team0', 'average_badge_team1']].mean(axis=1)

    output_path = "data/processed/bebop_items_matrix.csv"
    
    # Оставляем только полезные колонки для K-Means
    final_cols = ['match_id', 'account_id', 'net_worth', 'match_outcome', 'lobby_badge', 'weapon_souls', 'vitality_souls', 'spirit_souls']
    df_final = df_bebop[final_cols]
    df_final.to_csv(output_path, index=False)
    
    print(f"Матрица успешно сохранена в {output_path}")
    print(df_final.head())

if __name__ == "__main__":
    build_bebop_matrix()
