import os
import duckdb
from datetime import datetime

def filter_high_mmr(input_path: str, output_path: str):
    """
    Оставляет только матчи с рангом Phantom 1 (91) и выше.
    """
    if not os.path.exists(input_path):
        print(f"Ошибка: Файл {input_path} не найден.")
        return False
        
    con = duckdb.connect(':memory:')
    
    try:
        print(f"Фильтрация High MMR (Phantom 1+) в файле: {os.path.basename(input_path)}...")
        
        # Получаем количество до
        before_query = f"SELECT COUNT(DISTINCT match_id) FROM read_parquet('{input_path}')"
        matches_before = con.execute(before_query).fetchone()[0]
        
        # Оставляем только average_badge >= 91
        con.execute(f"""
            CREATE TABLE high_mmr_data AS 
            SELECT * FROM read_parquet('{input_path}')
            WHERE average_badge >= 91
        """)
        
        # Получаем количество после
        matches_after = con.execute("SELECT COUNT(DISTINCT match_id) FROM high_mmr_data").fetchone()[0]
        
        if matches_after == 0:
            print("Внимание: После фильтрации не осталось ни одного матча!")
            return False
            
        # Сохраняем результат
        con.execute(f"COPY high_mmr_data TO '{output_path}' (FORMAT PARQUET)")
        
        print(f"\n--- Результаты фильтрации ---")
        print(f"Матчей до:    {matches_before:,}".replace(',', ' '))
        print(f"Матчей после: {matches_after:,}".replace(',', ' '))
        print(f"Удалено:      {matches_before - matches_after:,}".replace(',', ' '))
        print(f"Сохранено в:  {output_path}")
        return True
        
    except Exception as e:
        print(f"Ошибка при обработке файла: {e}")
        return False
    finally:
        con.close()

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    temp_dir = os.path.join(base_dir, "training", "temp")
    training_dir = os.path.join(base_dir, "training")
    
    if not os.path.exists(temp_dir):
        print(f"Папка {temp_dir} не найдена.")
        exit()

    # Ищем файлы, которые начинаются на badged_
    parquet_files = [f for f in os.listdir(temp_dir) if f.startswith("badged_") and f.endswith(".parquet")]
    
    if not parquet_files:
        print(f"В папке {temp_dir} не найдено badged_ файлов.")
        exit()

    print("\nДоступные файлы для фильтрации (High MMR):")
    for i, file_name in enumerate(parquet_files, 1):
        print(f"[{i}] {file_name}")
        
    try:
        choice = input("\nВведите номер файла (или 0 для отмены): ")
        if not choice.strip().isdigit():
            print("Ошибка: Введите число.")
            exit()
            
        choice = int(choice)
        
        if choice == 0:
            exit()
            
        if 1 <= choice <= len(parquet_files):
            file_name = parquet_files[choice - 1]
            input_file = os.path.join(temp_dir, file_name)
            
            # Формируем имя для нового файла
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_name = f"high_mmr_dataset_{timestamp}.parquet"
            output_file = os.path.join(training_dir, output_name)
            
            filter_high_mmr(input_file, output_file)
        else:
            print("Ошибка: Неверный номер.")
            
    except KeyboardInterrupt:
        print("\nОтменено пользователем.")
