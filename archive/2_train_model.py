import json
import sys
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib
from tqdm import tqdm

def load_json(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def extract_all_possible_stats(kb):
    """Собираем все уникальные названия статов из всех предметов в базе"""
    all_stats = set()
    for item_id, data in kb.items():
        bonuses = data.get("stat_bonuses", {})
        for stat_name in bonuses.keys():
            all_stats.add(stat_name)
    return sorted(list(all_stats))

def vectorize_state(state, kb, all_items, all_abilities, all_stats):
    """
    Превращаем инвентарь и скиллы в математический вектор для Нейросети.
    Это 'глаза' нашей модели.
    """
    current_items = state.get("items", [])
    current_aps = state.get("ap", [])
    
    # 1. Multi-hot вектор предметов (1 если предмет есть, 0 если нет)
    item_vec = [1 if item_id in current_items else 0 for item_id in all_items]
    
    # 2. Вектор прокачки способностей (считаем уровни от 0 до 3+)
    ap_vec = [current_aps.count(ab_id) for ab_id in all_abilities]
    
    # 3. Вектор СУММАРНЫХ СТАТОВ (Синергия!)
    stat_vec = {stat: 0.0 for stat in all_stats}
    for item_id in current_items:
        bonuses = kb.get(item_id, {}).get("stat_bonuses", {})
        for stat_name, value in bonuses.items():
            try:
                stat_vec[stat_name] += float(value)
            except (ValueError, TypeError):
                pass # Пропускаем нечисловые статы (если вдруг попадутся)
                
    stat_vec_list = [stat_vec[stat] for stat in all_stats]
    
    # Склеиваем всё в один огромный вектор признаков (Features)
    return item_vec + ap_vec + stat_vec_list

def train_and_evaluate():
    print("🚀 Инициализация обучения модели...")
    
    kb = load_json("knowledge_base.json")
    train_data = load_json("dataset_train.json")
    test_data = load_json("dataset_test.json")
    
    # Собираем словари всех возможных сущностей для фиксированного размера вектора
    all_items = sorted([k for k, v in kb.items() if not v.get("is_ability") and v.get("type") != "ability"])
    all_abilities = sorted([k for k, v in kb.items() if v.get("type") == "ability"])
    all_stats = extract_all_possible_stats(kb)
    
    # Собираем классы (Targets), которые модель должна уметь предсказывать
    all_targets = list(set([d["target"]["id"] for d in train_data + test_data]))
    target_to_idx = {t_id: i for i, t_id in enumerate(all_targets)}
    idx_to_target = {i: t_id for t_id, i in target_to_idx.items()}
    
    print(f"📊 Размерность данных:")
    print(f" - Уникальных предметов (Items): {len(all_items)}")
    print(f" - Способностей героя (Abilities): {len(all_abilities)}")
    print(f" - Уникальных статов (Math Stats): {len(all_stats)}")
    print(f" - Возможных действий (Классов для предсказания): {len(all_targets)}")
    
    # === ПОДГОТОВКА X (Признаки) и y (Ответы) ===
    print("\n⚙️ Векторизация обучающей выборки (Train)...")
    X_train, y_train = [], []
    for d in tqdm(train_data):
        X_train.append(vectorize_state(d["state"], kb, all_items, all_abilities, all_stats))
        y_train.append(target_to_idx[d["target"]["id"]])
        
    print("⚙️ Векторизация тестовой выборки (Test)...")
    X_test, y_test = [], []
    for d in tqdm(test_data):
        X_test.append(vectorize_state(d["state"], kb, all_items, all_abilities, all_stats))
        y_test.append(target_to_idx[d["target"]["id"]])
        
    X_train, y_train = np.array(X_train), np.array(y_train)
    X_test, y_test = np.array(X_test), np.array(y_test)
    
    # === ОБУЧЕНИЕ МОДЕЛИ ===
    print("\n🧠 Обучение Random Forest (Поиск синергий)... Это займет секунд 10-30.")
    # Используем 200 деревьев, ограничение глубины для защиты от переобучения
    model = RandomForestClassifier(n_estimators=50, max_depth=15, min_samples_leaf=5, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    
    # === ОЦЕНКА ТОЧНОСТИ ===
    print("\n🎯 Оценка модели на скрытых тестовых данных...")
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)
    
    # Top-1 Accuracy
    acc_top1 = accuracy_score(y_test, y_pred)
    
    # Top-3 Accuracy (Модель угадала предмет, предложив 3 лучших варианта)
    top3_preds = np.argsort(y_pred_proba, axis=1)[:, -3:]
    acc_top3 = np.mean([1 if y_test[i] in top3_preds[i] else 0 for i in range(len(y_test))])
    
    print(f"✅ Точность Top-1 (Точное попадание): {acc_top1 * 100:.2f}%")
    print(f"✅ Точность Top-3 (Предмет в тройке рекомендаций): {acc_top3 * 100:.2f}%")
    
    if acc_top3 > 0.4:
        print("💡 Отличный результат! В реальной игре выбор из 3-5 адекватных предметов — это и есть мета.")
    else:
        print("⚠️ Точность маловата, но для MVP пойдет. Позже добавим больше данных.")

    # === СОХРАНЕНИЕ ВЕСОВ ===
    model_data = {
        "all_items": all_items,
        "all_abilities": all_abilities,
        "all_stats": all_stats,
        "idx_to_target": idx_to_target
    }
    
    joblib.dump(model, "bebop_ai_model.pkl")
    with open("bebop_ai_meta.json", "w", encoding="utf-8") as f:
        json.dump(model_data, f, indent=2)
        
    print("\n💾 Модель ('bebop_ai_model.pkl') и маппинг сохранены. Можно писать Симулятор!")

if __name__ == "__main__":
    train_and_evaluate()