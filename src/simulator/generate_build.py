import json
import random

def generate_build(playstyle=None):
    with open("data/processed/meta_rules.json", "r", encoding="utf-8") as f:
        meta_rules = json.load(f)
        
    archetypes = list(meta_rules["archetypes"].keys())
    
    if not playstyle or playstyle not in archetypes:
        playstyle = random.choice(archetypes)
        
    print(f"=== ГЕНЕРАЦИЯ БИЛДА ===")
    print(f"Герой: Bebop (ID: 15)")
    print(f"Стиль игры (Архетип): {playstyle}")
    print("=======================\n")
    
    build = meta_rules["archetypes"][playstyle]
    
    print("[1] ПОРЯДОК ЗАКУПА ПРЕДМЕТОВ (Хронология):")
    for idx, item in enumerate(build["purchase_order"], 1):
        status_text = ""
        if item.get("status_tag") == "апгрейд":
            status_text = " [Уходит в апгрейд]"
        elif item.get("status_tag") == "продажа":
            status_text = " [Продается]"
            
        time_str = f"{item['time_min']} мин."
        cat_icon = "[Weapon]  " if item['category'] == 'weapon' else "[Vitality]" if item['category'] == 'vitality' else "[Spirit]  "
        print(f" {idx:2d}. {cat_icon} {item['name']:<25} (Среднее время покупки: {time_str}){status_text}")
        
    print("\n[2] ПОРЯДОК ПРОКАЧКИ СПОСОБНОСТЕЙ:")
    seq = build["ability_sequence"]
    if seq:
        for idx, skill in enumerate(seq, 1):
            print(f" Очко {idx:2d}: {skill}")
    else:
        print("API не вернул данные для этого архетипа.")

if __name__ == "__main__":
    generate_build("Gun/Weapon Bebop")
    print("\n" + "="*50 + "\n")
    generate_build("Spirit/Bomb Bebop")
