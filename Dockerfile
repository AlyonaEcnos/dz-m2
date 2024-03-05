# Используйте официальный образ Python
FROM python:3.12

# Установите зависимости с помощью Poetry
RUN mkdir -p /usr/src/app 

# Установите рабочую директорию в /usr/src/app 
WORKDIR /usr/src/app 

# Скопируйте остальные файлы в контейнер
COPY . . 

# Команда для запуска вашего приложения
CMD ["python", "bot.py"]
