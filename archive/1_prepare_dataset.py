import json
import sys
from collections import Counter
from sklearn.model_selection import train_test_split
from tqdm import tqdm

def load_json(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Ошибка загрузки {filepath}: {e}")
        sys.exit(1)

def extract_timeline(build, kb):
    """
    Превращает сырой билд в хронологическую последовательность действий.
    С усиленной защитой от null-значений в JSON.
    """
    hero_build = build.get("hero_build") or {}
    details = hero_build.get("details") or {}
    
    # 1. Достаем порядок способностей
    ability_order = details.get("ability_order") or {}
    currency_changes = ability_order.get("currency_changes") or []
    
    ap_sequence = []
    for ch in currency_changes:
        if not isinstance(ch, dict): continue
        ab_id = str(ch.get("ability_id"))
        if ab_id in kb:
            ap_sequence.append(ab_id)
    
    # 2. Достаем предметы по стадиям
    categories = details.get("mod_categories") or []
    items_early, items_mid, items_late = [], [], []
    
    num_cats = len(categories)
    for i, cat in enumerate(categories):
        if not isinstance(cat, dict): continue
        
        phase_idx = min(2, int((i / max(1, num_cats)) * 3))
        
        mods_raw = cat.get("mods") or [] # Защита от null
        valid_mods = []
        for m in mods_raw:
            if not isinstance(m, dict): continue
            m_id = str(m.get("ability_id"))
            if m_id in kb and not kb[m_id].get("is_ability"):
                valid_mods.append(m_id)
        
        if phase_idx == 0: items_early.extend(valid_mods)
        elif phase_idx == 1: items_mid.extend(valid_mods)
        else: items_late.extend(valid_mods)
        
    # Собираем таймлайн (чередуем AP и шмотки)
    timeline = []
    ap_idx = 0
    
    # Сначала пара скиллов (открытие на старте игры)
    while ap_idx < min(3, len(ap_sequence)):
        timeline.append({"type": "ap", "id": ap_sequence[ap_idx]})
        ap_idx += 1
        
    # Early стадия
    for item in items_early:
        timeline.append({"type": "item", "id": item})
        if ap_idx < len(ap_sequence) and len(timeline) % 2 == 0:
            timeline.append({"type": "ap", "id": ap_sequence[ap_idx]})
            ap_idx += 1
            
    # Mid стадия
    for item in items_mid:
        timeline.append({"type": "item", "id": item})
        if ap_idx < len(ap_sequence) and len(timeline) % 3 == 0:
            timeline.append({"type": "ap", "id": ap_sequence[ap_idx]})
            ap_idx += 1
            
    # Late стадия
    for item in items_late:
        timeline.append({"type": "item", "id": item})
        
    # Добиваем оставшиеся AP
    while ap_idx < len(ap_sequence):
        timeline.append({"type": "ap", "id": ap_sequence[ap_idx]})
        ap_idx += 1
        
    return timeline

def process_data():
    print("Инициализация обработки датасета...")
    builds_raw = load_json("teacher_builds.json")
    kb = load_json("knowledge_base.json")
    
    valid_builds = []
    discarded_reasons = Counter()
    
    # Обработка билдов с прогресс баром
    for build in tqdm(builds_raw, desc="Анализ сборок"):
        timeline = extract_timeline(build, kb)
        
        # Валидация
        ap_count = sum(1 for action in timeline if action["type"] == "ap")
        item_count = sum(1 for action in timeline if action["type"] == "item")
        
        if ap_count < 4:
            discarded_reasons["Слишком мало прокачек AP (<4)"] += 1
            continue
        if item_count < 6:
            discarded_reasons["Слишком мало предметов (<6)"] += 1
            continue
            
        valid_builds.append({
            "build_id": build.get("hero_build", {}).get("hero_build_id", "unknown"),
            "timeline": timeline
        })

    # Аналитика до сплита
    print("\n--- АНАЛИТИКА ФИЛЬТРАЦИИ ---")
    print(f"Всего загружено гайдов: {len(builds_raw)}")
    print(f"Допущено к обучению: {len(valid_builds)}")
    if discarded_reasons:
        print("Отбраковано по причинам:")
        for reason, count in discarded_reasons.items():
            print(f" - {reason}: {count}")

    if not valid_builds:
        print("Критическая ошибка: нет валидных сборок для обучения!")
        sys.exit(1)

    # Train/Test Split (80% / 20%)
    train_builds, test_builds = train_test_split(valid_builds, test_size=0.2, random_state=42)
    
    def generate_states(build_list):
        dataset = []
        for b in build_list:
            current_state_items = []
            current_state_ap = []
            
            for action in b["timeline"]:
                dataset.append({
                    "state": {
                        "items": list(current_state_items),
                        "ap": list(current_state_ap)
                    },
                    "target": action
                })
                if action["type"] == "item":
                    current_state_items.append(action["id"])
                else:
                    current_state_ap.append(action["id"])
        return dataset

    train_dataset = generate_states(train_builds)
    test_dataset = generate_states(test_builds)

    # Сохранение результатов
    with open("dataset_train.json", "w", encoding="utf-8") as f:
        json.dump(train_dataset, f, indent=2)
    with open("dataset_test.json", "w", encoding="utf-8") as f:
        json.dump(test_dataset, f, indent=2)

    # Финальная аналитика
    target_items = [d["target"]["id"] for d in train_dataset if d["target"]["type"] == "item"]
    top_items = Counter(target_items).most_common(5)
    
    print("\n--- АНАЛИТИКА ДАТАСЕТА ---")
    print(f"Тренировочная выборка (Train): {len(train_builds)} гайдов -> {len(train_dataset)} шагов/примеров")
    print(f"Тестовая выборка (Test): {len(test_builds)} гайдов -> {len(test_dataset)} шагов/примеров")
    print("Топ-5 самых частых целевых предметов (Targets) в Train:")
    for item_id, count in top_items:
        name = kb.get(item_id, {}).get("name", item_id)
        print(f" - {name}: {count} раз")

if __name__ == "__main__":
    process_data()