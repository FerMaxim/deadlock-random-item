import os
import pandas as pd
import numpy as np
import xgboost as xgb
import json
from sklearn.preprocessing import LabelEncoder
import time

def train_models_for_hero(target_hero_id=15):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    training_dir = os.path.join(base_dir, "training")
    models_dir = os.path.join(base_dir, "ml", "models")
    os.makedirs(models_dir, exist_ok=True)
    
    print(f"=== ОБУЧЕНИЕ МОДЕЛЕЙ ДЛЯ ГЕРОЯ {target_hero_id} ===")
    
    # ---------------------------------------------------------
    # 1. Обучение модели предметов (Items)
    # ---------------------------------------------------------
    items_x_path = os.path.join(training_dir, f"xgb_items_X_hero_{target_hero_id}.csv")
    items_y_path = os.path.join(training_dir, f"xgb_items_Y_hero_{target_hero_id}.csv")
    
    print("\n[Предметы] Загрузка датасетов...")
    X_items = pd.read_csv(items_x_path)
    Y_items = pd.read_csv(items_y_path)
    
    print(f"[Предметы] Размер выборки: {X_items.shape}")
    
    # Кодируем таргеты (Item ID -> 0, 1, 2...)
    le_items = LabelEncoder()
    y_encoded = le_items.fit_transform(Y_items['target_item'])
    num_classes_items = len(le_items.classes_)
    
    # Сохраняем маппинг
    item_mapping = {int(class_idx): int(original_id) for class_idx, original_id in enumerate(le_items.classes_)}
    with open(os.path.join(models_dir, f"item_mapping_hero_{target_hero_id}.json"), "w") as f:
        json.dump(item_mapping, f, indent=4)
        
    print(f"[Предметы] Уникальных предметов для предсказания: {num_classes_items}")
    print("[Предметы] Запуск обучения XGBoost (это может занять пару минут)...")
    
    start_time = time.time()
    model_items = xgb.XGBClassifier(
        objective='multi:softprob',
        num_class=num_classes_items,
        tree_method='hist', # Быстрое обучение на CPU
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        n_jobs=-1,
        random_state=42
    )
    model_items.fit(X_items, y_encoded)
    
    item_model_path = os.path.join(models_dir, f"xgb_items_hero_{target_hero_id}.json")
    model_items.save_model(item_model_path)
    print(f"[Предметы] Обучение завершено за {time.time() - start_time:.1f} сек! Модель сохранена.")
    
    # ---------------------------------------------------------
    # 2. Обучение модели способностей (Abilities)
    # ---------------------------------------------------------
    abilities_x_path = os.path.join(training_dir, f"xgb_abilities_X_hero_{target_hero_id}.csv")
    abilities_y_path = os.path.join(training_dir, f"xgb_abilities_Y_hero_{target_hero_id}.csv")
    
    print("\n[Способности] Загрузка датасетов...")
    X_abilities = pd.read_csv(abilities_x_path)
    Y_abilities = pd.read_csv(abilities_y_path)
    
    print(f"[Способности] Размер выборки: {X_abilities.shape}")
    
    # Кодируем таргеты
    le_abilities = LabelEncoder()
    y_encoded_ab = le_abilities.fit_transform(Y_abilities['target_ability'])
    num_classes_ab = len(le_abilities.classes_)
    
    # Сохраняем маппинг
    ability_mapping = {int(class_idx): int(original_id) for class_idx, original_id in enumerate(le_abilities.classes_)}
    with open(os.path.join(models_dir, f"ability_mapping_hero_{target_hero_id}.json"), "w") as f:
        json.dump(ability_mapping, f, indent=4)
        
    print(f"[Способности] Уникальных способностей для предсказания: {num_classes_ab}")
    print("[Способности] Запуск обучения XGBoost...")
    
    start_time = time.time()
    model_abilities = xgb.XGBClassifier(
        objective='multi:softprob',
        num_class=num_classes_ab,
        tree_method='hist',
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        n_jobs=-1,
        random_state=42
    )
    model_abilities.fit(X_abilities, y_encoded_ab)
    
    ability_model_path = os.path.join(models_dir, f"xgb_abilities_hero_{target_hero_id}.json")
    model_abilities.save_model(ability_model_path)
    print(f"[Способности] Обучение завершено за {time.time() - start_time:.1f} сек! Модель сохранена.")

if __name__ == "__main__":
    train_models_for_hero(15)
