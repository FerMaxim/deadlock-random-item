import os
import pandas as pd
import numpy as np

def prepare_ability_dataset(target_hero_id=15, max_seq_length=16):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    training_dir = os.path.join(base_dir, "training")
    input_file = os.path.join(training_dir, "ml_labeled_dataset.parquet")
    output_x = os.path.join(training_dir, f"xgb_abilities_X_hero_{target_hero_id}.csv")
    output_y = os.path.join(training_dir, f"xgb_abilities_Y_hero_{target_hero_id}.csv")
    
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
        ability_build = row['ability_build']
        
        # Если билд пустой, пропускаем
        if len(ability_build) < 2:
            continue
            
        # Формируем окно (для способностей максимум 16 шагов)
        current_seq = []
        # Мы можем обрезать или ограничиться 16 шагами (иногда бывает больше из-за багов или отмены)
        build_len = min(len(ability_build), max_seq_length)
        
        for i in range(build_len):
            target_ability = ability_build[i]
            
            # Для XGBoost создаем вектор фиксированной длины
            feature_vector = current_seq.copy()
            # Дополняем нулями
            while len(feature_vector) < max_seq_length:
                feature_vector.append(0)
                
            feature_vector = feature_vector[:max_seq_length]
            
            # Добавляем фичу архетипа как первую колонку
            feature_vector.insert(0, archetype)
            
            X_data.append(feature_vector)
            Y_data.append(target_ability)
            
            # Обновляем инвентарь для следующего шага
            current_seq.append(target_ability)

    print(f"Сгенерировано {len(X_data)} примеров (X, Y).")
    
    # Создаем DataFrame
    cols = ['archetype'] + [f'ability_step_{i+1}' for i in range(max_seq_length)]
    
    X_df = pd.DataFrame(X_data, columns=cols)
    Y_df = pd.DataFrame(Y_data, columns=['target_ability'])
    
    print(f"Сохранение фичей в {output_x}...")
    X_df.to_csv(output_x, index=False)
    
    print(f"Сохранение таргетов в {output_y}...")
    Y_df.to_csv(output_y, index=False)
    
    print("Подготовка датасета способностей успешно завершена!")

if __name__ == "__main__":
    # 15 - Это Bebop
    prepare_ability_dataset(target_hero_id=15)
