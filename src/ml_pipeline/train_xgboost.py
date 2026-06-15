import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, top_k_accuracy_score

def train_model():
    print("Загрузка данных...")
    X = np.load("data/processed/xgb_X.npy")
    y = np.load("data/processed/xgb_Y.npy")
    
    print(f"Размер датасета: {X.shape[0]} примеров, {X.shape[1]} признаков")
    
    from sklearn.preprocessing import LabelEncoder
    import json
    
    le = LabelEncoder()
    y = le.fit_transform(y)
    
    # Сохраняем маппинг классов для генератора
    label_mapping = {int(encoded): int(original) for encoded, original in enumerate(le.classes_)}
    with open("data/processed/xgb_label_mapping.json", "w") as f:
        json.dump(label_mapping, f)
    
    num_classes = len(le.classes_)
    print(f"Количество уникальных предметов для предсказания: {num_classes}")
    
    # Настраиваем модель
    # objective 'multi:softprob' заставляет модель выдавать вероятности для каждого класса
    model = xgb.XGBClassifier(
        objective='multi:softprob',
        num_class=num_classes,
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        tree_method='hist', # Быстрое обучение на CPU
        random_state=42,
        n_jobs=-1
    )
    
    print("Обучение модели XGBoost на всем датасете (это может занять пару минут)...")
    model.fit(X, y)
    
    print("Сохранение модели...")
    model.save_model("data/processed/xgb_model.json")
    print("Модель успешно сохранена в data/processed/xgb_model.json!")

if __name__ == "__main__":
    train_model()
