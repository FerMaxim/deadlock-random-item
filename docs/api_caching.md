# Кэширование ML Моделей (API Performance)

## Проблема производительности
Сгенерированные XGBoost-модели предметов имеют размер около 60-80 МБ на каждого героя. Модели способностей — около 2.5 МБ.
При стандартном подходе (загрузка файла с жесткого диска при каждом HTTP-запросе), время ответа API составляет от 6 до 10 секунд на генерацию. Это неприемлемо для пользовательского интерфейса, так как при изменении температуры или архетипа юзеру приходится ждать заново.

## Текущее решение (In-Memory Cache)
Для решения этой проблемы в `server.py` был реализован In-Memory кэш инстансов `DeadlockBuildGenerator`:

```python
# Глобальный кэш
generator_cache = {}

if cache_key not in generator_cache:
    generator = DeadlockBuildGenerator(hero_id=hero_id, archetype=archetype)
    generator_cache[cache_key] = generator
else:
    generator = generator_cache[cache_key]
    # Сброс состояния перед новой генерацией...
```

**Результат:** Первая генерация билда для героя занимает ~6 секунд (загрузка с диска). Все последующие генерации для этого же героя (с другими температурами или архетипами) происходят мгновенно (< 100 мс).

## Потребление ОЗУ и Production рекомендации
38 героев * ~65 МБ = ~2.5 ГБ (чистых данных).
С учетом накладных расходов Python и C++ структур XGBoost, кэш всех 38 героев одновременно займет **около 4-5 ГБ оперативной памяти**.

Для продакшена с ограниченным объемом ОЗУ (например, 1 ГБ) рекомендуется использовать настраиваемый **LRU Cache** с возможностью включения/отключения. 

### Как сделать кэш включаемым (Toggle Cache)
Если вы хотите переносить проект на разные сервера, вы можете использовать переменную окружения `ENABLE_CACHE`:

```python
import os
from functools import lru_cache

# Читаем настройку из .env (по умолчанию выключено)
USE_CACHE = os.environ.get('ENABLE_CACHE', '0') == '1'

# Создаем функцию с кэшем на 3 героя (для 1 ГБ ОЗУ)
@lru_cache(maxsize=3)
def _get_generator_cached(hero_id):
    return DeadlockBuildGenerator(hero_id=hero_id, archetype=0)

def get_generator(hero_id):
    if USE_CACHE:
        # Берем из кэша
        gen = _get_generator_cached(hero_id)
        # Очищаем состояние для новой генерации
        gen.inventory = []
        gen.ability_points_spent = 0
        gen.item_history = []
        gen.ability_history = []
        gen.ability_levels = {sk_id: 0 for sk_id in gen.hero_abilities.keys()}
        return gen
    else:
        # Каждый раз грузим с диска
        return DeadlockBuildGenerator(hero_id=hero_id, archetype=0)
```

Чтобы включить кэширование на продакшен-сервере, достаточно будет прописать в консоли перед запуском:
`set ENABLE_CACHE=1` (для Windows)
`export ENABLE_CACHE=1` (для Linux)
