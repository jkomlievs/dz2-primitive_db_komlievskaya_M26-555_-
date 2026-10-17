import time
from functools import wraps


def handle_db_errors(func):


    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError as e:
            print(f"Ошибка: таблица или столбец не найдены ({e}). Попробуйте снова.")
        except ValueError as e:
            print(f"Некорректное значение: {e}. Попробуйте снова.")
        except FileNotFoundError as e:
            print(f"Ошибка: файл не найден ({e}). Попробуйте снова.")

    return wrapper


def confirm_action(action_name: str):


    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            answer = input(
                f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
            ).strip().lower()
            if answer != "y":
                print("Операция отменена.")
                return None
            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_time(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.monotonic()
        result = func(*args, **kwargs)
        elapsed = time.monotonic() - start
        print(f"Функция {func.__name__} выполнилась за {elapsed:.3f} секунд.")
        return result

    return wrapper


def create_cacher():

    cache = {}

    def cache_result(key, value_func):
        if key in cache:
            return cache[key]
        result = value_func()
        cache[key] = result
        return result

    def clear_cache():
        cache.clear()

    return cache_result, clear_cache