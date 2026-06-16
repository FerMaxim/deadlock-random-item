import os
import pandas as pd

def clean_dataset():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    training_dir = os.path.join(base_dir, "training")
    
    input_file = os.path.join(training_dir, "high_mmr_split.parquet")
    output_file = os.path.join(training_dir, "ml_ready_dataset.parquet")
    
    print(f"Читаем файл: {input_file}...")
    df = pd.read_parquet(input_file)
    print(f"Исходное количество строк: {len(df)}")
    
    # 1. Удаляем строки, где net_worth <= 15000
    df_cleaned = df[df['net_worth'] > 15000]
    print(f"Строк после фильтрации net_worth > 15000: {len(df_cleaned)}")
    
    # 2. Удаляем ненужные столбцы
    cols_to_drop = ['start_time', 'net_worth', 'items.game_time_s', 'stats.level', 'average_badge']
    
    # Удаляем только те, что реально есть в таблице
    existing_cols_to_drop = [c for c in cols_to_drop if c in df_cleaned.columns]
    df_cleaned = df_cleaned.drop(columns=existing_cols_to_drop)
    
    print(f"Удалены столбцы: {existing_cols_to_drop}")
    print(f"Оставшиеся столбцы: {list(df_cleaned.columns)}")
    
    # 3. Сохраняем в новый файл
    print(f"Сохраняем в {output_file}...")
    df_cleaned.to_parquet(output_file, engine='pyarrow')
    print("Готово!")

if __name__ == "__main__":
    clean_dataset()
