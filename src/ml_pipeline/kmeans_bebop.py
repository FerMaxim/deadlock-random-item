import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

def run_clustering():
    csv_path = "data/processed/bebop_items_matrix.csv"
    print(f"Загрузка данных из {csv_path}...")
    df = pd.read_csv(csv_path)

    print(f"Всего записей до фильтрации: {len(df)}")
    
    # Отбрасываем NaN бейджи
    df = df.dropna(subset=['lobby_badge'])
    
    # Берем только верхние 30% по MMR (Lobby Badge)
    badge_threshold = df['lobby_badge'].quantile(0.70)
    print(f"Порог высокого MMR (Lobby Badge): {badge_threshold:.2f}")
    
    df_high_mmr = df[df['lobby_badge'] >= badge_threshold].copy()
    print(f"Записей после фильтрации по высокому MMR: {len(df_high_mmr)}")

    # Фичи для кластеризации
    features = ['weapon_souls', 'vitality_souls', 'spirit_souls']
    X = df_high_mmr[features]

    # Масштабирование признаков
    print("Масштабирование данных (StandardScaler)...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Поиск оптимального K
    print("Поиск оптимального количества кластеров (K) от 2 до 6...")
    best_k = 2
    best_score = -1
    models = {}

    for k in range(2, 7):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init='auto')
        labels = kmeans.fit_predict(X_scaled)
        score = silhouette_score(X_scaled, labels)
        models[k] = kmeans
        print(f"  K={k} | Silhouette Score: {score:.4f}")
        
        if score > best_score:
            best_score = score
            best_k = k

    print(f"\nОптимальное количество кластеров: {best_k} (Score: {best_score:.4f})")

    # Применяем лучшую модель
    best_model = models[best_k]
    df_high_mmr['cluster_id'] = best_model.labels_

    # Денормализуем центроиды, чтобы увидеть реальные души
    centroids_scaled = best_model.cluster_centers_
    centroids_real = scaler.inverse_transform(centroids_scaled)

    print("\n--- Архетипы сборок (Центроиды) ---")
    for i, center in enumerate(centroids_real):
        print(f"Кластер {i}: Weapon={center[0]:.0f} душ | Vitality={center[1]:.0f} душ | Spirit={center[2]:.0f} душ")

    output_path = "data/processed/bebop_clustered.csv"
    df_high_mmr.to_csv(output_path, index=False)
    print(f"\nКластеризованный датасет сохранен в {output_path}")

if __name__ == "__main__":
    run_clustering()
