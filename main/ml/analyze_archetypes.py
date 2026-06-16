import os
import pandas as pd
import json
from collections import Counter

def analyze_hero_archetypes(target_hero_id=None):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    training_dir = os.path.join(base_dir, "training")
    dict_dir = os.path.join(base_dir, "data", "dictionary")
    input_file = os.path.join(training_dir, "ml_labeled_dataset.parquet")
    output_txt = os.path.join(training_dir, "temp", "all_archetypes_report.txt")
    
    # 1. Загружаем словари
    with open(os.path.join(dict_dir, "heroes_dict.json"), "r", encoding="utf-8") as f:
        heroes = json.load(f)
        id_to_hero = {str(v): k for k, v in heroes.items()}
        
    with open(os.path.join(dict_dir, "shop_items_dict.json"), "r", encoding="utf-8") as f:
        shop_items = json.load(f)
        
    # 2. Загружаем размеченный датасет
    print("Загрузка датасета...")
    df = pd.read_parquet(input_file)
    
    # Если передан ID, делаем только для одного. Иначе для всех.
    if target_hero_id is not None:
        hero_ids_to_process = [target_hero_id]
    else:
        hero_ids_to_process = sorted(df['hero_id'].unique())
        
    report_lines = []

    for h_id in hero_ids_to_process:
        df_hero = df[df['hero_id'] == h_id]
        if df_hero.empty:
            continue
            
        hero_name = id_to_hero.get(str(h_id), f"Hero_{h_id}")
        archetypes = sorted(df_hero['archetype'].unique())
        
        header = f"\n{'='*80}\nАнализ героя: {hero_name} (ID: {h_id}) | Всего матчей: {len(df_hero)} | Архетипов: {len(archetypes)}\n{'='*80}"
        print(header)
        report_lines.append(header)
        
        for arch in archetypes:
            arch_data = df_hero[df_hero['archetype'] == arch]
            match_count = len(arch_data)
            if match_count == 0:
                continue
                
            # Собираем все предметы из всех билдов этого архетипа
            item_counts = Counter()
            for build in arch_data['item_build']:
                # Убираем дубликаты внутри одного билда
                unique_items = set(build)
                item_counts.update(unique_items)
                
            top_items = []
            
            # Для авто-нейминга архетипа считаем "очки" слотов
            slot_scores = {"weapon": 0, "vitality": 0, "spirit": 0}
            
            for item_id, count in item_counts.most_common():
                item_info = shop_items.get(str(item_id), {})
                name = item_info.get("name", str(item_id))
                cost = item_info.get("cost", 0)
                slot_type = item_info.get("slot_type", "unknown")
                
                # Фокусируемся на предметах от 3200 и выше
                if cost >= 3200:
                    percent = (count / match_count) * 100
                    top_items.append(f" - [{slot_type.capitalize():^8}] {name} ({cost} душ) : {percent:.1f}%")
                    
                    if slot_type in slot_scores:
                        slot_scores[slot_type] += percent
                        
                    if len(top_items) >= 17:  # Берем топ-17 ключевых шмоток
                        break
            
            # Автоматически называем билд на основе доминирующей категории
            best_slot = max(slot_scores, key=slot_scores.get) if any(slot_scores.values()) else "Mixed"
            arch_name = f"{best_slot.capitalize()} Build"
            
            arch_header = f"=== Архетип {arch}: {arch_name} (Матчей: {match_count}, {match_count/len(df_hero)*100:.1f}%) ==="
            print(arch_header)
            report_lines.append(arch_header)
            
            items_str = '\n'.join(top_items)
            print(items_str + "\n")
            report_lines.append(items_str + "\n")

    # Сохраняем в файл, если обрабатывали всех
    if target_hero_id is None:
        os.makedirs(os.path.dirname(output_txt), exist_ok=True)
        with open(output_txt, "w", encoding="utf-8") as f:
            f.write("\n".join(report_lines))
        print(f"Полный отчет сохранен в: {output_txt}")

if __name__ == "__main__":
    # Вызываем без аргументов, чтобы проанализировать ВСЕХ героев
    analyze_hero_archetypes()
