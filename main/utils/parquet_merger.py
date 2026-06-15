import os
import duckdb
from datetime import datetime

def merge_parquet_files(input_files: list, output_path: str):
    """
    Объединяет несколько Parquet файлов в один с помощью DuckDB.
    Файлы должны иметь одинаковую структуру столбцов.
    """
    if not input_files:
        print("Ошибка: Нет файлов для объединения.")
        return False
        
    con = duckdb.connect(':memory:')
    
    try:
        print(f"\nНачинаем объединение {len(input_files)} файлов...")
        for f in input_files:
            print(f" - {os.path.basename(f)}")
            
        # Формируем список путей в формате SQL массива ['path1', 'path2']
        files_list_str = ", ".join([f"'{path}'" for path in input_files])
        
        # Запрос: читаем все файлы сразу и сохраняем в новый Parquet файл
        query = f"""
        COPY (
            SELECT * FROM read_parquet([{files_list_str}])
        ) TO '{output_path}' (FORMAT PARQUET);
        """
        
        con.execute(query)
        print(f"\n[Успешно] Файлы объединены! Результат сохранен в:\n{output_path}")
        return True
        
    except Exception as e:
        print(f"\n[Ошибка] Не удалось объединить файлы. Возможно, у них разная структура столбцов.")
        print(f"Текст ошибки: {e}")
        return False
    finally:
        con.close()


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    temp_dir = os.path.join(base_dir, "training", "temp")
    
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
        
    directories_to_scan = [
        os.path.join(base_dir, "data"),
        os.path.join(base_dir, "training")
    ]
    
    parquet_files = []
    
    # Ищем файлы рекурсивно
    for directory in directories_to_scan:
        if os.path.exists(directory):
            for root, _, files in os.walk(directory):
                for f in files:
                    if f.endswith(".parquet"):
                        full_path = os.path.join(root, f)
                        display_path = os.path.relpath(full_path, base_dir)
                        parquet_files.append((display_path, full_path))
    
    if len(parquet_files) < 2:
        print("Найдено менее 2-х файлов .parquet. Нечего объединять.")
        exit()

    print("\nДоступные Parquet-файлы для объединения:")
    print("[0] Выбрать ВСЕ найденные файлы")
    for i, (display_path, _) in enumerate(parquet_files, 1):
        print(f"[{i}] {display_path}")
        
    try:
        choice_str = input("\nВведите номера файлов через запятую (например, 1, 3, 4) или 0 для всех: ")
        
        files_to_merge = []
        
        if choice_str.strip() == "0":
            # Берем все пути (индекс 1 в кортеже)
            files_to_merge = [f[1] for f in parquet_files]
        else:
            # Парсим числа через запятую
            choices = [int(x.strip()) for x in choice_str.split(",") if x.strip().isdigit()]
            
            for c in set(choices): # Используем set для удаления дубликатов
                if 1 <= c <= len(parquet_files):
                    files_to_merge.append(parquet_files[c - 1][1])
                else:
                    print(f"Предупреждение: Файла с номером {c} не существует, пропускаем.")
                    
        if len(files_to_merge) < 2:
            print("\nОшибка: Для объединения нужно выбрать как минимум 2 файла!")
            exit()
            
        # Генерируем имя выходного файла
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"merged_{len(files_to_merge)}_files_{timestamp}.parquet"
        output_filepath = os.path.join(temp_dir, output_filename)
        
        merge_parquet_files(files_to_merge, output_filepath)
        
    except ValueError:
        print("Ошибка: Пожалуйста, вводите только числа через запятую.")
    except KeyboardInterrupt:
        print("\nОтменено пользователем.")
