import os
import json
import urllib.request
import urllib.error

def fetch_and_save_items():
    url = "https://api.deadlock-api.com/v1/assets/items"
    try:
        print(f"Запрос к API: {url}")
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            
        print(f"Получено предметов: {len(data)}")
        
        # Создаем словарь: ID -> { type, name, cost, hero_id, is_upgrade }
        items_dict = {}
        for item in data:
            item_id = str(item.get("id"))
            item_type = item.get("type", "unknown")
            name = item.get("name", "Unknown Item")
            cost = item.get("cost", 0)
            
            # Для способностей (ability) обычно есть hero_id
            hero_id = item.get("hero_id")
            
            # Улучшения могут быть отмечены в данных
            is_upgrade = item.get("is_upgrade", False)
            
            # Сохраняем самое нужное
            items_dict[item_id] = {
                "id": item_id,
                "name": name,
                "type": item_type,
                "cost": cost,
            }
            
            if hero_id is not None:
                items_dict[item_id]["hero_id"] = hero_id
                
            # Добавляем все доступные данные, если они есть
            if "item_slot_type" in item:
                items_dict[item_id]["slot_type"] = item.get("item_slot_type")
            if "components" in item:
                items_dict[item_id]["components"] = item.get("components")
                
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(base_dir, "data")
        os.makedirs(data_dir, exist_ok=True)
        
        output_file = os.path.join(data_dir, "items_metadata.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(items_dict, f, ensure_ascii=False, indent=4)
            
        print(f"Словарь успешно сохранен в: {output_file}")
        
    except urllib.error.URLError as e:
        print(f"Ошибка при подключении к API: {e}")
    except Exception as e:
        print(f"Непредвиденная ошибка: {e}")

if __name__ == "__main__":
    fetch_and_save_items()
