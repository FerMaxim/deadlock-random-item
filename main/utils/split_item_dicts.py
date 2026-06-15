import os
import json

def split_dictionaries():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    
    input_file = os.path.join(data_dir, "items_metadata.json")
    if not os.path.exists(input_file):
        print(f"Ошибка: Не найден файл {input_file}")
        return
        
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    from collections import defaultdict

    abilities_dict = defaultdict(dict)
    shop_items_dict = defaultdict(lambda: defaultdict(dict))
    
    for item_id, item in data.items():
        # Способности (abilities)
        if item.get("type") == "ability":
            hero_id = str(item.get("hero_id", "Unknown_Hero"))
            abilities_dict[hero_id][item_id] = {
                "name": item.get("name"),
                "cost": item.get("cost", 0)
            }
            
        # Покупаемые предметы (улучшения магазина)
        elif item.get("type") == "upgrade" and item.get("cost", 0) > 0:
            slot_type = str(item.get("slot_type", "Unknown")).lower()
            cost = str(item.get("cost"))
            
            shop_items_dict[slot_type][cost][item_id] = {
                "name": item.get("name")
            }
            if "components" in item and item["components"]:
                shop_items_dict[slot_type][cost][item_id]["components"] = item["components"]
                
    # Создаем папку dictionary
    dict_dir = os.path.join(data_dir, "dictionary")
    os.makedirs(dict_dir, exist_ok=True)
                
    # Сохраняем словарь со способностями
    abilities_path = os.path.join(dict_dir, "abilities_dict.json")
    with open(abilities_path, "w", encoding="utf-8") as f:
        json.dump(abilities_dict, f, ensure_ascii=False, indent=4)
        
    # Сохраняем словарь с предметами магазина
    shop_items_path = os.path.join(dict_dir, "shop_items_dict.json")
    with open(shop_items_path, "w", encoding="utf-8") as f:
        json.dump(shop_items_dict, f, ensure_ascii=False, indent=4)
        
    print(f"Успешно разделено на 2 многоуровневых словаря:")
    print(f"1. Способности героев (сгруппированы по {len(abilities_dict)} героям) -> {abilities_path}")
    print(f"2. Предметы магазина (сгруппированы по вкладкам {list(shop_items_dict.keys())} и ценам) -> {shop_items_path}")

if __name__ == "__main__":
    split_dictionaries()
