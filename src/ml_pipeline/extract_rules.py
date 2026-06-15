import pandas as pd
import ast
import json
import os
import requests
from collections import Counter, defaultdict
import numpy as np

def load_item_map():
    with open("data/reference/items.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
    return {item['id']: item for item in data if 'id' in item}

def fetch_ability_orders(item_ids_to_include):
    url = "https://api.deadlock-api.com/v1/analytics/ability-order-stats"
    params = {
        "hero_id": 15,
        "include_item_ids": ",".join(map(str, item_ids_to_include))
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    return []

def extract_rules():
    item_map = load_item_map()
    
    # Строим маппинг апгрейдов: id_базового -> [id_улучшенного]
    class_to_id = {v['class_name']: k for k, v in item_map.items() if 'class_name' in v}
    upgrades_into = defaultdict(list)
    for k, v in item_map.items():
        if 'component_items' in v:
            for comp_class in v['component_items']:
                if comp_class in class_to_id:
                    comp_id = class_to_id[comp_class]
                    upgrades_into[comp_id].append(k)
    
    df_clusters = pd.read_csv("data/processed/bebop_clustered.csv")
    # Используем кортеж (match_id, account_id) для точной идентификации игрока
    cluster_mapping = {(row['match_id'], row['account_id']): row['cluster_id'] for idx, row in df_clusters.iterrows()}
    
    df_matches = pd.read_csv("data/processed/match_player_88.csv", usecols=['match_id', 'account_id', 'hero_id', 'items.item_id', 'items.game_time_s', 'items.sold_time_s'])
    # ВАЖНО: Фильтруем только Бибопов!
    df_matches = df_matches[df_matches['hero_id'] == 15]
    
    # Структура для хронологии: {cluster_id: {item_id: {'times': [], 'sold_count': 0, 'bought_count': 0}}}
    cluster_stats = {0: defaultdict(lambda: {'times': [], 'sold_count': 0, 'bought_count': 0}), 
                     1: defaultdict(lambda: {'times': [], 'sold_count': 0, 'bought_count': 0})}
    cluster_counts = {0: 0, 1: 0}
    
    print("Парсинг матчей для построения хронологии...")
    for idx, row in df_matches.iterrows():
        key = (row['match_id'], row['account_id'])
        if key not in cluster_mapping: continue
            
        cid = cluster_mapping[key]
        cluster_counts[cid] += 1
        
        try:
            item_ids = ast.literal_eval(row['items.item_id'])
            game_times = ast.literal_eval(row['items.game_time_s'])
            sold_times = ast.literal_eval(row['items.sold_time_s'])
        except:
            continue
            
        unique_bought = set()
        for i_id, g_time, s_time in zip(item_ids, game_times, sold_times):
            if i_id in item_map:
                # Избегаем дубликатов одного и того же предмета в рамках одного матча для статистики
                if i_id not in unique_bought:
                    unique_bought.add(i_id)
                    cluster_stats[cid][i_id]['bought_count'] += 1
                    cluster_stats[cid][i_id]['times'].append(g_time)
                    if s_time > 0:
                        cluster_stats[cid][i_id]['sold_count'] += 1

    meta_rules = {"hero_id": 15, "archetypes": {}}

    for cid in [0, 1]:
        archetype_name = "Spirit/Bomb Bebop" if cid == 0 else "Gun/Weapon Bebop"
        
        # Фильтруем предметы, которые покупают как минимум в 40% матчей
        min_support = cluster_counts[cid] * 0.40
        
        valid_items = []
        for i_id, stats in cluster_stats[cid].items():
            if stats['bought_count'] >= min_support:
                category = item_map[i_id].get('item_slot_type')
                # Берем только реальные предметы (не скиллы и не врожденные)
                if category in ['weapon', 'vitality', 'spirit']:
                    median_time = np.median(stats['times'])
                    sell_rate = stats['sold_count'] / stats['bought_count']
                    
                    valid_items.append({
                        'id': i_id,
                        'name': item_map[i_id].get('name', str(i_id)),
                        'category': category,
                        'median_time_s': median_time,
                        'sell_rate': sell_rate,
                        'cost': item_map[i_id].get('cost', 0)
                    })
        
        # Сортируем предметы по медианному времени покупки
        valid_items.sort(key=lambda x: x['median_time_s'])
        
        # Для каждого предмета определяем его статус: апгрейдится, продается или остается
        final_purchase_order = []
        cluster_item_ids = set([i['id'] for i in valid_items])
        
        for i in valid_items:
            is_upgraded = False
            # Проверяем, есть ли его апгрейд в итоговом билде этого кластера
            for upg_id in upgrades_into.get(i['id'], []):
                if upg_id in cluster_item_ids:
                    is_upgraded = True
                    break
                    
            status_tag = ""
            if is_upgraded:
                status_tag = "апгрейд"
            elif i['sell_rate'] > 0.4:
                status_tag = "продажа"
                
            final_purchase_order.append({
                "name": i['name'],
                "category": i['category'],
                "time_min": round(i['median_time_s'] / 60, 1),
                "status_tag": status_tag
            })
        
        # Для API берем топ 3 предмета по популярности из дорогих (>1200)
        expensive_items = [i for i in valid_items if i['cost'] >= 1200 and i['sell_rate'] < 0.5]
        expensive_items.sort(key=lambda x: cluster_stats[cid][x['id']]['bought_count'], reverse=True)
        top3_ids = [i['id'] for i in expensive_items[:3]]
        
        ability_data = fetch_ability_orders(top3_ids)
        ability_sequence_names = []
        if ability_data:
            seq = ability_data[0].get('abilities', [])
            # Переводим ID способностей в читаемые названия
            for a_id in seq:
                name = item_map.get(a_id, {}).get('name', f"Unknown Ability ({a_id})")
                ability_sequence_names.append(name)
            
        meta_rules["archetypes"][archetype_name] = {
            "purchase_order": final_purchase_order,
            "ability_sequence": ability_sequence_names,
            "api_keys_used": [item_map[i]['name'] for i in top3_ids]
        }

    with open("data/processed/meta_rules.json", "w", encoding="utf-8") as f:
        json.dump(meta_rules, f, indent=4, ensure_ascii=False)
        
    print("Временные ряды и хронология успешно извлечены и сохранены в meta_rules.json")

if __name__ == "__main__":
    extract_rules()
