# Используйте официальный образ Python
FROM python:3.12

# Установите рабочую директорию в /app
WORKDIR /app

# Скопируйте зависимости и pyproject.toml в контейнер
COPY pyproject.toml poetry.lock /app/

# Установите зависимости с помощью Poetry
RUN pip install poetry && poetry install --no-dev

# Скопируйте остальные файлы в контейнер
COPY . /app/

# Команда для запуска вашего приложения
CMD ["python", "bot.py"]
