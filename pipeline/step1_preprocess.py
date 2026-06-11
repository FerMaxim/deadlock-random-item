"""
Шаг 1: Сбор и препроцессинг данных
====================================
Использует реальные эндпоинты deadlock-api.com:
- /v1/analytics/item-stats   → статистика покупки предметов по герою
- /v1/analytics/ability-order-stats → порядок прокачки способностей

ВАЖНО: item-stats возвращает агрегированные данные, а не таймлайны!
Мы используем avg_buy_time_s (среднее время покупки) как суррогат для
определения фазы игры (Early/Mid/Late) и bucket для анализа экономики.

Запуск: python pipeline/step1_preprocess.py [hero_id]
         python pipeline/step1_preprocess.py 13        # только Haze
"""

import json
import sys
import time
import requests
import pandas as pd
import numpy as np
from pathlib import Path

# --- НАСТРОЙКИ ---
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

API_BASE = "https://api.deadlock-api.com"
SPIKE_THRESHOLD = 4800   # Investment Spike порог
MIN_BADGE = 90           # Минимальный ранг (Eternus/Oracle)

ITEMS_DB_PATH = BASE_DIR / "randomizer" / "static" / "randomizer" / "data.json"

# ID героев
HERO_IDS = [1, 2, 3, 4, 6, 7, 8, 10, 11, 12, 13, 14, 15, 17, 18, 25, 27, 31, 35, 50, 52]

# Время в секундах — граница фаз игры
EARLY_CUTOFF = 600    # < 10 минут
MID_CUTOFF = 1200     # < 20 минут


def load_items_db() -> dict:
    """Загружаем базу предметов из локального data.json."""
    with open(ITEMS_DB_PATH, "r", encoding="utf-8") as f:
        items_list = json.load(f)
    # id может быть int или str в разных версиях
    return {str(item["id"]): item for item in items_list}


def fetch_item_stats(hero_id: int, min_badge: int = MIN_BADGE) -> list[dict]:
    """
    GET /v1/analytics/item-stats
    Возвращает статистику по каждому предмету для данного героя.
    Поля: item_id, bucket, wins, losses, matches, players,
          avg_buy_time_s, avg_sell_time_s, avg_buy_time_relative
    """
    url = f"{API_BASE}/v1/analytics/item-stats"
    params = {"hero_id": hero_id, "min_average_badge": min_badge}
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def fetch_ability_order_stats(hero_id: int, min_badge: int = MIN_BADGE) -> list[dict]:
    """
    GET /v1/analytics/ability-order-stats
    Возвращает топ-последовательности прокачки способностей с метриками.
    Поля: abilities (список ability_id в порядке прокачки), wins, losses, matches
    """
    url = f"{API_BASE}/v1/analytics/ability-order-stats"
    params = {"hero_id": hero_id, "min_average_badge": min_badge}
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def build_item_phase_vectors(
    item_stats: list[dict], items_db: dict
) -> pd.DataFrame:
    """
    Из агрегированной статистики предметов строим вектор трат по категориям.

    СТРАТЕГИЯ: bucket=0 → финальная сборка (все предметы куплены).
    Мы группируем предметы по категории и считаем суммарный spent.

    Для симуляции "сборок" генерируем синтетические векторы,
    используя avg_buy_time_s как вес для временной последовательности:
    - Early: avg_buy_time_s < 600s
    - Mid:   600 ≤ avg_buy_time_s < 1200s
    - Late:  avg_buy_time_s ≥ 1200s
    """
    records = []

    for entry in item_stats:
        item_id = str(entry.get("item_id", ""))
        item_info = items_db.get(item_id)
        if not item_info:
            continue

        cat = item_info.get("category", "")
        if cat not in ("Weapon", "Vitality", "Spirit"):
            continue

        price = item_info.get("price", 0)
        if price == 0:
            continue

        avg_buy_t = entry.get("avg_buy_time_s", 9999)
        matches = entry.get("matches", 0)
        players = entry.get("players", 1)

        # Фаза покупки
        if avg_buy_t < EARLY_CUTOFF:
            phase = "early"
        elif avg_buy_t < MID_CUTOFF:
            phase = "mid"
        else:
            phase = "late"

        records.append({
            "item_id": item_id,
            "category": cat,
            "price": price,
            "avg_buy_time_s": avg_buy_t,
            "matches": matches,
            "players": players,
            "phase": phase,
        })

    return pd.DataFrame(records)


def synthesize_build_vectors(
    item_df: pd.DataFrame,
    ability_orders: list[dict],
    n_samples: int = 500,
) -> pd.DataFrame:
    """
    Генерируем синтетические векторы сборок.

    Подход: Каждый вектор = один "тип сборки", определяемый как
    взвешенная выборка предметов из каждой категории. Вес = частота
    покупки (matches), скорректированная на фазу игры.

    Это позволяет имитировать разные архетипы без детальных таймлайнов.
    """
    if item_df.empty:
        return pd.DataFrame()

    vectors = []
    rng = np.random.default_rng(42)

    # Предвычислим словарь категорий
    weapon_items = item_df[item_df["category"] == "Weapon"]
    vitality_items = item_df[item_df["category"] == "Vitality"]
    spirit_items = item_df[item_df["category"] == "Spirit"]

    # Получаем уникальные ability_id для индексации
    all_ability_ids = set()
    for order in ability_orders:
        for ab in order.get("abilities", []):
            all_ability_ids.add(ab)
    ability_idx = {ab: i for i, ab in enumerate(sorted(all_ability_ids))}

    for _ in range(n_samples):
        # Случайно выбираем предметы с весом по matches
        def pick_items_from_cat(cat_df: pd.DataFrame, min_n=2, max_n=8):
            if cat_df.empty:
                return 0, []
            weights = cat_df["matches"].values.astype(float)
            weights = weights / weights.sum()
            n = rng.integers(min_n, max(min_n + 1, max_n))
            n = min(n, len(cat_df))
            chosen_idx = rng.choice(len(cat_df), size=n, replace=False, p=weights)
            chosen = cat_df.iloc[chosen_idx]
            total_spent = int(chosen["price"].sum())
            return total_spent, chosen["item_id"].tolist()

        spent_w, items_w = pick_items_from_cat(weapon_items, 2, 6)
        spent_v, items_v = pick_items_from_cat(vitality_items, 1, 5)
        spent_s, items_s = pick_items_from_cat(spirit_items, 1, 5)

        total = max(spent_w + spent_v + spent_s, 1)

        # Выбираем случайный порядок прокачки способностей
        ability_vec = {"skill_0_lvl": 0, "skill_1_lvl": 0, "skill_2_lvl": 0, "ult_lvl": 0}
        early_ult = 0

        if ability_orders:
            w = [o.get("matches", 1) for o in ability_orders]
            w_sum = sum(w)
            w_norm = [x / w_sum for x in w]
            chosen_order_idx = rng.choice(len(ability_orders), p=w_norm)
            chosen_order = ability_orders[chosen_order_idx]

            # Маппинг: 4 основных слота способностей (0,1,2,3)
            # ability-order-stats возвращает ability_id, нам нужны индексы
            # Используем heuristic: сортируем по частоте встречаемости
            abilities_seq = chosen_order.get("abilities", [])
            if len(abilities_seq) >= 4:
                unique_abs = list(dict.fromkeys(abilities_seq))  # уник порядок
                # Берем топ-4 уникальных как S1..S3, Ult (не менее 4 нужно)
                unique_abs = unique_abs[:4]
                for slot_i, ab in enumerate(unique_abs):
                    count = abilities_seq.count(ab)
                    key = ["skill_0_lvl", "skill_1_lvl", "skill_2_lvl", "ult_lvl"][slot_i]
                    ability_vec[key] = min(count, 7)

                # early_ult: если 4-й (ульта) прокачан рано
                if len(unique_abs) >= 4:
                    ult_positions = [
                        i for i, a in enumerate(abilities_seq[:12])
                        if a == unique_abs[3]
                    ]
                    early_ult = int(len(ult_positions) >= 3 and ult_positions[-1] < 10 if ult_positions else False)

        vec = {
            "spent_weapon": spent_w,
            "spent_vitality": spent_v,
            "spent_spirit": spent_s,
            "spent_total": total,

            # Флаги спайка (умножим на 5 в Шаге 2)
            "spike_weapon": int(spent_w >= SPIKE_THRESHOLD),
            "spike_vitality": int(spent_v >= SPIKE_THRESHOLD),
            "spike_spirit": int(spent_s >= SPIKE_THRESHOLD),

            # Пропорции
            "ratio_weapon": spent_w / total,
            "ratio_vitality": spent_v / total,
            "ratio_spirit": spent_s / total,

            # Способности
            **ability_vec,
            "early_ult": early_ult,

            # Для FP-Growth (Шаг 3)
            "_items_sequence": json.dumps(items_w + items_v + items_s),
            "_ability_sequence": json.dumps(
                ability_orders[0].get("abilities", []) if ability_orders else []
            ),
        }
        vectors.append(vec)

    return pd.DataFrame(vectors)


def process_hero(hero_id: int, items_db: dict) -> pd.DataFrame:
    """Основная функция: качаем данные и строим матрицу признаков."""
    print(f"\n{'─' * 50}")
    print(f"Герой {hero_id}")

    try:
        print("  → Загружаем item-stats...")
        item_stats = fetch_item_stats(hero_id)
        print(f"     Получено {len(item_stats)} записей предметов")
    except Exception as e:
        print(f"  ОШИБКА item-stats: {e}")
        return pd.DataFrame()

    time.sleep(0.3)  # Rate limiting

    try:
        print("  → Загружаем ability-order-stats...")
        ability_orders = fetch_ability_order_stats(hero_id)
        print(f"     Получено {len(ability_orders)} порядков прокачки")
    except Exception as e:
        print(f"  ОШИБКА ability-order-stats: {e}")
        ability_orders = []

    # Строим DataFrame предметов
    item_df = build_item_phase_vectors(item_stats, items_db)
    if item_df.empty:
        print(f"  WARN: Нет предметов из нашей БД для героя {hero_id}")
        return pd.DataFrame()

    print(f"  Предметов в БД: W={len(item_df[item_df.category=='Weapon'])}  "
          f"V={len(item_df[item_df.category=='Vitality'])}  "
          f"S={len(item_df[item_df.category=='Spirit'])}")

    # Сохраняем предметную статистику (нужно для Шага 4 — взвешенный выбор)
    item_df.to_csv(DATA_DIR / f"hero_{hero_id}_items.csv", index=False)

    # Генерируем синтетические векторы сборок
    df = synthesize_build_vectors(item_df, ability_orders, n_samples=600)

    if df.empty:
        print(f"  WARN: Не удалось сгенерировать векторы")
        return pd.DataFrame()

    # Сохраняем сырые ability orders для step2 (топ-50 по матчам)
    ability_orders_top = sorted(ability_orders, key=lambda x: x.get('matches', 0), reverse=True)[:50]
    with open(DATA_DIR / f"hero_{hero_id}_abilities.json", "w", encoding="utf-8") as f:
        json.dump(ability_orders_top, f, ensure_ascii=False)

    out_path = DATA_DIR / f"hero_{hero_id}_raw.csv"
    df.to_csv(out_path, index=False)

    print(f"  ✓ Создано {len(df)} синтетических векторов → {out_path.name}")
    print(f"  Spike rates: W={df['spike_weapon'].mean():.1%}  "
          f"V={df['spike_vitality'].mean():.1%}  "
          f"S={df['spike_spirit'].mean():.1%}")
    print(f"  Avg spent: W={df['spent_weapon'].mean():.0f}  "
          f"V={df['spent_vitality'].mean():.0f}  "
          f"S={df['spent_spirit'].mean():.0f}")

    return df


def main():
    print("=" * 60)
    print("ШАГ 1: СБОР И ПРЕПРОЦЕССИНГ ДАННЫХ DEADLOCK")
    print(f"API: {API_BASE}")
    print(f"Min badge rank: {MIN_BADGE} (High MMR)")
    print("=" * 60)

    items_db = load_items_db()
    print(f"Загружено {len(items_db)} предметов из data.json")

    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        target_heroes = [int(sys.argv[1])]
        print(f"Обрабатываем только героя: {target_heroes[0]}")
    else:
        target_heroes = HERO_IDS
        print(f"Обрабатываем {len(target_heroes)} героев")

    results = {}
    for hero_id in target_heroes:
        df = process_hero(hero_id, items_db)
        if not df.empty:
            results[hero_id] = len(df)
        time.sleep(0.5)  # Rate limiting между героями

    print(f"\n{'=' * 60}")
    print(f"ГОТОВО: Обработано {len(results)} героев")
    for hid, count in results.items():
        print(f"  Hero {hid}: {count} векторов")
    print(f"\nСледующий шаг: python pipeline/step2_clustering.py")


if __name__ == "__main__":
    main()
