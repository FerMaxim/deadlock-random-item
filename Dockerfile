FROM python:3.12-slim

# Установка переменных окружения
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Рабочая директория
WORKDIR /app

# Установка системных зависимостей для сборки C-расширений (pycairo и др.)
RUN apt-get update && apt-get install -y \
    gcc \
    libcairo2-dev \
    pkg-config \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Установка зависимостей
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Копирование проекта
COPY . /app/

# Запуск ASGI-сервера Daphne
CMD ["daphne", "-b", "0.0.0.0", "-p", "80", "deadlock_project.asgi:application"]
