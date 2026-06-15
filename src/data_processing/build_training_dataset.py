import json
import duckdb
import pandas as pd
import time

def process_data(limit=10000):
    start_time = time.time()
    
    # 1. Загружаем справочник способностей
    with open('data/reference/items.json', 'r', encoding='utf-8') as f:
        items_data = json.load(f)

    ability_map = {}
    for item in items_data:
        if item.get('type') == 'ability' and item.get('heroes'):
            ability_map[item['id']] = item['class_name']

    print(f"Загружено {len(ability_map)} уникальных способностей героев.")

    # 2. Подключаемся к дампу
    con = duckdb.connect()
    file_path = "data/raw/match_player_86.parquet"

    # Извлекаем сырые данные (с лимитом для теста, чтобы не ждать часы)
    # Если нужен весь файл, уберите строку LIMIT
    print(f"Извлекаем {limit} строк из Parquet дампа...")
    df = con.query(f"""
    SELECT 
        match_id, 
        hero_id,
        match_mode,
        winning_team,
        team,
        kills,
        deaths,
        assists,
        net_worth,
        average_badge_team0,
        average_badge_team1,
        "items.item_id" as item_ids,
        "items.upgrade_id" as upgrade_ids
    FROM '{file_path}'
    LIMIT {limit}
    """).df()

    print("Шаг 1: Разделяем предметы и навыки, очищаем массивы...")
    skill_records = []
    clean_item_records = []

    for idx, row in df.iterrows():
        seq = []
        ability_counts = {}
        clean_items = []
        
        # Разбираем массив покупок
        for item_id, upg_id in zip(row['item_ids'], row['upgrade_ids']):
            item_id = int(item_id) if hasattr(item_id, 'item') else item_id
            
            if item_id in ability_map:
                # Это способность! Записываем её в билд навыков
                ab_name = ability_map[item_id]
                ability_counts[ab_name] = ability_counts.get(ab_name, 0) + 1
                lvl = ability_counts[ab_name]
                seq.append(f"{ab_name}_lvl{lvl}")
            else:
                # Это обычный предмет (вещь из магазина)
                if item_id > 0:
                    clean_items.append(item_id)
                    
        skill_records.append({
            'match_id': row['match_id'],
            'hero_id': row['hero_id'],
            'skill_build': ",".join(seq)
        })
        
        clean_item_records.append({
            'match_id': row['match_id'],
            'hero_id': row['hero_id'],
            'item_build': ",".join(map(str, clean_items))
        })

    # ЭТАП А: Сохраняем базу только со скиллами
    df_skills = pd.DataFrame(skill_records)
    df_skills.to_csv('data/processed/db_skills_only.csv', index=False)
    print("-> Сохранена таблица: data/processed/db_skills_only.csv")

    # ЭТАП Б: Сохраняем очищенную базу основных характеристик + чистые предметы
    df_main = df.drop(columns=['item_ids', 'upgrade_ids'])
    df_items = pd.DataFrame(clean_item_records)
    df_clean = pd.merge(df_main, df_items, on=['match_id', 'hero_id'])
    
    # Определяем победил ли игрок (для обучения ML это важный таргет)
    df_clean['won'] = df_clean['team'] == df_clean['winning_team']
    
    df_clean.to_csv('data/processed/db_clean_main.csv', index=False)
    print("-> Сохранена таблица: data/processed/db_clean_main.csv")

    # ЭТАП В: Финальное объединение (ML-ready dataset)
    print("Шаг 2: Объединяем очищенные данные и навыки...")
    df_final = pd.merge(df_clean, df_skills, on=['match_id', 'hero_id'])

    # Оставляем только нужные колонки
    cols_to_keep = [
        'match_id', 'hero_id', 'match_mode', 'won', 
        'kills', 'deaths', 'assists', 'net_worth', 
        'average_badge_team0', 'average_badge_team1',
        'item_build', 'skill_build'
    ]
    df_final = df_final[cols_to_keep]

    df_final.to_csv('data/processed/db_ml_training_ready.csv', index=False)
    print("-> Сохранена итоговая таблица: data/processed/db_ml_training_ready.csv")
    
    print(f"\nГотово за {time.time() - start_time:.2f} сек. Пример итоговых данных:")
    print(df_final.head(2))

if __name__ == "__main__":
    # Вытягиваем 10 тысяч строк для начала.
    process_data(limit=10000)
