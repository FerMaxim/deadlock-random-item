import os
import json
import duckdb
import csv

def preview_items():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dict_dir = os.path.join(base_dir, "data", "dictionary")
    parquet_path = os.path.join(base_dir, "training", "high_mmr_dataset_20260615_225136.parquet")
    output_csv = os.path.join(base_dir, "training", "temp", "items_preview.csv")
    
    # 1. Загружаем словари и создаем единый маппинг ID -> Имя
    id_to_name = {}
    
    # Загружаем магазин
    shop_path = os.path.join(dict_dir, "shop_items_dict.json")
    if os.path.exists(shop_path):
        with open(shop_path, "r", encoding="utf-8") as f:
            shop_data = json.load(f)
            for item_id, info in shop_data.items():
                id_to_name[item_id] = info.get("name", "Unknown Item")
                
    # Загружаем способности
    abilities_path = os.path.join(dict_dir, "abilities_dict.json")
    if os.path.exists(abilities_path):
        with open(abilities_path, "r", encoding="utf-8") as f:
            abilities_data = json.load(f)
            # Структура: hero_id -> ability_id -> {name, type}
            for hero_id, skills in abilities_data.items():
                for skill_id, info in skills.items():
                    id_to_name[skill_id] = f"[СКИЛЛ] {info.get('name')}"

    # 2. Получаем первую строку из Parquet
    con = duckdb.connect(':memory:')
    try:
        # Вытаскиваем массив items.item_id из первой строки
        query = f'SELECT "items.item_id" FROM read_parquet(\'{parquet_path}\') LIMIT 1'
        row = con.execute(query).fetchone()
        
        if not row or not row[0]:
            print("Не удалось получить данные или массив пуст.")
            return
            
        item_ids = row[0]
        
        # 3. Формируем строки для CSV
        # Первая строка: сами айдишники
        row_ids = [str(i) for i in item_ids]
        
        # Вторая строка: расшифрованные названия (если нет в словаре, пишем Unknown)
        row_names = [id_to_name.get(str(i), f"UNKNOWN_{i}") for i in item_ids]
        
        # 4. Сохраняем в CSV (используем табуляцию, как вы просили)
        with open(output_csv, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerow(row_ids)
            writer.writerow(row_names)
            
        print(f"Превью успешно сохранено в: {output_csv}\n")
        
        # Выводим в консоль для наглядности (первые 10 для удобства)
        print("Предпросмотр (первые 10 элементов):")
        print("IDS:\t" + "\t".join(row_ids[:10]))
        print("NAMES:\t" + "\t".join(row_names[:10]))
        
    except Exception as e:
        print(f"Ошибка при чтении Parquet: {e}")
    finally:
        con.close()

if __name__ == "__main__":
    preview_items()
