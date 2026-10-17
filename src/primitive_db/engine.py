import shlex

import prompt

from primitive_db import core
from primitive_db.parser import parse_condition, parse_set_clause, parse_values
from primitive_db.utils import (
    delete_table_data,
    get_db_path,
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)

HELP_TEXT = """
***Операции с данными***

Функции:
<command> insert into <имя_таблицы> values (<значение1>, <значение2>, ...) 
- создать запись.
<command> select from <имя_таблицы> where <столбец> = <значение> 
- прочитать записи по условию.
<command> select from <имя_таблицы> - прочитать все записи.
<command> update <имя_таблицы> set <столбец1> = <новое_значение1> 
where <столбец_условия> 
= <значение_условия> - обновить запись.
<command> delete from <имя_таблицы> where <столбец> = <значение> - удалить запись.
<command> info <имя_таблицы> - вывести информацию о таблице.
<command> create_table <имя_таблицы> <столбец1:тип> ... - создать таблицу.
<command> drop_table <имя_таблицы> - удалить таблицу.
<command> list_tables - показать список таблиц.
<command> exit - выход из программы
<command> help - справочная информация

Примечание: строковые значения указывайте в кавычках, например "Anna".
"""

WELCOME_HELP_TEXT = """
<command> exit - выйти из программы
<command> help - справочная информация
"""


def welcome():
    print("Первая попытка запустить проект!")
    print("\n***")
    print(WELCOME_HELP_TEXT)

    while True:
        command = prompt.string("Введите команду: ")

        if command == "exit":
            print("До встречи!")
            break
        elif command == "help":
            print(WELCOME_HELP_TEXT)
        else:
            print(f"Неизвестная команда: {command}")


def run():
    db_path = get_db_path()
    print(HELP_TEXT)

    while True:
        metadata = load_metadata(db_path)
        user_input = input(">>> Введите команду: ").strip()

        if not user_input:
            continue

        try:
            command = _dispatch(user_input, metadata, db_path)
            if command == "exit":
                print("До встречи!")
                break
        except ValueError as e:
            print(f"Некорректное значение: {e}. Попробуйте снова.")


def _dispatch(user_input: str, metadata: dict, db_path: str):
    parts = user_input.split(maxsplit=1)
    command = parts[0]
    rest = parts[1] if len(parts) > 1 else ""

    if command == "exit":
        return "exit"

    elif command == "help":
        print(HELP_TEXT)

    elif command == "list_tables":
        core.list_tables(metadata)

    elif command == "create_table":
        args = shlex.split(rest)
        if not args:
            print("Некорректное значение: нужно указать имя таблицы. Попробуйте снова.")
            return
        table_name, *columns = args
        result = core.create_table(metadata, table_name, columns)
        if result is not None:
            metadata = result
            save_metadata(db_path, metadata)

    elif command == "drop_table":
        args = shlex.split(rest)
        if len(args) != 1:
            print("Некорректное значение: нужно указать имя таблицы. Попробуйте снова.")
            return
        table_name = args[0]
        result = core.drop_table(metadata, table_name)
        if result is not None:
            metadata = result
            save_metadata(db_path, metadata)
            delete_table_data(table_name)

    elif command == "insert":
        _handle_insert(rest, metadata)

    elif command == "select":
        _handle_select(rest, metadata)

    elif command == "update":
        _handle_update(rest, metadata)

    elif command == "delete":
        _handle_delete(rest, metadata)

    elif command == "info":
        table_name = rest.strip()
        table_data = load_table_data(table_name)
        core.info(metadata, table_name, table_data)

    else:
        print(f"Функции {command} нет. Попробуйте снова.")


def _handle_insert(rest: str, metadata: dict):
    if not rest.startswith("into "):
        raise ValueError(rest)
    rest = rest[len("into "):]

    if " values " not in rest:
        raise ValueError(rest)

    table_name, values_part = rest.split(" values ", 1)
    table_name = table_name.strip()
    values = parse_values(values_part)

    table_data = load_table_data(table_name)
    table_data = core.insert(metadata, table_name, values, table_data)
    save_table_data(table_name, table_data)


def _handle_select(rest: str, metadata: dict):
    if not rest.startswith("from "):
        raise ValueError(rest)
    rest = rest[len("from "):]

    if " where " in rest:
        table_name, where_part = rest.split(" where ", 1)
        where_clause = parse_condition(where_part.strip())
    else:
        table_name = rest
        where_clause = None

    table_name = table_name.strip()
    if table_name not in metadata:
        print(f"Таблица '{table_name}' не найдена.")
        return

    table_data = load_table_data(table_name)
    result = core.select(table_data, where_clause)
    core.print_records(result, metadata[table_name]["columns"])


def _handle_update(rest: str, metadata: dict):
    if " set " not in rest or " where " not in rest:
        raise ValueError(rest)

    table_name, remainder = rest.split(" set ", 1)
    set_part, where_part = remainder.split(" where ", 1)

    table_name = table_name.strip()
    if table_name not in metadata:
        print(f"Таблица '{table_name}' не найдена.")
        return

    set_clause = parse_set_clause(set_part.strip())
    where_clause = parse_condition(where_part.strip())

    table_data = load_table_data(table_name)
    table_data = core.update(table_data, set_clause, where_clause, table_name)
    save_table_data(table_name, table_data)


def _handle_delete(rest: str, metadata: dict):
    if not rest.startswith("from ") or " where " not in rest:
        raise ValueError(rest)
    rest = rest[len("from "):]

    table_name, where_part = rest.split(" where ", 1)
    table_name = table_name.strip()

    if table_name not in metadata:
        print(f"Таблица '{table_name}' не найдена.")
        return

    where_clause = parse_condition(where_part.strip())
    table_data = load_table_data(table_name)
    table_data = core.delete(table_data, where_clause, table_name)
    save_table_data(table_name, table_data)
