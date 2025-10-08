import argparse
import asyncio
import logging
import os
import sys
from dotenv import load_dotenv

# --- ИЗМЕНЕНИЕ 1: Загружаем переменные из .env файла ---
# load_dotenv() найдет .env файл, пройдясь по иерархии папок вверх от скрипта.
# Это сработает и при запуске из Docker, и локально.
load_dotenv()

# Добавляем корень проекта в пути, чтобы импорты `from src...` работали
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.core.init_db import create_user

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Главная асинхронная функция."""
    # --- ИЗМЕНЕНИЕ 2: Используем os.getenv для значений по умолчанию ---
    parser = argparse.ArgumentParser(description="Создание нового суперпользователя.")
    parser.add_argument(
        "--username",
        default=os.getenv("FIRST_SUPERUSER_USERNAME"), # Берем значение из окружения
        help="Имя пользователя (логин). По умолчанию: FIRST_SUPERUSER_USERNAME из .env"
    )
    parser.add_argument(
        "--phone",
        default=os.getenv("FIRST_SUPERUSER_PHONE"),
        help="Номер телефона. По умолчанию: FIRST_SUPERUSER_PHONE из .env"
    )
    parser.add_argument(
        "--password",
        default=os.getenv("FIRST_SUPERUSER_PASSWORD"),
        help="Пароль. По умолчанию: FIRST_SUPERUSER_PASSWORD из .env"
    )
    parser.add_argument(
        "--email",
        default=os.getenv("FIRST_SUPERUSER_EMAIL"),
        help="Адрес email. По умолчанию: FIRST_SUPERUSER_EMAIL из .env"
    )

    args = parser.parse_args()

    # --- ИЗМЕНЕНИЕ 3: Проверяем, что переменные действительно загрузились ---
    if not all([args.username, args.phone, args.password, args.email]):
        print("❌ Ошибка: Не все необходимые переменные"
              " окружения (FIRST_SUPERUSER_...) заданы в .env файле.")
        sys.exit(1) # Выходим с кодом ошибки

    logger.info(f"Попытка создать суперпользователя с именем '{args.email}'...")
    user = await create_user(
        username=args.username,
        phone=args.phone,
        password=args.password,
        email=args.email,
        is_superuser=True,
    )

    if user:
        print(f"✅ Суперпользователь '{user.username}' "
              f"успешно создан с ID: {user.id}")
    else:
        print(f"ℹ️ Суперпользователь '{args.username}' "
              f"не был создан (вероятно, уже существует).")


if __name__ == "__main__":
    asyncio.run(main())