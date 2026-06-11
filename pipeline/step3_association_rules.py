"""
Шаг 3: Майнинг ассоциативных правил (FP-Growth)
=================================================
Находим синергии предметов внутри каждого кластера.
Наполняет поле synergy_rules в meta_rules.json.

Запуск: python pipeline/step3_association_rules.py
Требует: pip install mlxtend
"""

import json
from pathlib import Path

try:
    import pandas as pd
    from mlxtend.frequent_patterns import fpgrowth, association_rules
    from mlxtend.preprocessing import TransactionEncoder
    HAS_MLXTEND = True
except ImportError:
    HAS_MLXTEND = False

DATA_DIR = Path(__file__).parent / "data"
OUTPUT_DIR = Path(__file__).parent / "output"
STATIC_DIR = (
    Path(__file__).parent.parent / "randomizer" / "static" / "randomizer"
)

META_RULES_PATH = STATIC_DIR / "meta_rules.json"

MIN_SUPPORT = 0.05      # Предмет должен встречаться в ≥5% матчей кластера
MIN_CONFIDENCE = 0.25   # Правило срабатывает в ≥25% случаев
MIN_LIFT = 1.2          # Lift > 1.2 = реальная синергия


def compute_association_rules(transactions: list[list[str]]) -> list[dict]:
    """
    Запускаем FP-Growth и извлекаем ассоциативные правила.
    Returns: список правил [{antecedents, consequents, confidence, lift}, ...]
    """
    if not HAS_MLXTEND:
        print("  WARN: mlxtend не установлен. pip install mlxtend")
        return []

    if len(transactions) < 20:
        return []

    te = TransactionEncoder()
    te_array = te.fit(transactions).transform(transactions)
    df_te = pd.DataFrame(te_array, columns=te.columns_)

    frequent_sets = fpgrowth(df_te, min_support=MIN_SUPPORT, use_colnames=True)
    if frequent_sets.empty:
        return []

    rules = association_rules(
        frequent_sets, metric="lift", min_threshold=MIN_LIFT
    )
    rules = rules[rules["confidence"] >= MIN_CONFIDENCE]

    result = []
    for _, row in rules.iterrows():
        result.append({
            "antecedents": list(row["antecedents"]),
            "consequents": list(row["consequents"]),
            "support": round(float(row["support"]), 4),
            "confidence": round(float(row["confidence"]), 4),
            "lift": round(float(row["lift"]), 4),
        })

    result.sort(key=lambda x: x["lift"], reverse=True)
    print(f"  Найдено {len(result)} правил (lift ≥ {MIN_LIFT})")
    return result[:50]  # Берем топ-50 по lift


def process_hero_rules(hero_id: int, hero_data: dict) -> dict:
    """Наполняем synergy_rules для каждого архетипа героя."""
    clustered_path = OUTPUT_DIR / f"hero_{hero_id}_clustered.csv"

    if not clustered_path.exists():
        print(f"  SKIP hero {hero_id}: нет clustered.csv")
        return hero_data

    try:
        import pandas as pd
        df = pd.read_csv(clustered_path)
    except Exception as e:
        print(f"  SKIP hero {hero_id}: {e}")
        return hero_data

    for arch_id, arch_data in hero_data.items():
        print(f"  Архетип {arch_id} '{arch_data['name']}':")

        cluster_rows = df[df["cluster"] == int(arch_id)]

        transactions = []
        for seq_str in cluster_rows["_items_sequence"].dropna():
            try:
                seq = json.loads(seq_str)
                if seq:
                    transactions.append(seq)
            except Exception:
                pass

        rules = compute_association_rules(transactions)
        hero_data[arch_id]["synergy_rules"] = rules

    return hero_data


def main():
    print("=" * 60)
    print("ШАГ 3: МАЙНИНГ АССОЦИАТИВНЫХ ПРАВИЛ (FP-GROWTH)")
    print("=" * 60)

    if not META_RULES_PATH.exists():
        print(f"ОШИБКА: {META_RULES_PATH.name} не найден.")
        print("Сначала запусти step2_clustering.py")
        return

    with open(META_RULES_PATH, "r", encoding="utf-8") as f:
        meta_rules = json.load(f)

    print(f"Загружено {len(meta_rules)} героев из meta_rules.json")

    for hero_id_str, hero_data in meta_rules.items():
        print(f"\n{'─' * 40}")
        print(f"Герой {hero_id_str}:")
        meta_rules[hero_id_str] = process_hero_rules(int(hero_id_str), hero_data)

    with open(META_RULES_PATH, "w", encoding="utf-8") as f:
        json.dump(meta_rules, f, ensure_ascii=False)

    print(f"\n{'=' * 60}")
    print(f"✓ meta_rules.json обновлен с synergy_rules")


if __name__ == "__main__":
    main()
