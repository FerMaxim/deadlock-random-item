import os
import duckdb

def transform_badge(input_path: str, output_path: str):
    """
    Преобразует столбцы average_badge_team0 и average_badge_team1 
    в единый столбец average_badge, усредняя их и округляя в большую сторону.
    (Например, тир 11 подранг 6 = 116. Среднее с 114 = 115).
    """
    if not os.path.exists(input_path):
        print(f"Ошибка: Файл {input_path} не найден.")
        return False
        
    con = duckdb.connect(':memory:')
    
    try:
        print(f"Преобразование рангов в файле: {os.path.basename(input_path)}...")
        
        # Создаем временную таблицу из parquet
        con.execute(f"CREATE TABLE temp_data AS SELECT * FROM read_parquet('{input_path}')")
        
        # Проверяем, есть ли нужные столбцы
        columns_info = con.execute("DESCRIBE temp_data").fetchall()
        col_names = [col[0] for col in columns_info]
        
        if "average_badge_team0" not in col_names or "average_badge_team1" not in col_names:
            print("Ошибка: В файле нет нужных столбцов (average_badge_team0, average_badge_team1).")
            return False
            
        # Добавляем новый столбец и вычисляем значение с округлением вверх (CEIL)
        con.execute("""
            ALTER TABLE temp_data ADD COLUMN average_badge INT;
            UPDATE temp_data SET average_badge = CEIL((average_badge_team0 + average_badge_team1) / 2.0)::INT;
        """)
        
        # Удаляем старые столбцы
        con.execute("""
            ALTER TABLE temp_data DROP COLUMN average_badge_team0;
            ALTER TABLE temp_data DROP COLUMN average_badge_team1;
        """)
        
        # Сохраняем в новый Parquet файл
        con.execute(f"COPY temp_data TO '{output_path}' (FORMAT PARQUET)")
        print(f"--> Успешно сохранено с новым столбцом average_badge в: {output_path}")
        return True
        
    except Exception as e:
        print(f"Ошибка при обработке файла: {e}")
        return False
    finally:
        con.close()

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    temp_dir = os.path.join(base_dir, "training", "temp")
    
    if not os.path.exists(temp_dir):
        print(f"Папка {temp_dir} не найдена. Сначала создайте clean_rows файлы.")
        exit()

    # Ищем файлы, которые начинаются на clean_rows или merged
    parquet_files = [f for f in os.listdir(temp_dir) if f.endswith(".parquet")]
    
    if not parquet_files:
        print(f"В папке {temp_dir} не найдено .parquet файлов для обработки.")
        exit()

    print("\nДоступные Parquet-файлы для преобразования рангов:")
    print("[0] Выбрать ВСЕ файлы")
    for i, file_name in enumerate(parquet_files, 1):
        print(f"[{i}] {file_name}")
        
    try:
        choice = input("\nВведите номер файла (0 для всех, 1, 2...): ")
        if not choice.strip().isdigit():
            print("Ошибка: Введите число.")
            exit()
            
        choice = int(choice)
        
        files_to_process = []
        if choice == 0:
            files_to_process = parquet_files
        elif 1 <= choice <= len(parquet_files):
            files_to_process = [parquet_files[choice - 1]]
        else:
            print("Ошибка: Неверный номер.")
            exit()
            
        print("\nНачинаем преобразование...")
        
        for file_name in files_to_process:
            input_file = os.path.join(temp_dir, file_name)
            # Добавляем префикс badged_ чтобы не перезаписывать оригинал
            output_file = os.path.join(temp_dir, f"badged_{file_name}")
            transform_badge(input_file, output_file)
            
        print("\nВсе выбранные файлы обработаны!")
        
    except KeyboardInterrupt:
        print("\nОтменено пользователем.")
