# Константы для полей модели User

# Длина полей
USERNAME_MAX_LENGTH = 100
PHONE_MAX_LENGTH = 20
PHONE_MIN_LENGTH = 10
TG_ID_MAX_LENGTH = 50

# Ограничения валидации
USERNAME_MIN_LENGTH = 1

# Значения по умолчанию для суперпользователя
SUPERUSER_DEFAULT_USERNAME = 'admin'
SUPERUSER_DEFAULT_PHONE = '+00000000000'

# Логирование
LOG_FILE = 'project.log'
MAX_BYTES = 5 * 1024 * 1024  # 5 MB
BACKUP_COUNT = 3
