import os
import duckdb

def clean_parquet_file(input_path: str, output_path: str):
    """
    Создает новый Parquet-файл, оставляя только нужные столбцы:
    - Основные данные матча и игроков
    - Данные о предметах
    - Данные об уровнях (stats.level)
    """
    # Список необходимых столбцов (с двойными кавычками для столбцов с точкой в названии)
    columns_to_keep = [
        "match_id",
        "start_time",
        "average_badge_team0",
        "average_badge_team1",
        "hero_id",
        "net_worth",
        '"items.game_time_s"',
        '"items.item_id"',
        '"items.upgrade_id"',
        '"items.sold_time_s"',
        '"items.flags"',
        '"items.upgrade_info"',
        '"stats.level"'
    ]
    
    # Собираем столбцы в строку для SQL запроса
    select_cols = ",\n                ".join(columns_to_keep)
    
    # Подключение к DuckDB (в памяти)
    con = duckdb.connect(':memory:')
    
    try:
        print(f"Очистка файла: {os.path.basename(input_path)}...")
        
        # SQL запрос использует встроенный механизм COPY DuckDB 
        # для быстрой фильтрации и сохранения прямо в Parquet
        query = f"""
        COPY (
            SELECT 
                {select_cols}
            FROM '{input_path}'
        ) TO '{output_path}' (FORMAT PARQUET);
        """
        
        con.execute(query)
        print(f"--> Успешно сохранено в: {output_path}")
        
    except Exception as e:
        print(f"--> Ошибка при обработке {os.path.basename(input_path)}: {e}")
    finally:
        con.close()

if __name__ == "__main__":
    # Настраиваем пути
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    temp_dir = os.path.join(base_dir, "training", "temp")
    
    if not os.path.exists(data_dir):
        print(f"Папка с данными не найдена: {data_dir}")
        exit()
        
    # Создаем папку temp, если она не существует
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    # Ищем .parquet файлы
    parquet_files = [f for f in os.listdir(data_dir) if f.endswith(".parquet")]
    
    if not parquet_files:
        print(f"В папке {data_dir} не найдено .parquet файлов")
        exit()

    # Интерактивное меню
    print("\nДоступные Parquet-файлы для очистки (сокращения столбцов):")
    print("[0] Выбрать ВСЕ файлы")
    for i, file_name in enumerate(parquet_files, 1):
        print(f"[{i}] {file_name}")
        
    try:
        choice = input("\nВведите номер файла (0 для всех, 1, 2...): ")
        if not choice.strip().isdigit():
            print("Ошибка: Введите число.")
            exit()
            
        choice = int(choice)
        
        # Определяем, какие файлы обрабатывать
        files_to_process = []
        if choice == 0:
            files_to_process = parquet_files
        elif 1 <= choice <= len(parquet_files):
            files_to_process = [parquet_files[choice - 1]]
        else:
            print("Ошибка: Неверный номер.")
            exit()
            
        print("\nНачинаем обработку...")
        
        # Обрабатываем выбранные файлы
        for file_name in files_to_process:
            input_file = os.path.join(data_dir, file_name)
            # Добавляем префикс clean_rows_ к названию нового файла
            output_file = os.path.join(temp_dir, f"clean_rows_{file_name}")
            
            clean_parquet_file(input_file, output_file)
            
        print("\nВсе выбранные файлы обработаны! Ищите их в папке training/temp")
        
    except KeyboardInterrupt:
        print("\nОтменено пользователем.")
