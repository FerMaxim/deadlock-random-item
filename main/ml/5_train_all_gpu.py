import os
import pandas as pd
import numpy as np
import xgboost as xgb
import json
from sklearn.preprocessing import LabelEncoder
import time
import sys

import sys
import importlib.util

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

prepare_items_mod = load_module("prepare_items", os.path.join(os.path.dirname(__file__), "2_prepare_items.py"))
prepare_abilities_mod = load_module("prepare_abilities", os.path.join(os.path.dirname(__file__), "3_prepare_abilities.py"))

prepare_item_dataset = prepare_items_mod.prepare_item_dataset
prepare_ability_dataset = prepare_abilities_mod.prepare_ability_dataset

def train_hero_models(target_hero_id, use_gpu=True):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    training_dir = os.path.join(base_dir, "training")
    models_dir = os.path.join(base_dir, "ml", "models")
    os.makedirs(models_dir, exist_ok=True)
    
    print(f"\n{'='*60}")
    print(f"НАЧАЛО ОБУЧЕНИЯ ДЛЯ ГЕРОЯ ID: {target_hero_id}")
    print(f"{'='*60}")
    
    # Файлы
    items_x_path = os.path.join(training_dir, f"xgb_items_X_hero_{target_hero_id}.csv")
    items_y_path = os.path.join(training_dir, f"xgb_items_Y_hero_{target_hero_id}.csv")
    abilities_x_path = os.path.join(training_dir, f"xgb_abilities_X_hero_{target_hero_id}.csv")
    abilities_y_path = os.path.join(training_dir, f"xgb_abilities_Y_hero_{target_hero_id}.csv")
    
    # 1. Генерация матриц
    print("[1/5] Генерация обучающих матриц (Предметы и Способности)...")
    prepare_item_dataset(target_hero_id=target_hero_id)
    prepare_ability_dataset(target_hero_id=target_hero_id)
    
    # Настройки XGBoost
    device_target = 'cuda' if use_gpu else 'cpu'
    print(f"\n[2/5] Устройство для вычислений: {device_target.upper()}")
    
    # ---------------------------------------------------------
    # 2. Обучение предметов
    # ---------------------------------------------------------
    print("\n[3/5] Загрузка данных для ПРЕДМЕТОВ...")
    X_items = pd.read_csv(items_x_path)
    Y_items = pd.read_csv(items_y_path)
    
    if len(X_items) == 0:
        print(f"Нет данных для героя {target_hero_id}, пропускаем.")
        return
        
    le_items = LabelEncoder()
    y_encoded = le_items.fit_transform(Y_items['target_item'])
    num_classes_items = len(le_items.classes_)
    
    item_mapping = {int(class_idx): int(original_id) for class_idx, original_id in enumerate(le_items.classes_)}
    with open(os.path.join(models_dir, f"item_mapping_hero_{target_hero_id}.json"), "w") as f:
        json.dump(item_mapping, f, indent=4)
        
    print(f"[4/5] Обучение модели ПРЕДМЕТОВ (Классов: {num_classes_items}, Строк: {len(X_items)})...")
    start_time = time.time()
    try:
        model_items = xgb.XGBClassifier(
            objective='multi:softprob',
            num_class=num_classes_items,
            tree_method='hist',
            device=device_target, # Включаем GPU или CPU
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42
        )
        model_items.fit(X_items, y_encoded)
    except Exception as e:
        print(f"Ошибка при обучении на {device_target.upper()}: {e}")
        print("Попробуем переключиться на CPU...")
        model_items.set_params(device='cpu')
        model_items.fit(X_items, y_encoded)
        
    model_items.save_model(os.path.join(models_dir, f"xgb_items_hero_{target_hero_id}.json"))
    print(f"      Готово за {time.time() - start_time:.1f} сек!")
    
    # Очистка ОЗУ
    del X_items, Y_items, model_items
    
    # ---------------------------------------------------------
    # 3. Обучение способностей
    # ---------------------------------------------------------
    print("\n[5/5] Обучение модели СПОСОБНОСТЕЙ...")
    X_abilities = pd.read_csv(abilities_x_path)
    Y_abilities = pd.read_csv(abilities_y_path)
    
    le_abilities = LabelEncoder()
    y_encoded_ab = le_abilities.fit_transform(Y_abilities['target_ability'])
    num_classes_ab = len(le_abilities.classes_)
    
    ability_mapping = {int(class_idx): int(original_id) for class_idx, original_id in enumerate(le_abilities.classes_)}
    with open(os.path.join(models_dir, f"ability_mapping_hero_{target_hero_id}.json"), "w") as f:
        json.dump(ability_mapping, f, indent=4)
        
    start_time = time.time()
    try:
        model_abilities = xgb.XGBClassifier(
            objective='multi:softprob',
            num_class=num_classes_ab,
            tree_method='hist',
            device=device_target,
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42
        )
        model_abilities.fit(X_abilities, y_encoded_ab)
    except Exception as e:
        model_abilities.set_params(device='cpu')
        model_abilities.fit(X_abilities, y_encoded_ab)
        
    model_abilities.save_model(os.path.join(models_dir, f"xgb_abilities_hero_{target_hero_id}.json"))
    print(f"      Готово за {time.time() - start_time:.1f} сек!")
    
    del X_abilities, Y_abilities, model_abilities
    
    # ---------------------------------------------------------
    # 4. Удаление временных файлов (экономим 7 ГБ)
    # ---------------------------------------------------------
    print("\nОчистка временных CSV файлов...")
    for f_path in [items_x_path, items_y_path, abilities_x_path, abilities_y_path]:
        if os.path.exists(f_path):
            os.remove(f_path)
            
    print(f"=== ГЕРОЙ {target_hero_id} УСПЕШНО ОБУЧЕН И СОХРАНЕН ===")


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dict_dir = os.path.join(base_dir, "data", "dictionary")
    
    with open(os.path.join(dict_dir, "heroes_dict.json"), "r", encoding="utf-8") as f:
        heroes = json.load(f)
        
    all_hero_ids = sorted([int(h_id) for h_id in heroes.values()])
    
    print("Начинаем конвейер обучения для всех 38 героев...")
    # Для проверки, если есть видеокарта NVIDIA с CUDA, use_gpu=True даст огромный буст
    for h_id in all_hero_ids:
        # Пропускаем Bebop, если мы его уже обучили (раскомментируйте, если нужно пропустить)
        # if h_id == 15:
        #    continue
            
        try:
            train_hero_models(h_id, use_gpu=True)
        except Exception as e:
            print(f"!!! ОШИБКА ПРИ ОБУЧЕНИИ ГЕРОЯ {h_id}: {e}")

if __name__ == "__main__":
    main()
