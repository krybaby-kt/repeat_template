# Repeat Template 🔄

Универсальный декоратор для повторного выполнения функций с поддержкой синхронных и асинхронных функций.

## Описание

Этот проект представляет собой готовый к использованию шаблон декоратора `@__repeat__`, который автоматически повторяет выполнение функции при возникновении исключений. Декоратор интеллектуально определяет тип функции (синхронная или асинхронная) и применяет соответствующую логику обработки.

## Особенности

✅ **Универсальность** - работает с sync и async функциями автоматически  
✅ **Гибкие настройки** - количество попыток, задержки, типы исключений  
✅ **Экспоненциальный backoff** - увеличивающиеся задержки между попытками  
✅ **Фильтрация исключений** - retry только для определенных типов ошибок  
✅ **Полная типизация** - поддержка TypeScript-подобной типизации  
✅ **Логирование** - детальные логи процесса повторных попыток  

## Быстрый старт

```python
from repeat import __repeat__

# Простое использование
@__repeat__()
def unstable_function():
    # Ваш код, который может падать
    return "success"

# Асинхронная функция
@__repeat__(tries=3, delay=1.0)
async def async_api_call():
    # Асинхронный код
    return await some_api_call()
```

## Параметры декоратора

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `tries` | `int` | `5` | Количество попыток выполнения |
| `delay` | `float` | `0.0` | Начальная задержка между попытками (сек) |
| `backoff` | `float` | `1.0` | Множитель увеличения задержки |
| `exceptions` | `Exception \| Tuple[Exception, ...]` | `Exception` | Типы исключений для retry |

## Примеры использования

### Базовое использование
```python
@__repeat__(tries=3)
def flaky_network_call():
    response = requests.get("https://api.example.com/data")
    return response.json()
```

### С задержкой и exponential backoff
```python
@__repeat__(tries=5, delay=1.0, backoff=2.0)
def database_operation():
    # 1s, 2s, 4s, 8s задержки между попытками
    return db.execute_query()
```

### Фильтрация исключений
```python
@__repeat__(tries=3, exceptions=ConnectionError)
def network_request():
    # Повторяет только при ConnectionError
    # ValueError пройдет без retry
    return make_request()

@__repeat__(tries=3, exceptions=(TimeoutError, ConnectionError))
def multiple_exceptions():
    # Обрабатывает несколько типов исключений
    return api_call()
```

### Асинхронные функции
```python
@__repeat__(tries=3, delay=0.5)
async def async_operation():
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

# Использование
result = await async_operation()
```

## Логирование

Декоратор автоматически логирует процесс повторных попыток:

```
WARNING: Attempt 1/3 failed: Connection timeout. Retrying in 1.00s...
WARNING: Attempt 2/3 failed: Connection timeout. Retrying in 2.00s...
ERROR: All 3 attempts failed. Last error: Connection timeout
```

Для настройки логирования:
```python
import logging
logging.basicConfig(level=logging.WARNING)
```

## Установка

1. Скопируйте файл `repeat.py` в ваш проект
2. Импортируйте декоратор:
   ```python
   from repeat import __repeat__
   ```

## Требования

- Python 3.7+
- Стандартные библиотеки: `typing`, `functools`, `logging`, `inspect`, `asyncio`, `time`

## Структура проекта

```
repeat_template/
├── repeat.py          # Основной модуль с декоратором
├── README.md          # Документация
└── examples/          # Примеры использования (опционально)
```

## Примеры из реального мира

### Работа с API
```python
@__repeat__(tries=3, delay=1.0, exceptions=requests.RequestException)
def fetch_user_data(user_id):
    response = requests.get(f"https://api.service.com/users/{user_id}")
    response.raise_for_status()
    return response.json()
```

### Работа с базой данных
```python
@__repeat__(tries=5, delay=0.1, backoff=1.5, exceptions=DatabaseError)
def create_user(user_data):
    with database.transaction():
        return database.users.create(user_data)
```

### Файловые операции
```python
@__repeat__(tries=3, exceptions=OSError)
def save_file(filename, content):
    with open(filename, 'w') as f:
        f.write(content)
```

## Лицензия

MIT License - используйте свободно в своих проектах.

## Вклад в проект

Этот проект создан как базовый шаблон. Вы можете:
- Форкнуть репозиторий
- Адаптировать под свои нужды
- Расширить функциональность
- Использовать как основу для более сложных решений

---

*Создано как универсальный шаблон для retry-логики в Python проектах* 🚀
