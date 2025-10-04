FROM python:3.11-slim

WORKDIR /app

# 3. Установка переменных окружения
#    - PYTHONUNBUFFERED: чтобы логи Python сразу выводились в консоль Docker
#    - PYTHONPATH: чтобы Python мог находить ваши модули в /app
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /app


# Ставим зависимости проекта
# 4. Копируем файл с зависимостями и устанавливаем их
#    Это делается до копирования остального кода для использования кэша Docker
COPY ./src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Копируем весь остальной код приложения
COPY ./src /app/src
COPY ./alembic /app/alembic
COPY ./alembic.ini /app/alembic.ini

# CMD - команда по умолчанию, которая будет переопределена в docker-compose
# Она нужна, если вы захотите запустить образ напрямую через `docker run`
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

