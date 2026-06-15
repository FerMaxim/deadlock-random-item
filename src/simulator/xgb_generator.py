import json
import numpy as np
# pyrefly: ignore [missing-import]
import xgboost as xgb
import random
import requests

def load_data():
    with open("data/reference/items.json", 'r', encoding='utf-8') as f:
        items_data = json.load(f)
    item_details = {i['id']: i for i in items_data if 'id' in i}
    
    with open("data/processed/xgb_mapping.json", 'r', encoding='utf-8') as f:
        mapping = json.load(f)
        
    with open("data/processed/xgb_label_mapping.json", 'r', encoding='utf-8') as f:
        label_mapping = json.load(f)
        
    return item_details, mapping, label_mapping

def apply_temperature(probs, temperature):
    """
    Применяет температуру к вероятностям.
    T < 1: более строгий выбор (ближе к мете).
    T > 1: более хаотичный выбор (тестирование странных сборок).
    T = 0: всегда берется самый вероятный предмет (argmax).
    """
    if temperature == 0:
        new_probs = np.zeros_like(probs)
        new_probs[np.argmax(probs)] = 1.0
        return new_probs
        
    # Предотвращаем деление на ноль и логарифм нуля
    probs = np.maximum(probs, 1e-10)
    logits = np.log(probs) / temperature
    # Сдвигаем логиты для вычислительной стабильности
    logits -= np.max(logits)
    exp_logits = np.exp(logits)
    return exp_logits / np.sum(exp_logits)

class InventoryManager:
    def __init__(self, item_details):
        self.item_details = item_details
        self.inventory = [] # list of item ids
        
        self.class_to_id = {v.get('class_name'): k for k, v in item_details.items() if v.get('class_name')}
        
        # Precompute upgrades to know if an item is a "dead end" (no upgrades)
        self.has_upgrades = set()
        for item in item_details.values():
            for comp_class in item.get('component_items', []):
                comp_id = self.class_to_id.get(comp_class)
                if comp_id:
                    self.has_upgrades.add(comp_id)

    def is_active(self, item_id):
        return self.item_details.get(item_id, {}).get('is_active_item', False)

    def get_cost(self, item_id):
        return self.item_details.get(item_id, {}).get('cost', 0)
        
    def find_component_in_inventory(self, target_item_id):
        target_item = self.item_details.get(target_item_id, {})
        for comp_class in target_item.get('component_items', []):
            comp_id = self.class_to_id.get(comp_class)
            if comp_id in self.inventory:
                return comp_id
        return None

    def find_sellable_item(self, must_be_active=False):
        candidates = self.inventory
        if must_be_active:
            candidates = [i for i in candidates if self.is_active(i)]
            
        if not candidates:
            return None
            
        # Priority:
        # 1. No upgrades available (dead end) -> prefer to sell
        # 2. Lowest cost
        
        def sort_key(i_id):
            is_dead_end = i_id not in self.has_upgrades
            cost = self.get_cost(i_id)
            return (0 if is_dead_end else 1, cost)
            
        candidates_sorted = sorted(candidates, key=sort_key)
        return candidates_sorted[0]

def generate_build(playstyle="Gun/Weapon Bebop", num_items=15, temperature=0.5, ability_temp=0.5):
    item_details, mapping, label_mapping = load_data()
    
    # Загрузка модели
    model = xgb.XGBClassifier()
    model.load_model("data/processed/xgb_model.json")
    
    # 0 = Spirit Bebop, 1 = Gun Bebop
    cluster_id = 1 if "Gun" in playstyle else 0
    
    num_total_items = mapping["num_items"]
    current_inventory_arr = np.zeros(num_total_items, dtype=np.float32)
    inv_manager = InventoryManager(item_details)
    
    print(f"=== ГЕНЕРАЦИЯ БИЛДА (XGBOOST AI) ===")
    print(f"Герой: Bebop (ID: 15)")
    print(f"Стиль игры: {playstyle}")
    print(f"Температура предметов: {temperature}")
    print(f"Температура скиллов: {ability_temp}")
    print("======================================\n")
    
    print("[1] СИМУЛЯЦИЯ ЗАКУПКИ (Шаг за шагом):")
    
    build_order = []
    
    step = 1
    attempts = 0
    while step <= num_items and attempts < num_items * 3:
        attempts += 1
        # Формируем фичи: [cluster_id, step_count, inventory_0, ..., inventory_N]
        features = np.zeros(num_total_items + 2, dtype=np.float32)
        features[0] = cluster_id
        features[1] = len(build_order)
        features[2:] = current_inventory_arr
        
        probs_output = model.predict_proba(features.reshape(1, -1))[0]
        probs = np.zeros(num_total_items, dtype=np.float32)
        for class_idx, prob_val in enumerate(probs_output):
            original_idx = label_mapping.get(str(class_idx))
            if original_idx is not None:
                probs[int(original_idx)] = prob_val
        
        # Обнуляем то, что уже в инвентаре
        for i_id in inv_manager.inventory:
            idx = mapping["item_id_to_idx"].get(str(i_id))
            if idx is not None:
                probs[idx] = 0.0
                
        if np.sum(probs) == 0:
            break
            
        probs = probs / np.sum(probs)
        
        # Применяем температуру
        adj_probs = apply_temperature(probs, temperature)
        
        # Обнуляем еще раз на всякий случай
        for i_id in inv_manager.inventory:
            idx = mapping["item_id_to_idx"].get(str(i_id))
            if idx is not None:
                adj_probs[idx] = 0.0
        
        if np.sum(adj_probs) == 0:
            break
        adj_probs = adj_probs / np.sum(adj_probs)
        
        action_taken = False
        
        # Пытаемся выбрать валидный предмет (до 50 попыток на шаг)
        for _ in range(50):
            if np.sum(adj_probs) == 0:
                break
                
            # Нормализуем вероятности для np.random.choice
            adj_probs = adj_probs / np.sum(adj_probs)
            
            # Сэмплируем предмет с учетом температуры!
            next_item_idx = np.random.choice(num_total_items, p=adj_probs)
                
            item_id = mapping["idx_to_item_id"][str(next_item_idx)]
            item_info = item_details.get(item_id, {})
            name = item_info.get("name", "Unknown")
            cost = item_info.get("cost", 0)
            is_active = item_info.get("is_active_item", False)
            
            # Проверка на апгрейд
            comp_id = inv_manager.find_component_in_inventory(item_id)
            
            if comp_id:
                comp_cost = inv_manager.get_cost(comp_id)
                comp_name = item_details[comp_id].get("name", "Unknown")
                paid = max(0, cost - comp_cost)
                
                inv_manager.inventory.remove(comp_id)
                inv_manager.inventory.append(item_id)
                
                current_inventory_arr[mapping["item_id_to_idx"][str(comp_id)]] = 0.0
                current_inventory_arr[next_item_idx] = 1.0
                
                cat = item_info.get("item_slot_type", "unknown")
                cat_icon = "[Weapon]  " if cat == 'weapon' else "[Vitality]" if cat == 'vitality' else "[Spirit]  "
                print(f" Шаг {step:2d}: {cat_icon} [Апгрейд] {comp_name} -> {name} (Доплата: {paid}) (Уверенность ИИ: {probs[next_item_idx]*100:4.1f}%)")
                build_order.append({"id": item_id, "cost": cost, "name": name})
                action_taken = True
                break
                
            # Проверка лимитов для нового предмета
            active_count = sum(1 for i in inv_manager.inventory if inv_manager.is_active(i))
            
            if is_active and active_count >= 4:
                sell_candidate = inv_manager.find_sellable_item(must_be_active=True)
                if sell_candidate and sell_candidate not in inv_manager.has_upgrades:
                    sell_name = item_details[sell_candidate].get("name", "Unknown")
                    inv_manager.inventory.remove(sell_candidate)
                    inv_manager.inventory.append(item_id)
                    current_inventory_arr[mapping["item_id_to_idx"][str(sell_candidate)]] = 0.0
                    current_inventory_arr[next_item_idx] = 1.0
                    
                    cat = item_info.get("item_slot_type", "unknown")
                    cat_icon = "[Weapon]  " if cat == 'weapon' else "[Vitality]" if cat == 'vitality' else "[Spirit]  "
                    print(f" Шаг {step:2d}: {cat_icon} [Продажа Актив: {sell_name}] -> Покупка {name} (Цена: {cost}) (Уверенность ИИ: {probs[next_item_idx]*100:4.1f}%)")
                    build_order.append({"id": item_id, "cost": cost, "name": name})
                    action_taken = True
                    break
                else:
                    # Отказ от покупки, обнуляем вероятность этого предмета и пробуем снова
                    adj_probs[next_item_idx] = 0.0
                    continue
                    
            if len(inv_manager.inventory) >= 12:
                sell_candidate = inv_manager.find_sellable_item(must_be_active=False)
                sell_name = item_details[sell_candidate].get("name", "Unknown")
                
                inv_manager.inventory.remove(sell_candidate)
                inv_manager.inventory.append(item_id)
                current_inventory_arr[mapping["item_id_to_idx"][str(sell_candidate)]] = 0.0
                current_inventory_arr[next_item_idx] = 1.0
                
                cat = item_info.get("item_slot_type", "unknown")
                cat_icon = "[Weapon]  " if cat == 'weapon' else "[Vitality]" if cat == 'vitality' else "[Spirit]  "
                print(f" Шаг {step:2d}: {cat_icon} [Умная Продажа: {sell_name}] -> Покупка {name} (Цена: {cost}) (Уверенность ИИ: {probs[next_item_idx]*100:4.1f}%)")
                build_order.append({"id": item_id, "cost": cost, "name": name})
                action_taken = True
                break
                
            # Обычная покупка (Слотов хватает)
            inv_manager.inventory.append(item_id)
            current_inventory_arr[next_item_idx] = 1.0
            
            cat = item_info.get("item_slot_type", "unknown")
            cat_icon = "[Weapon]  " if cat == 'weapon' else "[Vitality]" if cat == 'vitality' else "[Spirit]  "
            print(f" Шаг {step:2d}: {cat_icon} [Покупка] {name:<25} (Цена: {cost}) (Уверенность ИИ: {probs[next_item_idx]*100:4.1f}%)")
            build_order.append({"id": item_id, "cost": cost, "name": name})
            action_taken = True
            break
            
        if action_taken:
            step += 1
        else:
            break
            
    print("\n[2] ФОРМИРОВАНИЕ ПРОКАЧКИ СКИЛЛОВ (Через API):")
    expensive_items = sorted([i for i in build_order if i['cost'] >= 1200], key=lambda x: x['cost'], reverse=True)
    
    seq = None
    for k in [3, 2, 1]:
        top_k_ids = [i['id'] for i in expensive_items[:k]]
        if not top_k_ids:
            continue
            
        url = "https://api.deadlock-api.com/v1/analytics/ability-order-stats"
        params = {"hero_id": 15, "include_item_ids": ",".join(map(str, top_k_ids))}
        response = requests.get(url, params=params)
        
        if response.status_code == 200 and response.json():
            patterns = response.json()
            if not patterns:
                continue
                
            # Температура для способностей
            if ability_temp == 0:
                seq = patterns[0].get('abilities', [])
            else:
                matches = np.array([p.get('matches', 1) for p in patterns], dtype=np.float32)
                matches = np.maximum(matches, 1e-10)
                logits = np.log(matches) / ability_temp
                logits -= np.max(logits)
                exp_logits = np.exp(logits)
                probs = exp_logits / np.sum(exp_logits)
                
                chosen_idx = np.random.choice(len(patterns), p=probs)
                seq = patterns[chosen_idx].get('abilities', [])
                
            if seq:
                print(f" Успех! Найден паттерн прокачки по {k} дорогим предметам.")
                break
                
    if seq:
        for idx, a_id in enumerate(seq, 1):
            a_name = item_details.get(a_id, {}).get("name", f"Скилл {a_id}")
            print(f" Очко {idx:2d}: {a_name}")
    else:
        print(" API не смог найти паттерн прокачки даже по 1 предмету.")

if __name__ == "__main__":
    # print("--- ТЕСТ 1: Gun Bebop (Строгая мета T=0) ---")
    # generate_build("Gun/Weapon Bebop", num_items=20, temperature=0.0, ability_temp=0.0)
    # print("\n")
    print("--- ТЕСТ 2: Spirit Bebop (Строгая мета T=0) ---")
    generate_build("Spirit/Bomb Bebop", num_items=20, temperature=0.0, ability_temp=0.0)
    print("\n")
    print("--- ТЕСТ 3: Spirit Bebop (Творческая T=0.8) ---")
    generate_build("Spirit/Bomb Bebop", num_items=20, temperature=0.5, ability_temp=0.8)
    print("\n")
    print("--- ТЕСТ 4: Spirit Bebop (Творческая T=0.8) ---")
    generate_build("Spirit/Bomb Bebop", num_items=20, temperature=1, ability_temp=0.8)
    print("\n")
    print("--- ТЕСТ 5: Spirit Bebop (Творческая T=0.8) ---")
    generate_build("Spirit/Bomb Bebop", num_items=20, temperature=3, ability_temp=0.8)
