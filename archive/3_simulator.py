import json
import random
import numpy as np
import joblib

def load_json(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def vectorize_state(state, kb, all_items, all_abilities, all_stats):
    current_items = state.get("items", [])
    current_aps = state.get("ap", [])
    
    item_vec = [1 if item_id in current_items else 0 for item_id in all_items]
    ap_vec = [current_aps.count(ab_id) for ab_id in all_abilities]
    
    stat_vec = {stat: 0.0 for stat in all_stats}
    for item_id in current_items:
        bonuses = kb.get(item_id, {}).get("stat_bonuses", {})
        for stat_name, value in bonuses.items():
            try:
                stat_vec[stat_name] += float(value)
            except: pass
            
    stat_vec_list = [stat_vec[stat] for stat in all_stats]
    return item_vec + ap_vec + stat_vec_list

class AIBuildSimulator:
    def __init__(self):
        print("🧠 Загрузка ИИ...")
        self.model = joblib.load("bebop_ai_model.pkl")
        self.meta = load_json("bebop_ai_meta.json")
        self.kb = load_json("knowledge_base.json")
        
        self.all_items = self.meta["all_items"]
        self.all_abilities = self.meta["all_abilities"]
        self.all_stats = self.meta["all_stats"]
        self.idx_to_target = {int(k): str(v) for k, v in self.meta["idx_to_target"].items()}
        
        # Экономика и Статы Игрока
        self.wallet_souls = 0        # Души в кармане (Тратим)
        self.networth_souls = 0      # Всего заработано (Определяет уровень и AP)
        self.available_ap = 1        # Стартовый поинт
        self.total_ap_earned = 1
        
        self.current_aps = []
        self.inventory = {
            "weapon": [],
            "spirit": [],
            "vitality": []
        }
        self.active_count = 0
        self.max_actives = 4

    def check_ap_milestone(self, old_networth, new_networth):
        """В Deadlock AP выдаются за определенные пороги душ"""
        # Упрощенная таблица порогов выдачи AP (примерно как в игре)
        milestones = [500, 1000, 1500, 2000, 2500, 3000, 4000, 5000, 6500, 8000, 9500, 11500, 13500, 15500, 18000, 21000, 24000]
        gained_ap = 0
        for m in milestones:
            if old_networth < m <= new_networth:
                gained_ap += 1
        return gained_ap

    def get_skill_cost(self, ability_id):
        """Стоимость прокачки: Открытие=1, T1=1, T2=2, T3=5"""
        lvl = self.current_aps.count(ability_id)
        if lvl == 0: return 1
        if lvl == 1: return 1
        if lvl == 2: return 2
        if lvl == 3: return 5
        return 999 # Максимум

    def get_all_owned_items(self):
        return self.inventory["weapon"] + self.inventory["spirit"] + self.inventory["vitality"]

    def mask_illegal_moves(self, probabilities):
        """Обнуляем вероятности действий, которые физически невозможны (чтобы ИИ их не хотел)"""
        owned_items = self.get_all_owned_items()
        
        for idx, prob in enumerate(probabilities):
            if prob == 0: continue
            target_id = self.idx_to_target[idx]
            item_info = self.kb.get(target_id, {})
            
            # 1. Если это скилл
            if item_info.get("type") == "ability":
                lvl = self.current_aps.count(target_id)
                if lvl >= 4: # Скилл замакшен
                    probabilities[idx] = 0
                elif lvl == 0 and self.networth_souls < 3000 and "ult" in item_info.get("class_name", "").lower():
                    # Запрещаем ульту до 3000 душ
                    probabilities[idx] = 0
                continue
                
            # 2. Если это предмет
            # Уже есть?
            if target_id in owned_items:
                probabilities[idx] = 0
                continue
                
        return probabilities

    def sell_worst_item(self, target_slot_type):
        """Продает самый дешевый предмет в категории, если он не является компонентом"""
        owned = self.inventory[target_slot_type]
        if not owned: return False
        
        # Сортируем по цене, чтобы продать самое дешевое
        # В идеале тут ИИ должен оценивать "полезность", но цена для старта отлично работает
        candidates = []
        for i_id in owned:
            cost = self.kb[i_id].get("cost", 0)
            candidates.append((cost, i_id))
            
        candidates.sort()
        sold_id = candidates[0][1]
        sold_cost = candidates[0][0]
        
        # Возвращаем 50% стоимости (как в игре)
        refund = sold_cost // 2
        self.wallet_souls += refund
        self.inventory[target_slot_type].remove(sold_id)
        
        if self.kb[sold_id].get("is_active"):
            self.active_count -= 1
            
        print(f"     [!] Инвентарь {target_slot_type.upper()} полон. 💰 ПРОДАНО: {self.kb[sold_id].get('name')} (+{refund} Souls)")
        return True

    def simulate(self, target_networth=25000):
        print("\n🎮 СИМУЛЯЦИЯ МАТЧА (Начало игры, 0 Souls)")
        print("-" * 65)
        
        steps_without_action = 0
        
        while self.networth_souls < target_networth:
            owned_items = self.get_all_owned_items()
            state = {"items": owned_items, "ap": self.current_aps}
            vec = vectorize_state(state, self.kb, self.all_items, self.all_abilities, self.all_stats)
            
            # ИИ предсказывает синергии
            probs = self.model.predict_proba([vec])[0]
            probs = self.mask_illegal_moves(probs)
            
            # Берем самую желанную цель
            best_idx = np.argmax(probs)
            if probs[best_idx] == 0:
                print("Модель не знает, что делать дальше. Конец билда.")
                break
                
            target_id = self.idx_to_target[best_idx]
            info = self.kb.get(target_id, {})
            name = info.get("name", target_id)
            
            action_taken = False
            
            # --- Пытаемся ПРОКАЧАТЬ СКИЛЛ ---
            if info.get("type") == "ability":
                cost_ap = self.get_skill_cost(target_id)
                if self.available_ap >= cost_ap:
                    self.available_ap -= cost_ap
                    self.current_aps.append(target_id)
                    lvl = self.current_aps.count(target_id)
                    lvl_str = ["Открыт", "Tier 1", "Tier 2", "Tier 3"][lvl-1]
                    print(f"[{self.networth_souls:>5} Souls] 🔼 ПРОКАЧАНО: {name} ({lvl_str}) [Потрачено {cost_ap} AP]")
                    action_taken = True
                else:
                    # ИИ хочет скилл, но нет AP -> Фармим!
                    pass 
                    
            # --- Пытаемся КУПИТЬ ПРЕДМЕТ ---
            else:
                base_cost = info.get("cost", 0)
                actual_cost = base_cost
                slot_type = info.get("slot_type", "weapon")
                
                # Проверяем, есть ли компонент для апгрейда (Скидка)
                upgrade_base_id = None
                for comp in info.get("components", []):
                    for o_id in owned_items:
                        if self.kb[o_id].get("class_name") == comp:
                            upgrade_base_id = o_id
                            actual_cost -= self.kb[o_id].get("cost", 0)
                            break
                            
                if self.wallet_souls >= actual_cost:
                    # Проверяем слоты
                    slot_is_full = len(self.inventory.get(slot_type, [])) >= 4
                    
                    if slot_is_full and upgrade_base_id is None:
                        # Слот забит, это не апгрейд. Нужно что-то продать!
                        if self.sell_worst_item(slot_type):
                            slot_is_full = False
                        else:
                            # Не смогли продать (невозможно) -> блокируем эту цель
                            pass
                            
                    if not slot_is_full or upgrade_base_id is not None:
                        # Покупаем!
                        self.wallet_souls -= actual_cost
                        
                        if upgrade_base_id:
                            self.inventory[slot_type].remove(upgrade_base_id)
                            if self.kb[upgrade_base_id].get("is_active"): self.active_count -= 1
                            print(f"[{self.networth_souls:>5} Souls] ⏫ АПГРЕЙД: {self.kb[upgrade_base_id].get('name')} ➔ {name} (Доплачено {actual_cost})")
                        else:
                            act_tag = " ⚡" if info.get("is_active") else ""
                            print(f"[{self.networth_souls:>5} Souls] ➕ КУПЛЕНО: {name} ({actual_cost} Souls){act_tag}")
                            
                        self.inventory[slot_type].append(target_id)
                        if info.get("is_active"): self.active_count += 1
                        action_taken = True

            # --- ЭКОНОМИЧЕСКИЙ ЦИКЛ (Фарм) ---
            if action_taken:
                steps_without_action = 0 # Сбрасываем счетчик ожидания
            else:
                # Если мы ничего не сделали (копим на дорогую шмотку или ждем AP)
                # "Фармим" 250 душ
                farm_amount = 250
                old_net = self.networth_souls
                self.wallet_souls += farm_amount
                self.networth_souls += farm_amount
                
                # Проверяем, не дали ли нам AP за фарм?
                new_ap = self.check_ap_milestone(old_net, self.networth_souls)
                if new_ap > 0:
                    self.available_ap += new_ap
                    self.total_ap_earned += new_ap
                    
                steps_without_action += 1
                if steps_without_action > 50:
                    print(f"\n⚠️ ИИ застрял (не может накопить или забаговал). Остановка симуляции.")
                    break

        # ФИНАЛЬНЫЙ ОТЧЕТ
        print("-" * 65)
        print(f"🏆 ФИНАЛЬНЫЙ БИЛД (Networth: {self.networth_souls} Souls | AP заработано: {self.total_ap_earned})")
        
        for s_type in ["weapon", "spirit", "vitality"]:
            print(f"\n🔹 {s_type.upper()} ({len(self.inventory[s_type])}/4):")
            items = [self.kb.get(i, {}) for i in self.inventory[s_type]]
            items.sort(key=lambda x: x.get("cost", 0), reverse=True)
            for it in items:
                act = "⚡" if it.get("is_active") else " "
                print(f"   {act} {it.get('name', '?'):<20} | {it.get('cost', 0)} S")

if __name__ == "__main__":
    sim = AIBuildSimulator()
    sim.simulate(target_networth=25000)