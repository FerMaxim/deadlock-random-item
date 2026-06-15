import requests
import json
import time
import os

BASE_URL = "https://api.deadlock-api.com/v1"
HERO_NAME = "bebop"

def fetch_hero_data():
    print(f"🦸‍♂️ 1. Изучаем анатомию героя: {HERO_NAME}...")
    resp = requests.get(f"{BASE_URL}/assets/heroes/by-name/{HERO_NAME}")
    if resp.status_code != 200:
        print("❌ Ошибка получения данных героя!")
        return None
    
    hero_data = resp.json()
    hero_id = hero_data.get("id")
    
    # Собираем только самое важное для математики
    stats = {
        "id": hero_id,
        "name": hero_data.get("name"),
        "starting_stats": hero_data.get("starting_stats", {}),
        "scaling_stats": hero_data.get("scaling_stats", {})
    }
    
    with open("hero_stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
        
    print(f"✅ Герой изучен! ID: {hero_id}")
    return hero_id

def fetch_items_and_abilities(hero_id):
    print("📚 2. Собираем Энциклопедию Предметов и Способностей (с их статами!)...")
    resp = requests.get(f"{BASE_URL}/assets/items")
    if resp.status_code != 200:
        print("❌ Ошибка получения предметов!")
        return
        
    items_raw = resp.json()
    knowledge_base = {}

    for item in items_raw:
        item_id = str(item.get("id"))
        if item_id == "0": continue # Пропускаем багованные дампы
        
        item_type = item.get("type", "")
        item_class = item.get("class_name", "")
        
        # 1. Проверяем, это способность Бебопа?
        is_hero_ability = False
        if item_type == "ability":
            # Способности привязаны к массиву heroes
            if hero_id in item.get("heroes", []):
                is_hero_ability = True
            else:
                continue # Чужие способности нам в энциклопедии не нужны
                
        # 2. Или это предмет из магазина?
        # В API Deadlock магазинные предметы обычно имеют тип "upgrade" или "weapon"
        is_shop_item = item.get("item_slot_type") in ["weapon", "spirit", "vitality"]
        
        if not (is_hero_ability or is_shop_item):
            continue

        # ВЫТЯГИВАЕМ МАТЕМАТИКУ (Статы, которые дает предмет)
        stat_bonuses = {}
        upgrades = item.get("upgrades", [])
        if upgrades and isinstance(upgrades, list):
            for upg in upgrades:
                props = upg.get("property_upgrades", [])
                for prop in props:
                    stat_name = prop.get("name")
                    stat_value = prop.get("bonus")
                    if stat_name and stat_value:
                        stat_bonuses[stat_name] = stat_value

        knowledge_base[item_id] = {
            "name": item.get("name", item_class),
            "class_name": item_class,
            "type": "ability" if is_hero_ability else "shop_item",
            "slot_type": item.get("item_slot_type", "ability"), # weapon, spirit, vitality, ability
            "cost": item.get("cost", 0),
            "is_active": item.get("is_active", False) or item.get("behaviours", []) != [],
            "components": item.get("components", item.get("component_items", [])), # База для крафтов
            "stat_bonuses": stat_bonuses # ТО САМОЕ ДЛЯ ИИ: +15% Spirit, +160 Health и тд.
        }
        
    with open("knowledge_base.json", "w", encoding="utf-8") as f:
        json.dump(knowledge_base, f, indent=2, ensure_ascii=False)
        
    print(f"✅ База знаний собрана! Записано объектов: {len(knowledge_base)}")

def fetch_top_builds(hero_id, limit=200):
    print(f"🎓 3. Ищем 'Учителей': скачиваем ТОП-{limit} гайдов...")
    all_builds = []
    
    # Берем сразу по 100 (максимум API), сортируем по weekly_favorites
    url = f"{BASE_URL}/builds?hero_id={hero_id}&sort_by=weekly_favorites&sort_direction=desc&start=0&limit=100&only_latest=true"
    resp = requests.get(url)
    if resp.status_code == 200:
        all_builds.extend(resp.json())
        
    time.sleep(1)
    
    # Докачиваем еще 50-100 для верности
    url2 = f"{BASE_URL}/builds?hero_id={hero_id}&sort_by=weekly_favorites&sort_direction=desc&start=100&limit=100&only_latest=true"
    resp2 = requests.get(url2)
    if resp2.status_code == 200:
        all_builds.extend(resp2.json())
        
    # Обрезаем жестко до нужного лимита (150 самых качественных)
    best_builds = all_builds[:limit]
    
    with open("teacher_builds.json", "w", encoding="utf-8") as f:
        json.dump(best_builds, f, indent=2, ensure_ascii=False)
        
    print(f"✅ Скачано {len(best_builds)} лучших гайдов для обучения.")

if __name__ == "__main__":
    print("="*50)
    print("🚀 ЗАПУСК ПОДГОТОВКИ ДАННЫХ ДЛЯ ИИ")
    print("="*50)
    
    h_id = fetch_hero_data()
    if h_id is not None:
        fetch_items_and_abilities(h_id)
        fetch_top_builds(h_id, limit=200)
        
    print("\n🎉 ГОТОВО! Энциклопедия сформирована.")