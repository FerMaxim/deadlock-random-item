import os
import json
import duckdb

def preview_upgrades():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dict_dir = os.path.join(base_dir, "data", "dictionary")
    parquet_path = os.path.join(base_dir, "training", "high_mmr_dataset_20260615_225136.parquet")
    
    # 1. Загружаем словари для маппинга
    id_to_name = {}
    shop_path = os.path.join(dict_dir, "shop_items_dict.json")
    if os.path.exists(shop_path):
        with open(shop_path, "r", encoding="utf-8") as f:
            for k, v in json.load(f).items():
                id_to_name[k] = f"[Магазин] {v['name']} ({v['cost']})"
                
    abilities_path = os.path.join(dict_dir, "abilities_dict.json")
    if os.path.exists(abilities_path):
        with open(abilities_path, "r", encoding="utf-8") as f:
            for hero_id, skills in json.load(f).items():
                for skill_id, info in skills.items():
                    id_to_name[skill_id] = f"[Скилл] {info['name']}"

    # 2. Вытаскиваем первую строчку с item_id и upgrade_id
    con = duckdb.connect(':memory:')
    query = f"""
    SELECT "items.item_id", "items.upgrade_id" 
    FROM read_parquet('{parquet_path}') 
    LIMIT 1
    """
    row = con.execute(query).fetchone()
    con.close()
    
    item_ids = row[0]
    upgrade_ids = row[1]
    
    print("\n=== ВЫТАСКА items.upgrade_id ДЛЯ ПЕРВОГО МАТЧА ===")
    print("Формат: Действие -> [ID_предмета: Название]  |  [upgrade_id: Расшифровка]")
    print("-" * 80)
    
    for i, (i_id, u_id) in enumerate(zip(item_ids, upgrade_ids)):
        i_name = id_to_name.get(str(i_id), "UNKNOWN_ITEM")
        
        # Расшифровываем upgrade_id (это может быть ID предмета, 0 или 1)
        u_name = ""
        if u_id == 0:
            u_name = "(Нет апгрейда)"
        elif u_id == 1:
            u_name = "(Флаг базового апгрейда / Внутренний код)"
        else:
            u_name = f"-> Указывает на: {id_to_name.get(str(u_id), 'UNKNOWN_UPGRADE')}"
            
        print(f"Шаг {i+1:02d}: {i_id} ({i_name})")
        print(f"        upgrade_id = {u_id} {u_name}")
        print()

if __name__ == "__main__":
    preview_upgrades()
