import os
import json
import urllib.request

def process_data():
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    print("Получаем список героев...")
    req_heroes = urllib.request.Request("https://api.deadlock-api.com/v1/assets/heroes", headers=headers)
    with urllib.request.urlopen(req_heroes) as response:
        heroes_data = json.loads(response.read().decode('utf-8'))
        
    print("Получаем список предметов...")
    req_items = urllib.request.Request("https://api.deadlock-api.com/v1/assets/items", headers=headers)
    with urllib.request.urlopen(req_items) as response:
        items_data = json.loads(response.read().decode('utf-8'))

    # Парсим героев (отбираем только 38 штук)
    heroes_dict = {}
    valid_hero_ids = []
    
    # Чтобы получить ровно 38 персонажей с 4 способностями, пройдемся по списку героев
    # В Deadlock большинство "нормальных" героев не имеют префикса npc_
    count_heroes = 0
    
    # Словарь способностей по героям (ID -> ID Способности -> данные)
    abilities_dict = {}
    
    for hero in heroes_data:
        if count_heroes >= 38:
            break
            
        hero_id = str(hero.get("id"))
        hero_name = hero.get("name", "").replace("hero_", "").capitalize()
        
        # Находим скиллы этого героя
        hero_skills = {}
        for item in items_data:
            if item.get("type") == "ability":
                h_id = str(item.get("hero_id", ""))
                if not h_id and item.get("heroes"):
                    h_id = str(item.get("heroes")[0])
                    
                if h_id == hero_id:
                    ability_type = item.get("ability_type", "unknown")
                    if ability_type in ["signature", "ultimate"]:
                        skill_id = str(item.get("id"))
                        hero_skills[skill_id] = {
                            "name": item.get("name"),
                            "type": ability_type
                        }
        
        # Если у героя есть хотя бы 4 скилла (выбираем ровно 4)
        if len(hero_skills) >= 4:
            # Берем ровно 4
            selected_skills = dict(list(hero_skills.items())[:4])
            
            heroes_dict[hero_name] = hero_id
            abilities_dict[hero_id] = selected_skills
            valid_hero_ids.append(hero_id)
            count_heroes += 1

    # Парсим магазин (возвращаем плоскую структуру, как было изначально, без мусора)
    shop_items_dict = {}
    for item in items_data:
        if item.get("type") == "upgrade":
            cost = item.get("cost", 0)
            if cost > 0 and cost < 9999: # Убираем тестовые предметы 9999
                item_id = str(item.get("id"))
                shop_items_dict[item_id] = {
                    "name": item.get("name"),
                    "class_name": item.get("class_name", ""),
                    "cost": cost,
                    "slot_type": str(item.get("item_slot_type", "Unknown")).lower(),
                    "is_active": item.get("is_active_item", False)
                }
                
                # Компоненты, если они есть
                if "component_items" in item and item["component_items"]:
                    shop_items_dict[item_id]["components"] = item["component_items"]
                elif "components" in item and item["components"]:
                    shop_items_dict[item_id]["components"] = item["components"]

    # Сохраняем в папку
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dict_dir = os.path.join(base_dir, "data", "dictionary")
    os.makedirs(dict_dir, exist_ok=True)
    
    with open(os.path.join(dict_dir, "heroes_dict.json"), "w", encoding="utf-8") as f:
        json.dump(heroes_dict, f, ensure_ascii=False, indent=4)
        
    with open(os.path.join(dict_dir, "abilities_dict.json"), "w", encoding="utf-8") as f:
        json.dump(abilities_dict, f, ensure_ascii=False, indent=4)
        
    with open(os.path.join(dict_dir, "shop_items_dict.json"), "w", encoding="utf-8") as f:
        json.dump(shop_items_dict, f, ensure_ascii=False, indent=4)
        
    print(f"Успешно! Сохранено героев: {len(heroes_dict)}. Сохранено способностей: {sum(len(v) for v in abilities_dict.values())}. Магазин: {len(shop_items_dict)} предметов.")

if __name__ == "__main__":
    process_data()
