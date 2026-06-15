import duckdb
import os

def analyze_and_read_parquet(file_path: str, n_rows: int = 10, export_txt: bool = False):
    """
    Анализирует parquet файл с использованием DuckDB:
    - Выводит общее количество строк.
    - Выводит количество уникальных значений в первом столбце.
    - Выводит N первых строк без обрезания (полностью).
    
    Скрипт не привязан к конкретному файлу и может работать с любым parquet файлом.
    
    :param file_path: Путь к файлу parquet
    :param n_rows: Количество строк для считывания и вывода
    :param export_txt: Если True, сохраняет результат в txt файл без сокращений
    :return: Словарь с результатами (total_rows, unique_first_col, data)
    """
    if not os.path.exists(file_path):
        print(f"Ошибка: Файл не найден по пути {file_path}")
        return None

    # Инициализируем подключение duckdb (в памяти)
    con = duckdb.connect(database=':memory:')

    try:
        # Получаем структуру файла для определения первого столбца
        columns_query = f"DESCRIBE SELECT * FROM '{file_path}'"
        columns_info = con.execute(columns_query).fetchall()
        
        if not columns_info:
            print("Ошибка: Не удалось получить структуру файла.")
            return None
            
        first_column_name = columns_info[0][0]

        # 1. Считаем общее количество строк (DuckDB оптимизирует это для parquet)
        total_rows_query = f"SELECT COUNT(*) FROM '{file_path}'"
        total_rows = con.execute(total_rows_query).fetchone()[0]

        # 2. Считаем количество уникальных строк первого столбца
        unique_first_col_query = f"SELECT COUNT(DISTINCT {first_column_name}) FROM '{file_path}'"
        unique_first_col = con.execute(unique_first_col_query).fetchone()[0]

        # 3. Читаем N строк
        read_n_rows_query = f"SELECT * FROM '{file_path}' LIMIT {n_rows}"
        
        # Пытаемся вывести данные как DataFrame для красивого форматирования, если есть pandas
        try:
            import pandas as pd
            # Отключаем обрезку столбцов и строк в pandas для полного вывода
            pd.set_option('display.max_columns', None)
            pd.set_option('display.max_rows', None)
            pd.set_option('display.width', 2000)
            pd.set_option('display.max_colwidth', None)
            
            data_result = con.execute(read_n_rows_query).df()
            
            # Формируем строку вывода
            output_str = f"--- Анализ файла: {os.path.basename(file_path)} ---\n"
            output_str += f"Общее количество строк: {total_rows}\n"
            output_str += f"Уникальных значений в первом столбце ('{first_column_name}'): {unique_first_col}\n"
            output_str += f"Первые {n_rows} строк (Полный вывод):\n"
            output_str += data_result.to_string()
            
            # Сохранение в файл
            if export_txt:
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                temp_dir = os.path.join(base_dir, "training", "temp")
                if not os.path.exists(temp_dir):
                    os.makedirs(temp_dir)
                
                txt_filename = os.path.basename(file_path).replace('.parquet', f'_head{n_rows}.txt')
                txt_filepath = os.path.join(temp_dir, txt_filename)
                
                with open(txt_filepath, 'w', encoding='utf-8') as f:
                    f.write(output_str)
                print(f"\n[Успешно] Полный форматированный вывод сохранен в файл: {txt_filepath}")
                
        except ImportError:
            # Фолбэк, если pandas не установлен
            print(f"--- Анализ файла: {os.path.basename(file_path)} ---")
            print(f"Общее количество строк: {total_rows}")
            print(f"Уникальных значений: {unique_first_col}")
            print(f"Первые {n_rows} строк:")
            data_result = con.execute(read_n_rows_query).fetchall()
            for row in data_result:
                print(row)
        
        return {
            "total_rows": total_rows,
            "unique_first_column": unique_first_col,
            "data": data_result
        }

    except Exception as e:
        print(f"Произошла ошибка при обработке файла DuckDB: {e}")
        return None
    finally:
        con.close()

if __name__ == "__main__":
    # Интерактивный режим при запуске скрипта напрямую
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    directories_to_scan = [
        os.path.join(base_dir, "data"),
        os.path.join(base_dir, "training")
    ]
    
    parquet_files = []
    
    for directory in directories_to_scan:
        if os.path.exists(directory):
            for root, _, files in os.walk(directory):
                for f in files:
                    if f.endswith(".parquet"):
                        full_path = os.path.join(root, f)
                        # Сохраняем относительный путь для красивого вывода и полный для работы
                        display_path = os.path.relpath(full_path, base_dir)
                        parquet_files.append((display_path, full_path))
    
    if not parquet_files:
        print("Не найдено файлов формата .parquet в папках data и training.")
        exit()

    print("\nДоступные Parquet-файлы для анализа:")
    for i, (display_path, _) in enumerate(parquet_files, 1):
        print(f"[{i}] {display_path}")
        
    try:
        choice = int(input("\nВведите номер файла (1, 2, 3...): "))
        if 1 <= choice <= len(parquet_files):
            selected_file = parquet_files[choice - 1][1]
            
            n_rows_input = input("Сколько строк вывести? (нажмите Enter для 5 по умолчанию): ")
            n_rows = int(n_rows_input) if n_rows_input.strip().isdigit() else 5
            
            save_input = input("Сохранить полный вывод в .txt файл? (y/n): ")
            export_txt = save_input.strip().lower() == 'y'
            
            analyze_and_read_parquet(selected_file, n_rows=n_rows, export_txt=export_txt)
        else:
            print("Ошибка: Выбран неверный номер.")
    except ValueError:
        print("Ошибка: Пожалуйста, введите число.")
    except KeyboardInterrupt:
        print("\nОтменено пользователем.")
