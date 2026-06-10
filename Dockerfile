FROM python:3.10-slim

# Установка переменных окружения
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Рабочая директория
WORKDIR /app

# Установка зависимостей
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Копирование проекта
COPY . /app/

# Запуск ASGI-сервера Daphne
CMD ["daphne", "-b", "0.0.0.0", "-p", "80", "deadlock_project.asgi:application"]
