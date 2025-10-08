from pydantic import constr

# Определяем кастомные, переиспользуемые типы здесь
PhoneNumber = constr(
    pattern=r'^\+?[1-9]\d{7,14}$',
    min_length=10,
    max_length=15,
)
