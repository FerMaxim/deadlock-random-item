import os
import json
import pandas as pd
from tqdm import tqdm

# Опционально: можно использовать tqdm для отображения прогресса в pandas
tqdm.pandas()

def split_items_column(input_parquet: str, output_parquet: str):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dict_dir = os.path.join(base_dir, "data", "dictionary")
    
    # 1. Загружаем словари для определения типа ID
    ability_ids = set()
    abilities_path = os.path.join(dict_dir, "abilities_dict.json")
    if os.path.exists(abilities_path):
        with open(abilities_path, "r", encoding="utf-8") as f:
            abilities_data = json.load(f)
            for hero_id, skills in abilities_data.items():
                for skill_id in skills.keys():
                    ability_ids.add(int(skill_id))
                    
    shop_ids = set()
    shop_path = os.path.join(dict_dir, "shop_items_dict.json")
    if os.path.exists(shop_path):
        with open(shop_path, "r", encoding="utf-8") as f:
            shop_data = json.load(f)
            for item_id in shop_data.keys():
                shop_ids.add(int(item_id))
                
    print(f"Загружено {len(ability_ids)} ID способностей и {len(shop_ids)} ID предметов магазина.")
    
    # 2. Загружаем Parquet
    print(f"Читаем Parquet файл: {os.path.basename(input_parquet)}...")
    df = pd.read_parquet(input_parquet)
    print(f"Записей для обработки: {len(df)}")
    
    # 3. Функции для разделения
    def get_abilities(item_list):
        if not hasattr(item_list, '__iter__'): return []
        # Сохраняем порядок: оставляем только ID, которые есть в словаре способностей
        return [x for x in item_list if x in ability_ids]
        
    def get_shop_items(item_list):
        if not hasattr(item_list, '__iter__'): return []
        # Сохраняем порядок: оставляем только ID, которые есть в словаре магазина
        return [x for x in item_list if x in shop_ids]

    # 4. Применяем разделение
    print("Разделяем колонку items.item_id на способности и предметы (это займет пару секунд)...")
    df['ability_build'] = df['items.item_id'].apply(get_abilities)
    df['item_build'] = df['items.item_id'].apply(get_shop_items)
    
    # Удаляем оригинальную колонку, если нужно (или оставляем, пока просто оставляем или удаляем?)
    # Лучше удалить, раз мы разделили, чтобы сэкономить место
    df = df.drop(columns=['items.item_id'])
    
    # 5. Сохраняем результат
    print(f"Сохраняем новый датасет в {os.path.basename(output_parquet)}...")
    df.to_parquet(output_parquet, engine='pyarrow')
    print("Готово!")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    training_dir = os.path.join(base_dir, "training")
    
    # Берем конкретный файл, как просил пользователь
    input_file = os.path.join(training_dir, "high_mmr_dataset_20260615_225136.parquet")
    
    if not os.path.exists(input_file):
        print(f"Ошибка: Файл не найден: {input_file}")
        exit()
        
    # Короткое и понятное имя файла
    output_file = os.path.join(training_dir, "high_mmr_split.parquet")
    
    split_items_column(input_file, output_file)
