import duckdb
import os
import time

def convert_parquet_to_csv(parquet_path, csv_path):
    if not os.path.exists(parquet_path):
        print(f"Ошибка: Файл {parquet_path} не найден.")
        return

    print(f"Начинаю конвертацию {parquet_path} в {csv_path} с помощью DuckDB...")
    start_time = time.time()
    
    # Запрос для конвертации с использованием DuckDB
    query = f"COPY (SELECT * FROM '{parquet_path}') TO '{csv_path}' (HEADER, DELIMITER ',')"
    duckdb.query(query)
    
    end_time = time.time()
    print(f"Успешно! Конвертация заняла {end_time - start_time:.2f} секунд.")

if __name__ == "__main__":
    raw_parquet = "data/raw/match_player_86.parquet"
    output_csv = "data/processed/match_player_86.csv"
    # raw_parquet = "data/raw/match_player_86.parquet"
    # output_csv = "data/processed/match_player_86.csv"
    
    # Создаем папку, если вдруг ее нет
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    
    convert_parquet_to_csv(raw_parquet, output_csv)
