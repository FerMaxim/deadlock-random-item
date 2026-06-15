import pandas as pd
import ast
import json
import numpy as np
import os
from collections import defaultdict

def prepare_data():
    print("Загрузка предметов...")
    with open("data/reference/items.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # Выбираем только реальные покупаемые предметы (отсеиваем отключенные скиллы и системные вещи)
    valid_items = [
        i for i in data 
        if 'id' in i 
        and i.get('cost', 0) > 0 
        and i.get('item_slot_type') in ['weapon', 'vitality', 'spirit']
        and i.get('shopable', True) == True
        and i.get('disabled', False) == False
    ]
    
    # Создаем маппинг: item_id -> index (от 0 до N-1)
    item_id_to_idx = {item['id']: idx for idx, item in enumerate(valid_items)}
    idx_to_item_id = {idx: item_id for item_id, idx in item_id_to_idx.items()}
    num_items = len(item_id_to_idx)
    
    # Сохраняем маппинг для генератора
    mapping_data = {
        "item_id_to_idx": item_id_to_idx,
        "idx_to_item_id": idx_to_item_id,
        "num_items": num_items
    }
    with open("data/processed/xgb_mapping.json", "w", encoding="utf-8") as f:
        json.dump(mapping_data, f, indent=4)
        
    print(f"Отслеживаем {num_items} уникальных предметов.")
    
    print("Загрузка кластеров...")
    df_clusters = pd.read_csv("data/processed/bebop_clustered.csv")
    cluster_mapping = {(row['match_id'], row['account_id']): row['cluster_id'] for idx, row in df_clusters.iterrows()}
    
    print("Загрузка матчей...")
    df_matches = pd.read_csv("data/processed/match_player_88.csv", usecols=['match_id', 'account_id', 'hero_id', 'items.item_id', 'items.game_time_s'])
    df_matches = df_matches[df_matches['hero_id'] == 15]
    
    X_list = []
    Y_list = []
    
    print("Генерация микро-шагов...")
    for idx, row in df_matches.iterrows():
        key = (row['match_id'], row['account_id'])
        if key not in cluster_mapping:
            continue
            
        cluster_id = cluster_mapping[key]
        
        try:
            item_ids = ast.literal_eval(row['items.item_id'])
            game_times = ast.literal_eval(row['items.game_time_s'])
        except:
            continue
            
        # Формируем список (время, item_id) и сортируем по времени
        purchases = []
        for i_id, t in zip(item_ids, game_times):
            if i_id in item_id_to_idx:
                purchases.append((t, i_id))
                
        purchases.sort(key=lambda x: x[0])
        
        # Инвентарь на старте пуст
        current_inventory = np.zeros(num_items, dtype=np.float32)
        
        # Для каждой покупки создаем пример: (Текущий инвентарь + Кластер + Шаг) -> (Новая покупка)
        step_count = 0
        for _, bought_item_id in purchases:
            target_idx = item_id_to_idx[bought_item_id]
            
            # Формируем фичи: [Cluster ID, Step Count, Item 0, Item 1, ... Item N]
            features = np.zeros(num_items + 2, dtype=np.float32)
            features[0] = cluster_id
            features[1] = step_count
            features[2:] = current_inventory
            
            X_list.append(features)
            Y_list.append(target_idx)
            
            # Обновляем инвентарь (помечаем предмет как купленный)
            current_inventory[target_idx] = 1.0
            step_count += 1
            
    print(f"Сгенерировано {len(X_list)} микро-шагов из реальных матчей.")
    
    # --- ВНЕДРЕНИЕ ЗОЛОТЫХ СБОРОК (DATA AUGMENTATION) ---
    print("Загрузка Золотых Сборок...")
    try:
        with open("data/reference/golden_builds.json", 'r', encoding='utf-8') as f:
            golden = json.load(f)
            
        # Маппинг имени предмета в ID
        name_to_id = {item['name']: item['id'] for item in data if 'name' in item}
        
        golden_steps = 0
        for cluster_id_str, g_data in golden.items():
            c_id = int(cluster_id_str)
            weight = g_data['weight']
            build_names = g_data['build']
            
            # Конвертируем имена в target_idx
            build_indices = []
            for name in build_names:
                i_id = name_to_id.get(name)
                if i_id and i_id in item_id_to_idx:
                    build_indices.append(item_id_to_idx[i_id])
                    
            # Размножаем этот билд weight раз
            for _ in range(weight):
                current_inventory = np.zeros(num_items, dtype=np.float32)
                step_count = 0
                for target_idx in build_indices:
                    features = np.zeros(num_items + 2, dtype=np.float32)
                    features[0] = c_id
                    features[1] = step_count
                    features[2:] = current_inventory
                    
                    X_list.append(features)
                    Y_list.append(target_idx)
                    
                    current_inventory[target_idx] = 1.0
                    step_count += 1
                    golden_steps += 1
                    
        print(f"Успешно внедрено {golden_steps} микро-шагов из эталонных сборок (с учетом веса).")
    except Exception as e:
        print(f"Ошибка при обработке Золотых Сборок: {e}")
            
    X = np.array(X_list, dtype=np.float32)
    Y = np.array(Y_list, dtype=np.int32)
    
    print(f"Сгенерировано {len(X)} микро-шагов обучения.")
    
    np.save("data/processed/xgb_X.npy", X)
    np.save("data/processed/xgb_Y.npy", Y)
    print("Данные сохранены в data/processed/xgb_X.npy и xgb_Y.npy")

if __name__ == "__main__":
    prepare_data()
