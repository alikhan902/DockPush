# Базовый образ
FROM python:3.10

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .


# Команда по умолчанию
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
