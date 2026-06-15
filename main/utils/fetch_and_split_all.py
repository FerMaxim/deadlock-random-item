import os
import json
import urllib.request
import urllib.error
from collections import defaultdict

def fetch_data():
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    # Загружаем героев
    print("Получаем список героев...")
    req_heroes = urllib.request.Request("https://api.deadlock-api.com/v1/assets/heroes", headers=headers)
    with urllib.request.urlopen(req_heroes) as response:
        heroes_data = json.loads(response.read().decode('utf-8'))
        
    # Загружаем предметы
    print("Получаем список предметов...")
    req_items = urllib.request.Request("https://api.deadlock-api.com/v1/assets/items", headers=headers)
    with urllib.request.urlopen(req_items) as response:
        items_data = json.loads(response.read().decode('utf-8'))
        
    # Индексируем предметы по ID
    items_by_id = {str(item["id"]): item for item in items_data}
        
    return heroes_data, items_by_id

def process_and_save():
    try:
        heroes_data, items_by_id = fetch_data()
    except Exception as e:
        print(f"Ошибка загрузки данных: {e}")
        return

    abilities_dict = defaultdict(dict)
    shop_items_dict = defaultdict(lambda: defaultdict(dict))
    
    # 1. Сначала обрабатываем героев и их способности
    hero_id_to_name = {}
    
    for hero in heroes_data:
        hero_id = str(hero.get("id"))
        hero_name = hero.get("name", f"Unknown_Hero_{hero_id}").replace("hero_", "").capitalize()
        hero_id_to_name[hero_id] = hero_name
        
        # Получаем способности героя. У героя может быть массив items или bound abilities.
        # В Deadlock API способности героя лежат в массиве items или abilities (сейчас посмотрим)
        # Обычно это ключи в объекте, но мы можем найти их по items_by_id
        # Но чтобы гарантированно найти 4 способности, просто пройдемся по items_by_id
        pass

    # Чтобы точно найти способности, проходим по всем предметам типа 'ability'
    for item_id, item in items_by_id.items():
        if item.get("type") == "ability":
            # Ищем героя, которому принадлежит абилка. 
            # Либо по hero_id, либо по массиву heroes
            h_id = str(item.get("hero_id", ""))
            
            if not h_id and item.get("heroes"):
                h_id = str(item.get("heroes")[0])
                
            if h_id and h_id in hero_id_to_name:
                # Фильтруем только скиллы (сигнатурки, ульта и т.д.)
                # Убираем пассивки или системные вещи, если это нужно, но пока оставим все привязанные
                ability_type = item.get("ability_type", "unknown")
                if ability_type in ["signature", "ultimate"]:
                    hero_name = hero_id_to_name[h_id]
                    abilities_dict[f"{hero_name}_{h_id}"][item_id] = {
                        "name": item.get("name").replace("ability_", "").replace(f"{hero_name.lower()}_", ""),
                        "type": ability_type
                    }
                    
        # 2. Обрабатываем предметы магазина
        elif item.get("type") == "upgrade":
            cost = item.get("cost", 0)
            if cost > 0 and cost < 9999:
                slot_type = str(item.get("item_slot_type", "Unknown")).lower()
                cost_str = str(cost)
                
                shop_items_dict[slot_type][cost_str][item_id] = {
                    "name": item.get("name").replace("upgrade_", "")
                }
                
                # Добавляем компоненты, если есть (component_items)
                if "component_items" in item and item["component_items"]:
                    shop_items_dict[slot_type][cost_str][item_id]["components"] = item["component_items"]

    # Сохраняем
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dict_dir = os.path.join(base_dir, "data", "dictionary")
    os.makedirs(dict_dir, exist_ok=True)
    
    with open(os.path.join(dict_dir, "abilities_dict.json"), "w", encoding="utf-8") as f:
        json.dump(abilities_dict, f, ensure_ascii=False, indent=4)
        
    with open(os.path.join(dict_dir, "shop_items_dict.json"), "w", encoding="utf-8") as f:
        json.dump(shop_items_dict, f, ensure_ascii=False, indent=4)
        
    print("Успешно созданы словари:")
    print(f"- Способностей привязано: {sum(len(h) for h in abilities_dict.values())} шт. для {len(abilities_dict)} героев")
    print(f"- Магазин (без 9999): {sum(len(c) for t in shop_items_dict.values() for c in t.values())} предметов с компонентами")

if __name__ == "__main__":
    process_and_save()
