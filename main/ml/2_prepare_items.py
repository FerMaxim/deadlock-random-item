import os
import pandas as pd
import numpy as np

def prepare_item_dataset(target_hero_id=15, max_seq_length=24):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    training_dir = os.path.join(base_dir, "training")
    input_file = os.path.join(training_dir, "ml_labeled_dataset.parquet")
    output_x = os.path.join(training_dir, f"xgb_items_X_hero_{target_hero_id}.csv")
    output_y = os.path.join(training_dir, f"xgb_items_Y_hero_{target_hero_id}.csv")
    
    print(f"Чтение датасета: {input_file}...")
    df = pd.read_parquet(input_file)
    
    # Оставляем только нужного героя
    df_hero = df[df['hero_id'] == target_hero_id]
    print(f"Найдено {len(df_hero)} матчей для героя {target_hero_id}")
    
    X_data = []
    Y_data = []
    
    print("Формирование последовательностей (Sliding Window)...")
    for _, row in df_hero.iterrows():
        archetype = row['archetype']
        item_build = row['item_build']
        
        # Если билд пустой, пропускаем
        if len(item_build) < 2:
            continue
            
        # Формируем окно
        current_seq = []
        for i in range(len(item_build)):
            target_item = item_build[i]
            
            # Для XGBoost нам нужно фиксированное количество фичей. 
            # Создаем вектор фиксированной длины max_seq_length (остальное нули)
            feature_vector = current_seq.copy()
            # Дополняем нулями до нужной длины
            while len(feature_vector) < max_seq_length:
                feature_vector.append(0)
            
            # Обрезаем, если секвенция слишком длинная (хотя обычно 24 хватает)
            feature_vector = feature_vector[:max_seq_length]
            
            # Добавляем фичу архетипа как первую колонку
            feature_vector.insert(0, archetype)
            
            X_data.append(feature_vector)
            Y_data.append(target_item)
            
            # Обновляем инвентарь для следующего шага
            current_seq.append(target_item)

    print(f"Сгенерировано {len(X_data)} примеров (X, Y).")
    
    # Создаем DataFrame для удобства и сохранения
    # Колонки: archetype, step_1, step_2, ..., step_24
    cols = ['archetype'] + [f'item_step_{i+1}' for i in range(max_seq_length)]
    
    X_df = pd.DataFrame(X_data, columns=cols)
    Y_df = pd.DataFrame(Y_data, columns=['target_item'])
    
    print(f"Сохранение фичей в {output_x}...")
    X_df.to_csv(output_x, index=False)
    
    print(f"Сохранение таргетов в {output_y}...")
    Y_df.to_csv(output_y, index=False)
    
    print("Подготовка датасета предметов успешно завершена!")

if __name__ == "__main__":
    # 15 - Это Bebop (исходя из словаря heroes_dict.json)
    prepare_item_dataset(target_hero_id=15)
