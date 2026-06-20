import os
import json
import numpy as np
import xgboost as xgb
import pandas as pd

class DeadlockBuildGenerator:
    def __init__(self, hero_id=15, archetype=0):
        self.hero_id = hero_id
        self.archetype = archetype
        
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.models_dir = os.path.join(base_dir, "ml", "models")
        self.dict_dir = os.path.join(base_dir, "data", "dictionary")
        
        # Загрузка словарей
        with open(os.path.join(self.dict_dir, "shop_items_dict.json"), "r", encoding="utf-8") as f:
            self.shop_dict = json.load(f)
            
        with open(os.path.join(self.dict_dir, "abilities_dict.json"), "r", encoding="utf-8") as f:
            abilities = json.load(f)
            self.hero_abilities = abilities.get(str(hero_id), {})
            
        # Загрузка маппингов (Target ID -> Original ID)
        with open(os.path.join(self.models_dir, f"item_mapping_hero_{hero_id}.json"), "r") as f:
            # json ключи всегда строки, конвертируем обратно в int
            self.item_mapping = {int(k): int(v) for k, v in json.load(f).items()}
            
        with open(os.path.join(self.models_dir, f"ability_mapping_hero_{hero_id}.json"), "r") as f:
            self.ability_mapping = {int(k): int(v) for k, v in json.load(f).items()}
            
        # Загрузка моделей
        self.item_model = xgb.XGBClassifier()
        self.item_model.load_model(os.path.join(self.models_dir, f"xgb_items_hero_{hero_id}.json"))
        
        self.ability_model = xgb.XGBClassifier()
        self.ability_model.load_model(os.path.join(self.models_dir, f"xgb_abilities_hero_{hero_id}.json"))
        
        # Инициализация состояния
        self.inventory = [] # Максимум 12
        self.ability_points_spent = 0 # Максимум 16
        self.ability_levels = {skill_id: 0 for skill_id in self.hero_abilities.keys()}
        
        self.item_history = []
        self.ability_history = []

    def count_active_items(self):
        active_count = 0
        for item_id in self.inventory:
            item_info = self.shop_dict.get(str(item_id), {})
            # Предположим, что у нас есть флаг is_active в словаре (или определяем по слову Active в названии)
            # В Deadlock активные предметы лежат в тех же слотах, но их не может быть больше 4
            # Если нет флага, в будущем можно парсить из описания. Пока оставим задел:
            if item_info.get("is_active", False) or "Active" in item_info.get("description", ""):
                active_count += 1
        return active_count

    def sell_cheapest_item(self):
        if not self.inventory:
            return False
            
        # Находим самый дешевый предмет (800 душ)
        cheapest_item = None
        min_cost = 99999
        
        for item_id in self.inventory:
            cost = self.shop_dict.get(str(item_id), {}).get("cost", 9999)
            if cost < min_cost:
                min_cost = cost
                cheapest_item = item_id
                
        if cheapest_item:
            self.inventory.remove(cheapest_item)
            item_name = self.shop_dict.get(str(cheapest_item), {}).get("name", "Unknown")
            print(f"[-] ПРОДАЖА: Продан дешевый предмет '{item_name}' ({min_cost} душ) для освобождения слота!")
            return True
        return False

    def check_and_apply_upgrade(self, new_item_id):
        new_item_info = self.shop_dict.get(str(new_item_id), {})
        components = new_item_info.get("components", [])
        
        # Если у предмета есть компоненты, проверяем, есть ли они в инвентаре
        if components:
            for comp_class_name in components:
                # Ищем ID по class_name
                comp_id = None
                for k, v in self.shop_dict.items():
                    if v.get("class_name") == comp_class_name:
                        comp_id = int(k)
                        break
                        
                if comp_id and comp_id in self.inventory:
                    # Апгрейд!
                    self.inventory.remove(comp_id)
                    self.inventory.append(new_item_id)
                    
                    old_name = self.shop_dict.get(str(comp_id), {}).get("name", "Unknown")
                    new_name = new_item_info.get("name", "Unknown")
                    cost_diff = new_item_info.get("cost", 0) - self.shop_dict.get(str(comp_id), {}).get("cost", 0)
                    
                    print(f"[^] УЛУЧШЕНИЕ: '{old_name}' -> '{new_name}' (Доплата: {cost_diff} душ). Слот сохранен.")
                    return True
        return False

    def predict_next_item(self, strict_rules=False, temperature=1.0):
        # Формируем X: [archetype, step_1, ..., step_24]
        max_seq_length = 24
        x_input = [self.archetype] + self.item_history[-max_seq_length:]
        while len(x_input) < max_seq_length + 1:
            x_input.append(0)
            
        x_df = pd.DataFrame([x_input], columns=['archetype'] + [f'item_step_{i+1}' for i in range(max_seq_length)])
        
        # Получаем сырые логиты (до применения Softmax)
        logits = self.item_model.predict(x_df, output_margin=True)[0]
        
        # Применяем температуру
        # Если temperature -> 0, это жадный поиск (всегда берется максимальный)
        # Если temperature -> infinity, это случайный выбор
        temperature = max(0.01, temperature) # Избегаем деления на ноль
        scaled_logits = logits / temperature
        
        # Избегаем переполнения при экспоненте
        scaled_logits -= np.max(scaled_logits)
        exp_logits = np.exp(scaled_logits)
        probs = exp_logits / np.sum(exp_logits)
        
        # Сортируем индексы от наибольшей вероятности к меньшей
        # Чтобы высокие температуры давали настоящий хаос, мы расширяем пул кандидатов в зависимости от температуры
        # При temp=1.0 -> пул из топ-10. При temp=5.0 -> пул из топ-50!
        top_k = max(3, int(10 * temperature))
        top_k = min(top_k, len(probs)) # Не выходим за рамки всех предметов
        
        top_indices = np.argsort(probs)[::-1][:top_k]
        top_probs = probs[top_indices]
        top_probs = top_probs / np.sum(top_probs) # Нормализуем заново для top-k
        
        # Сэмплируем кандидата с учетом вероятностей
        valid_candidates = []
        for idx in top_indices:
            candidate_item_id = self.item_mapping[idx]
            
            # Проверка 1: Предмет уже есть в инвентаре?
            if candidate_item_id in self.inventory:
                continue
                
            candidate_info = self.shop_dict.get(str(candidate_item_id), {})
            candidate_class = candidate_info.get("class_name", "")
            candidate_name = candidate_info.get("name", "").lower()
            
            BLACKLISTED_ITEMS = {
                "conjure missiles", "endless magazine", "glass cannon v2", 
                "enduring spirit", "patron's healing", "bullet armor", 
                "toughness", "spirit armor", "hexafoil ward", 
                "majestic leap - disabled", "soul rebirth", "ammo scavenger", 
                "hex-sealed knuckles", "soul explosion", "rebirth"
            }
            # Проверка на служебные/скрытые предметы
            if candidate_name.startswith("upgrade_") or candidate_name.startswith("item_") or candidate_name in BLACKLISTED_ITEMS:
                continue
                
            # Проверка 2: Лимит активных предметов
            if candidate_info.get("is_active", False) and self.count_active_items() >= 4:
                continue
                
            # Проверка 3: БАГФИКС - не покупаем компонент, если грейд уже куплен!
            # Например, если есть Enduring Speed, не покупаем Sprint Boots
            is_component_of_existing = False
            for inv_item_id in self.inventory:
                inv_item_info = self.shop_dict.get(str(inv_item_id), {})
                inv_components = inv_item_info.get("components", [])
                if candidate_class and candidate_class in inv_components:
                    is_component_of_existing = True
                    break
                    
            if is_component_of_existing:
                continue
                
            valid_candidates.append(idx)
            
        if not valid_candidates:
            # Fallback: pick any item not in inventory
            available = []
            BLACKLISTED_ITEMS = {
                "conjure missiles", "endless magazine", "glass cannon v2", 
                "enduring spirit", "patron's healing", "bullet armor", 
                "toughness", "spirit armor", "hexafoil ward", 
                "majestic leap - disabled", "soul rebirth", "ammo scavenger", 
                "hex-sealed knuckles", "soul explosion", "rebirth"
            }
            for item_id_str, info in self.shop_dict.items():
                iid = int(item_id_str)
                name = info.get("name", "").lower()
                c_class = info.get("class_name", "").lower()
                if iid not in self.inventory and not name.startswith("upgrade_") and not name.startswith("item_") and name not in BLACKLISTED_ITEMS:
                    available.append(iid)
            if not available:
                return False
            candidate_item_id = np.random.choice(available)
        else:
            # Заново считаем вероятности только для валидных кандидатов
            valid_probs = [probs[idx] for idx in valid_candidates]
            valid_probs = valid_probs / np.sum(valid_probs)
            
            # ВЫБОР С УЧЕТОМ ТЕМПЕРАТУРЫ (Сэмплирование)
            chosen_idx = np.random.choice(valid_candidates, p=valid_probs)
            candidate_item_id = self.item_mapping[chosen_idx]
            
        candidate_info = self.shop_dict.get(str(candidate_item_id), {})
        
        if not strict_rules:
            self.inventory.append(candidate_item_id)
            name = candidate_info.get("name", str(candidate_item_id))
            cost = candidate_info.get("cost", 0)
            print(f"[+] ПОКУПКА: '{name}' ({cost} душ).")
            self.item_history.append(candidate_item_id)
            return True

            # Проверка 3: Если инвентарь полон (12 слотов), пробуем улучшить или продать
            if len(self.inventory) >= 12:
                # Пытаемся сделать апгрейд
                if self.check_and_apply_upgrade(candidate_item_id):
                    self.item_history.append(candidate_item_id)
                    return True # Успешно апгрейднули
                    
                # Если не апгрейд, надо продать мусор
                if self.sell_cheapest_item():
                    self.inventory.append(candidate_item_id)
                    name = candidate_info.get("name", str(candidate_item_id))
                    cost = candidate_info.get("cost", 0)
                    print(f"[+] ПОКУПКА: '{name}' ({cost} душ). Инвентарь снова полон (12/12).")
                    self.item_history.append(candidate_item_id)
                    return True
                else:
                    return False
            else:
                # Слоты есть. Пробуем апгрейд (вдруг компонент есть)
                if self.check_and_apply_upgrade(candidate_item_id):
                    self.item_history.append(candidate_item_id)
                    return True
                else:
                    # Просто покупаем
                    self.inventory.append(candidate_item_id)
                    name = candidate_info.get("name", str(candidate_item_id))
                    cost = candidate_info.get("cost", 0)
                    print(f"[+] ПОКУПКА: '{name}' ({cost} душ). Слотов занято: {len(self.inventory)}/12.")
                    self.item_history.append(candidate_item_id)
                    return True
                    
        return False

    def predict_next_ability(self, temperature=1.0):
        if self.ability_points_spent >= 16:
            return False
            
        max_seq_length = 16
        x_input = [self.archetype] + self.ability_history[-max_seq_length:]
        while len(x_input) < max_seq_length + 1:
            x_input.append(0)
            
        x_df = pd.DataFrame([x_input], columns=['archetype'] + [f'ability_step_{i+1}' for i in range(max_seq_length)])
        
        logits = self.ability_model.predict(x_df, output_margin=True)[0]
        
        temperature = max(0.01, temperature)
        scaled_logits = logits / temperature
        
        scaled_logits -= np.max(scaled_logits)
        exp_logits = np.exp(scaled_logits)
        probs = exp_logits / np.sum(exp_logits)
        
        # Способностей у героя всего 4, так что top_k должен быть маленьким
        top_k = max(2, int(2 * temperature))
        top_k = min(top_k, len(probs))
        
        top_indices = np.argsort(probs)[::-1][:top_k]
        top_probs = probs[top_indices]
        top_probs = top_probs / np.sum(top_probs)
        
        valid_candidates = []
        for idx in top_indices:
            candidate_ability_id = self.ability_mapping[idx]
            str_id = str(candidate_ability_id)
            if str_id not in self.hero_abilities:
                continue
            if self.ability_levels.get(str_id, 0) >= 4:
                continue
            valid_candidates.append(idx)
            
        if not valid_candidates:
            # Fallback: pick any available ability for this hero
            available = []
            for ab_id in self.hero_abilities:
                if self.ability_levels.get(str(ab_id), 0) < 4:
                    available.append(int(ab_id))
            if not available:
                return False
            candidate_ability_id = np.random.choice(available)
            str_id = str(candidate_ability_id)
        else:
            valid_probs = [probs[idx] for idx in valid_candidates]
            valid_probs = valid_probs / np.sum(valid_probs)
            
            chosen_idx = np.random.choice(valid_candidates, p=valid_probs)
            candidate_ability_id = self.ability_mapping[chosen_idx]
            str_id = str(candidate_ability_id)
        
        # Все проверки пройдены!
        self.ability_levels[str_id] += 1
        self.ability_points_spent += 1
        self.ability_history.append(candidate_ability_id)
        
        ab_name = self.hero_abilities[str_id].get("name", "Unknown Skill")
        level = self.ability_levels[str_id]
        
        action = "ОТКРЫТИЕ" if level == 1 else f"УЛУЧШЕНИЕ (T{level-1})"
        print(f"[*] СКИЛЛ: {action} '{ab_name}'. Очков потрачено: {self.ability_points_spent}/16.")
        return True

    def generate_full_build(self, max_items=24, strict_rules=False, temperature=1.0):
        print(f"\n{'='*60}")
        print(f"ГЕНЕРАЦИЯ БИЛДА (Герой: {self.hero_id}, Архетип: {self.archetype}, Строгие правила: {strict_rules}, Температура: {temperature})")
        print(f"{'='*60}\n")
        
        print("--- ПОРЯДОК ПРОКАЧКИ СПОСОБНОСТЕЙ ---")
        while self.ability_points_spent < 16:
            if not self.predict_next_ability(temperature=temperature):
                break # Если модель не может предсказать, прерываем цикл
                
        print("\n--- ПОРЯДОК ПОКУПКИ ПРЕДМЕТОВ ---")
        for step in range(max_items):
            self.predict_next_item(strict_rules=strict_rules, temperature=temperature)
            
        print(f"\n{'='*60}")
        limit_text = "(Макс 12 слотов)" if strict_rules else "(Без лимита слотов)"
        print(f"ФИНАЛЬНЫЙ ИНВЕНТАРЬ {limit_text}:")
        for item_id in self.inventory:
            name = self.shop_dict.get(str(item_id), {}).get("name", "Unknown")
            cost = self.shop_dict.get(str(item_id), {}).get("cost", 0)
            print(f" - {name} ({cost} душ)")
        print(f"{'='*60}\n")

if __name__ == "__main__":
    try:
        generator = DeadlockBuildGenerator(hero_id=15, archetype=0) # Пробуем Weapon Bebop
        
        for temp in [2.0]:
            generator.item_history = []
            generator.inventory = []
            generator.ability_points_spent = 0
            generator.ability_history = []
            # Сброс уровней способностей
            generator.ability_levels = {ab_id: 0 for ab_id in generator.hero_abilities}
            generator.generate_full_build(max_items=24, strict_rules=False, temperature=temp)
            
    except Exception as e:
        print(f"Ошибка при запуске (возможно модели еще обучаются): {e}")
