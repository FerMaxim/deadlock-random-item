import os
import duckdb

# Официальные названия рангов из Deadlock API
TIER_NAMES = {
    0: "Obscurus",
    1: "Initiate",
    2: "Seeker",
    3: "Alchemist",
    4: "Arcanist",
    5: "Ritualist",
    6: "Emissary",
    7: "Archon",
    8: "Oracle",
    9: "Phantom",
    10: "Ascendant",
    11: "Eternus"
}

def show_badge_statistics(file_path: str):
    """
    Считает статистику по рангам (average_badge) в файле и выводит красивую таблицу.
    """
    if not os.path.exists(file_path):
        print(f"Ошибка: Файл не найден: {file_path}")
        return

    con = duckdb.connect(':memory:')
    try:
        # Проверяем структуру файла
        columns = [col[0] for col in con.execute(f"DESCRIBE SELECT * FROM '{file_path}'").fetchall()]
        if "average_badge" not in columns:
            print("Ошибка: В файле нет столбца 'average_badge'. Убедитесь, что это badged_ файл.")
            return

        # Получаем общее количество уникальных матчей
        total_query = f"SELECT COUNT(DISTINCT match_id) FROM '{file_path}' WHERE average_badge IS NOT NULL"
        total_matches = con.execute(total_query).fetchone()[0]
        
        if total_matches == 0:
            print("В файле нет данных о рангах.")
            return
            
        # Группируем по тирам
        # Тир вычисляется делением ранга на 10 (например, ранг 116 -> тир 11)
        stats_query = f"""
            SELECT 
                CAST(FLOOR(average_badge / 10.0) AS INT) as tier,
                COUNT(DISTINCT match_id) as count
            FROM '{file_path}'
            WHERE average_badge IS NOT NULL
            GROUP BY CAST(FLOOR(average_badge / 10.0) AS INT)
            ORDER BY tier ASC
        """
        
        results = con.execute(stats_query).fetchall()
        
        # Форматированный вывод
        print(f"\n--- Статистика рангов: {os.path.basename(file_path)} ---")
        print("-" * 65)
        print(f"{'TIER':<5} | {'Название ранга':<15} | {'% (от матчей)':<15} | {'Кол-во матчей':<15}")
        print("-" * 65)
        
        for tier, count in results:
            tier_name = TIER_NAMES.get(tier, f"Unknown ({tier})")
            percentage = (count / total_matches) * 100
            print(f"{tier:<5} | {tier_name:<15} | {percentage:>6.2f}%{' ' * 8} | {count:<15}")
            
        print("-" * 65)
        print(f"{'Всего уникальных матчей:':<30} {total_matches:,}".replace(',', ' '))
        print("-" * 65)
        
    except Exception as e:
        print(f"Ошибка при сборе статистики: {e}")
    finally:
        con.close()

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    training_dir = os.path.join(base_dir, "training")
    temp_dir = os.path.join(training_dir, "temp")
    
    parquet_files = []
    
    # Ищем файлы в temp
    if os.path.exists(temp_dir):
        for f in os.listdir(temp_dir):
            if f.startswith("badged_") and f.endswith(".parquet"):
                parquet_files.append(os.path.join(temp_dir, f))
                
    # Ищем файлы в training (готовые датасеты)
    if os.path.exists(training_dir):
        for f in os.listdir(training_dir):
            if f.endswith(".parquet"):
                parquet_files.append(os.path.join(training_dir, f))
    
    if not parquet_files:
        print(f"Не найдено подходящих .parquet файлов в {training_dir} или {temp_dir}.")
        exit()

    print("\nДоступные файлы для статистики:")
    for i, file_path in enumerate(parquet_files, 1):
        # Показываем путь относительно папки main
        rel_path = os.path.relpath(file_path, base_dir)
        print(f"[{i}] {rel_path}")
        
    try:
        choice = input("\nВведите номер файла для просмотра статистики: ")
        if not choice.strip().isdigit():
            print("Ошибка: Введите число.")
            exit()
            
        choice = int(choice)
        
        if 1 <= choice <= len(parquet_files):
            selected_file = parquet_files[choice - 1]
            show_badge_statistics(selected_file)
        else:
            print("Ошибка: Неверный номер.")
            
    except KeyboardInterrupt:
        print("\nОтменено пользователем.")
