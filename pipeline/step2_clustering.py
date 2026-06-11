"""
Шаг 2: Кластеризация — Определение Архетипов сборок
=====================================================
K-Means с оптимизацией количества кластеров через Silhouette Score.
Ключевой трюк: spike-флаги умножаются на 5 перед нормализацией,
чтобы доминировать в разделении кластеров.

Запуск: python pipeline/step2_clustering.py [hero_id]
"""

import json
import sys
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

DATA_DIR = Path(__file__).parent / "data"
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

HERO_IDS = [1, 2, 3, 4, 6, 7, 8, 10, 11, 12, 13, 14, 15, 17, 18, 25, 27, 31, 35, 50, 52]

# Признаки для кластеризации
# Порядок важен: сначала структурные, потом spike-флаги (они получат x5)
CLUSTER_FEATURES = [
    "ratio_weapon",    # Доля трат в Weapon (0.0–1.0)
    "ratio_vitality",  # Доля трат в Vitality (0.0–1.0)
    "ratio_spirit",    # Доля трат в Spirit (0.0–1.0)
    "spike_weapon",    # Флаг Weapon-спайка × 5 → доминирует при нормализации
    "spike_vitality",  # Флаг Vitality-спайка × 5
    "spike_spirit",    # Флаг Spirit-спайка × 5
    "skill_0_lvl",     # Уровень скилла S1
    "skill_1_lvl",     # Уровень скилла S2
    "skill_2_lvl",     # Уровень скилла S3
    "ult_lvl",         # Уровень ульты (коррелирует с Burst-архетипом)
    "early_ult",       # Ранняя прокачка ульты (бинарный)
]

SPIKE_COLS = ["spike_weapon", "spike_vitality", "spike_spirit"]
SPIKE_WEIGHT = 5.0  # Вес spike-флагов для доминирования в K-Means


def auto_name_archetype(cluster_df: pd.DataFrame) -> str:
    """
    Автоматически называем архетип по его характеристикам.
    Примеры: "Full Weapon", "Full Weapon + V-Dip", "Spirit Burst"
    """
    avg = {
        "Weapon": cluster_df["spent_weapon"].mean(),
        "Vitality": cluster_df["spent_vitality"].mean(),
        "Spirit": cluster_df["spent_spirit"].mean(),
    }
    spike_rates = {
        "Weapon": cluster_df["spike_weapon"].mean(),
        "Vitality": cluster_df["spike_vitality"].mean(),
        "Spirit": cluster_df["spike_spirit"].mean(),
    }

    # Находим основную ветку
    primary = max(avg, key=avg.get)
    dips = [
        cat for cat, rate in spike_rates.items()
        if rate > 0.5 and cat != primary
    ]

    name = f"Full {primary}"
    if dips:
        name += " + " + "/".join(f"{d[0]}-Dip" for d in dips)
    elif cluster_df["early_ult"].mean() > 0.5:
        name += " (Ult-First)"

    return name


def find_optimal_k(X_scaled: np.ndarray, k_range=range(2, 7)) -> int:
    """
    Подбираем оптимальное k через Silhouette Score.
    Silhouette > Elbow: показывает реальное качество разделения кластеров.
    """
    print("  Поиск оптимального k:")
    best_k, best_score = 2, -1

    for k in k_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(X_scaled)
        score = silhouette_score(X_scaled, labels)
        print(f"    k={k}: Silhouette={score:.4f}")
        if score > best_score:
            best_k, best_score = k, score

    print(f"  → Оптимальное k={best_k} (score={best_score:.4f})")
    return best_k


def cluster_hero(hero_id: int, force_k: int = None) -> dict | None:
    """
    Кластеризуем сборки одного героя.
    Returns: dict с архетипами или None если данных мало.
    """
    parquet_path = DATA_DIR / f"hero_{hero_id}_raw.csv"
    if not parquet_path.exists():
        print(f"  SKIP: Нет данных ({parquet_path.name}). Запусти step1_preprocess.py")
        return None

    df = pd.read_csv(parquet_path)
    print(f"  Загружено {len(df)} векторов")

    if len(df) < 30:
        print(f"  WARN: Слишком мало данных ({len(df)} < 30). Пропускаем.")
        return None

    # Готовим матрицу признаков
    available_features = [f for f in CLUSTER_FEATURES if f in df.columns]
    X = df[available_features].fillna(0).copy()

    # КЛЮЧЕВОЙ ТРЮК: spike-флаги × 5 перед нормализацией
    # Это гарантирует разделение "Full Gun" от "Gun + 4800 Vitality Dip"
    for col in SPIKE_COLS:
        if col in X.columns:
            X[col] = X[col] * SPIKE_WEIGHT

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Определяем k
    if force_k:
        best_k = force_k
    elif len(df) < 100:
        best_k = 2  # Мало данных → минимум кластеров
    else:
        best_k = find_optimal_k(X_scaled)

    # Финальная кластеризация
    km = KMeans(n_clusters=best_k, random_state=42, n_init=20, max_iter=500)
    df = df.copy()
    df["cluster"] = km.fit_predict(X_scaled)

    # Анализируем кластеры
    archetypes = {}
    for cid in range(best_k):
        cdf = df[df["cluster"] == cid]
        n = len(cdf)
        pct = n / len(df)

        name = auto_name_archetype(cdf)

        print(f"\n  ┌─ Cluster {cid}: '{name}' ({n} матчей, {pct:.1%})")
        print(f"  │  Avg: W={cdf['spent_weapon'].mean():.0f}  "
              f"V={cdf['spent_vitality'].mean():.0f}  "
              f"S={cdf['spent_spirit'].mean():.0f}")
        print(f"  │  Spike: W={cdf['spike_weapon'].mean():.1%}  "
              f"V={cdf['spike_vitality'].mean():.1%}  "
              f"S={cdf['spike_spirit'].mean():.1%}")
        print(f"  └─ Ult-first: {cdf['early_ult'].mean():.1%}")

        # Строим частотный словарь предметов для этого архетипа
        item_freq = {}
        for seq_str in cdf["_items_sequence"].dropna():
            try:
                seq = json.loads(seq_str)
                for item_id in seq:
                    item_freq[item_id] = item_freq.get(item_id, 0) + 1
            except Exception:
                pass

        # Нормализуем: частота → вероятность (0..100%)
        total_matches = n
        item_weights = {
            iid: round(count / total_matches * 100, 2)
            for iid, count in item_freq.items()
            if count >= max(2, total_matches * 0.02)  # Отсекаем редкие (< 2%)
        }

        archetypes[str(cid)] = {
            "name": name,
            "matches_analyzed": n,
            "popularity_weight": round(pct, 4),
            "avg_spent": {
                "Weapon": round(float(cdf["spent_weapon"].mean()), 1),
                "Vitality": round(float(cdf["spent_vitality"].mean()), 1),
                "Spirit": round(float(cdf["spent_spirit"].mean()), 1),
            },
            "spike_rates": {
                "Weapon": round(float(cdf["spike_weapon"].mean()), 4),
                "Vitality": round(float(cdf["spike_vitality"].mean()), 4),
                "Spirit": round(float(cdf["spike_spirit"].mean()), 4),
            },
            "item_weights": item_weights,  # Для Шага 4: взвешенный выбор предметов
            "_row_indices": cdf.index.tolist(),  # Для Шага 3: FP-Growth
        }

    # Сохраняем DF с метками для Шага 3
    df.to_csv(OUTPUT_DIR / f"hero_{hero_id}_clustered.csv", index=False)

    # Добавляем ability sequences в архетипы
    abilities_path = DATA_DIR / f"hero_{hero_id}_abilities.json"
    if abilities_path.exists():
        with open(abilities_path, "r", encoding="utf-8") as f:
            all_ability_orders = json.load(f)
        _attach_ability_sequences(archetypes, df, all_ability_orders)

    return archetypes


def _attach_ability_sequences(archetypes: dict, df: pd.DataFrame, ability_orders: list):
    """
    Привязываем ability sequences к кластерам.
    Сохраняем топ-10 секвенций по популярности (matches) для каждого архетипа.
    Температура в JS будет выбирать: низкая = самая популярная, высокая = редкие.
    """
    # Строим маппинг: ability_id → slot name (по индексу первого появления)
    # У нас есть последовательность в _ability_sequence колонке DF
    # Определяем 4 уникальных ability_id через все секвенции
    from collections import Counter
    all_ids_in_order = []
    for seq_str in df["_ability_sequence"].dropna():
        try:
            seq = json.loads(seq_str)
            all_ids_in_order.extend(seq)
        except Exception:
            pass

    # Топ-4 абильных аида = S1, S2, S3, Ult (в порядке популярности)
    top4 = [aid for aid, _ in Counter(all_ids_in_order).most_common(4)]
    slot_names = {}
    labels = ["S1", "S2", "S3", "Ult"]
    for i, aid in enumerate(top4):
        slot_names[str(aid)] = labels[i] if i < len(labels) else f"A{i+1}"

    # Преобразуем каждую секвенцию в понятные имена слотов
    tier_map = {1: "UNL", 2: "T1", 3: "T2", 4: "T3"}
    class_map = {1: "t-unlock", 2: "t-tier1", 3: "t-tier2", 4: "t-tier3"}

    named_orders = []
    for order in ability_orders:
        seq = order.get("abilities", [])
        if not seq:
            continue
        stages = {}
        named_seq = []
        for aid in seq[:16]:
            aid_s = str(aid)
            slot_name = slot_names.get(aid_s, f"#{aid_s[-4:]}")
            stages[aid_s] = stages.get(aid_s, 0) + 1
            tier = min(stages[aid_s], 4)
            named_seq.append({
                "name": slot_name,
                "label": tier_map[tier],
                "cssClass": class_map[tier]
            })
        named_orders.append({
            "matches": order.get("matches", 0),
            "wins": order.get("wins", 0),
            "sequence": named_seq
        })

    # Сортируем по популярности (matches для низкой темп-ы, редкие для высокой)
    named_orders.sort(key=lambda x: x["matches"], reverse=True)

    for arch_id in archetypes:
        # Через _row_indices не передаем (ability sequences общие для всех архетипов)
        archetypes[arch_id]["ability_sequences"] = named_orders[:10]
        archetypes[arch_id]["slot_names"] = slot_names


def export_meta_weights(all_archetypes: dict):
    """
    Экспортируем в формат meta_weights.json (уже используется в проекте).
    Совместимо с текущей структурой: {hero_id: {archetype_id: {..., slots: {...}}}}
    """
    print("\nЭкспорт meta_weights.json...")

    # Трансформируем в слотовый формат (как в текущем meta_weights.json)
    meta_weights = {}

    for hero_id, archetypes in all_archetypes.items():
        meta_weights[str(hero_id)] = {}

        for arch_id, arch_data in archetypes.items():
            item_weights = arch_data.get("item_weights", {})

            # Разбиваем предметы по "слотам" (позициям в порядке частоты покупки)
            sorted_items = sorted(
                item_weights.items(), key=lambda x: x[1], reverse=True
            )

            # Группируем по ценовым тирам для приближения к реальным слотам
            slots = {}
            slot_idx = 1
            for item_id, weight in sorted_items:
                slots[str(slot_idx)] = {item_id: weight}
                slot_idx += 1

            meta_weights[str(hero_id)][arch_id] = {
                "name": arch_data["name"],
                "matches_analyzed": arch_data["matches_analyzed"],
                "slots": slots,
            }

    out_path = (
        Path(__file__).parent.parent
        / "randomizer" / "static" / "randomizer" / "meta_weights.json"
    )
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(meta_weights, f, ensure_ascii=False)
    print(f"  ✓ Сохранено в {out_path.name}")


def export_meta_rules(all_archetypes: dict):
    print("Экспорт meta_rules.json (для test_ml.html + app.js)...")

    meta_rules = {}
    for hero_id, archetypes in all_archetypes.items():
        meta_rules[str(hero_id)] = {}
        for arch_id, arch_data in archetypes.items():
            meta_rules[str(hero_id)][arch_id] = {
                "name": arch_data["name"],
                "matches_analyzed": arch_data["matches_analyzed"],
                "popularity_weight": arch_data["popularity_weight"],
                "avg_spent": arch_data["avg_spent"],
                "spike_rates": arch_data["spike_rates"],
                "base_weights": arch_data.get("item_weights", {}),
                # ability_sequences: сортированы по популярности.
                # JS: низкая темп = берём [0], высокая темп = берём с рандомного индекса
                "ability_sequences": arch_data.get("ability_sequences", []),
                "slot_names": arch_data.get("slot_names", {}),
                # synergy_rules заполнит Шаг 3
                "synergy_rules": [],
            }

    out_path = (
        Path(__file__).parent.parent
        / "randomizer" / "static" / "randomizer" / "meta_rules.json"
    )
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(meta_rules, f, ensure_ascii=False)
    print(f"  ✓ Сохранено в {out_path.name}")


def main():
    print("=" * 60)
    print("ШАГ 2: КЛАСТЕРИЗАЦИЯ — ОПРЕДЕЛЕНИЕ АРХЕТИПОВ")
    print("=" * 60)

    # Определяем целевых героев
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        target_heroes = [int(sys.argv[1])]
    else:
        # Берем всех, для которых есть данные
        target_heroes = [
            int(p.stem.split("_")[1])
            for p in DATA_DIR.glob("hero_*_raw.csv")
        ]

    if not target_heroes:
        print("ОШИБКА: Нет данных. Запусти step1_preprocess.py сначала.")
        return

    force_k = None
    if "--k" in sys.argv:
        k_idx = sys.argv.index("--k")
        force_k = int(sys.argv[k_idx + 1])
        print(f"Принудительное k={force_k}")

    all_archetypes = {}

    for hero_id in target_heroes:
        print(f"\n{'─' * 50}")
        print(f"Герой {hero_id}")
        archetypes = cluster_hero(hero_id, force_k=force_k)
        if archetypes:
            all_archetypes[hero_id] = archetypes

    if all_archetypes:
        export_meta_weights(all_archetypes)
        export_meta_rules(all_archetypes)
        print(f"\n{'=' * 60}")
        print(f"ГОТОВО! Обработано героев: {len(all_archetypes)}")
        print("Следующий шаг: python pipeline/step3_association_rules.py")
    else:
        print("WARN: Нет данных для кластеризации.")


if __name__ == "__main__":
    main()
