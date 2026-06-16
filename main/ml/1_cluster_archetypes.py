import os
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.cluster import KMeans, MiniBatchKMeans
from sklearn.metrics import silhouette_score
import warnings

warnings.filterwarnings('ignore')

def build_archetypes():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    training_dir = os.path.join(base_dir, "training")
    input_file = os.path.join(training_dir, "ml_ready_dataset.parquet")
    output_file = os.path.join(training_dir, "ml_labeled_dataset.parquet")
    
    print(f"Загрузка датасета: {input_file}...")
    df = pd.read_parquet(input_file)
    print(f"Всего строк: {len(df)}")
    
    # Чтобы векторизовать список ID предметов, превратим его в строку, разделенную пробелами
    print("Векторизация инвентарей (создание мешка слов из ID предметов)...")
    df['item_str'] = df['item_build'].apply(lambda x: ' '.join(map(str, x)))
    
    heroes = df['hero_id'].unique()
    print(f"Найдено уникальных героев: {len(heroes)}")
    
    # Сюда будем складывать лейблы архетипов
    df['archetype'] = -1
    
    vectorizer = CountVectorizer(token_pattern=r'\b\d+\b')
    
    # Для каждого героя находим лучший кластер
    for hero in heroes:
        hero_mask = df['hero_id'] == hero
        df_hero = df[hero_mask]
        
        n_samples = len(df_hero)
        if n_samples < 100:
            # Слишком мало данных для кластеризации
            df.loc[hero_mask, 'archetype'] = 0
            continue
            
        print(f"\nАнализ героя ID {hero} (Матчей: {n_samples})")
        
        # Получаем матрицу частот предметов
        X = vectorizer.fit_transform(df_hero['item_str'])
        
        best_k = 2
        best_score = -1
        best_model = None
        
        # Перебираем количество кластеров от 2 до 5 (архетипов не бывает очень много)
        # Если матчей много, используем подвыборку для Silhouette Score, так как он работает за O(N^2)
        sample_size = min(n_samples, 3000)
        
        for k in range(2, 6):
            kmeans = MiniBatchKMeans(n_clusters=k, random_state=42, batch_size=1024)
            labels = kmeans.fit_predict(X)
            
            # Считаем силуэт только на сэмпле для скорости
            if n_samples > sample_size:
                np.random.seed(42)
                indices = np.random.choice(n_samples, sample_size, replace=False)
                score = silhouette_score(X[indices], labels[indices])
            else:
                score = silhouette_score(X, labels)
                
            if score > best_score:
                best_score = score
                best_k = k
                best_model = kmeans
                
        print(f"Лучшее число архетипов: {best_k} (Silhouette Score: {best_score:.3f})")
        
        # Присваиваем лейблы
        final_labels = best_model.predict(X)
        df.loc[hero_mask, 'archetype'] = final_labels

    # Удаляем временную колонку и сохраняем
    df = df.drop(columns=['item_str'])
    print(f"\nСохранение датасета с разметкой архетипов в {output_file}...")
    df.to_parquet(output_file, engine='pyarrow')
    print("Готово!")

if __name__ == "__main__":
    build_archetypes()
