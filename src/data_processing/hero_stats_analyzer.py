import duckdb
import json

# Загружаем карту героев из файла
with open('data/reference/heroes.json', 'r', encoding='utf-8') as f:
    hero_map = json.load(f)
    # Ключи в JSON всегда строки, поэтому нужно будет использовать str(h_id) при поиске

con = duckdb.connect()
threshold = con.query("SELECT quantile_cont(average_badge_team0, 0.85) FROM 'data/raw/match_player_86.parquet'").fetchone()[0]

query = f"""
SELECT 
    hero_id, 
    COUNT(*) as total_matches,
    CAST(SUM(CASE WHEN average_badge_team0 >= {threshold} THEN 1 ELSE 0 END) AS INTEGER) as top_15_matches
FROM 'data/raw/match_player_86.parquet' 
GROUP BY hero_id 
ORDER BY total_matches DESC
"""
df = con.query(query).df()

print("| Герой | Всего матчей | Матчей (Топ-15% MMR) |")
print("|-------|--------------|----------------------|")
for _, row in df.iterrows():
    h_id = int(row['hero_id'])
    h_name = hero_map.get(str(h_id), f"Hero {h_id}")
    print(f"| {h_name} | {int(row['total_matches']):,} | {int(row['top_15_matches']):,} |".replace(',', ' '))
