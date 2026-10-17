from primitive_db.decorators import (
    confirm_action,
    create_cacher,
    handle_db_errors,
    log_time,
)

SUPPORTED_TYPES = ("int", "str", "bool")

_cache_result, _clear_cache = create_cacher()

def _parse_column(column_str: str):
    if ":" not in column_str:
        raise ValueError(column_str)
    name, col_type = column_str.split(":", 1)
    name = name.strip()
    col_type = col_type.strip()
    if not name or col_type not in SUPPORTED_TYPES:
        raise ValueError(column_str)
    return name, col_type

@handle_db_errors
def create_table(metadata: dict, table_name: str, columns: list[str]) -> dict:
    if table_name in metadata:
        print(f"Таблица '{table_name}' уже существует.")
        return metadata

    parsed_columns = []
    has_id = False

    for col in columns:
        name, col_type = _parse_column(col)
        if name.lower() == "id":
            has_id = True
        parsed_columns.append({"name": name, "type": col_type})

    if not has_id:
        parsed_columns.insert(0, {"name": "ID", "type": "int"})

    metadata[table_name] = {"columns": parsed_columns}
    print(f"Таблица '{table_name}' успешно создана.")
    return metadata


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata: dict, table_name: str) -> dict:
    if table_name not in metadata:
        raise KeyError(table_name)
    del metadata[table_name]
    print(f"Таблица '{table_name}' удалена.")
    _clear_cache()
    return metadata


def list_tables(metadata: dict) -> None:
    from prettytable import PrettyTable

    if not metadata:
        print("Таблиц пока нет.")
        return

    table = PrettyTable()
    table.field_names = ["Таблица", "Столбцы"]
    for name, info_ in metadata.items():
        cols = ", ".join(f"{c['name']}:{c['type']}" for c in info_["columns"])
        table.add_row([name, cols])
    print(table)


def _cast_value(value: str, col_type: str):
    if col_type == "int":
        return int(value)
    elif col_type == "bool":
        if value.lower() in ("true", "1"):
            return True
        elif value.lower() in ("false", "0"):
            return False
        raise ValueError(value)
    else:
        return str(value)


@handle_db_errors
@log_time
def insert(metadata: dict, table_name: str, values: list, table_data: list) -> list:
    if table_name not in metadata:
        raise KeyError(table_name)

    columns = metadata[table_name]["columns"]
    data_columns = columns[1:]

    if len(values) != len(data_columns):
        raise ValueError(
            f"ожидалось {len(data_columns)} значений, получено {len(values)}"
        )

    new_record = {}
    for col, raw_value in zip(data_columns, values):
        new_record[col["name"]] = _cast_value(raw_value, col["type"])

    existing_ids = [row["ID"] for row in table_data]
    new_id = max(existing_ids) + 1 if existing_ids else 1

    final_record = {"ID": new_id}
    final_record.update(new_record)
    table_data.append(final_record)

    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')
    _clear_cache()
    return table_data


@handle_db_errors
@log_time
def select(table_data: list, where_clause: dict | None = None) -> list:
    cache_key = tuple(sorted(where_clause.items())) if where_clause else None

    def compute():
        if where_clause is None:
            return table_data
        result = []
        for row in table_data:
            match = all(str(row.get(k)) == str(v) for k, v in where_clause.items())
            if match:
                result.append(row)
        return result

    return _cache_result(cache_key, compute)


@handle_db_errors
def update(table_data: list, set_clause: dict, where_clause: dict, table_name: str
) -> list:
    updated_ids = []
    for row in table_data:
        match = all(str(row.get(k)) == str(v) for k, v in where_clause.items())
        if match:
            for key, value in set_clause.items():
                current_value = row.get(key)
                if isinstance(current_value, bool):
                    row[key] = value.lower() in ("true", "1")
                elif isinstance(current_value, int):
                    row[key] = int(value)
                else:
                    row[key] = value
            updated_ids.append(row["ID"])

    if updated_ids:
        for rid in updated_ids:
            print(f'Запись с ID={rid} в таблице "{table_name}" успешно обновлена.')
        _clear_cache()
    else:
        print("Записи, подходящие под условие, не найдены.")

    return table_data


@handle_db_errors
@confirm_action("удаление записи")
def delete(table_data: list, where_clause: dict, table_name: str) -> list:
    to_keep = []
    deleted_ids = []
    for row in table_data:
        match = all(str(row.get(k)) == str(v) for k, v in where_clause.items())
        if match:
            deleted_ids.append(row["ID"])
        else:
            to_keep.append(row)

    if deleted_ids:
        for rid in deleted_ids:
            print(f'Запись с ID={rid} успешно удалена из таблицы "{table_name}".')
        _clear_cache()
    else:
        print("Записи, подходящие под условие, не найдены.")

    return to_keep


@handle_db_errors
def info(metadata: dict, table_name: str, table_data: list) -> None:
    if table_name not in metadata:
        raise KeyError(table_name)

    columns = metadata[table_name]["columns"]
    cols_str = ", ".join(f"{c['name']}:{c['type']}" for c in columns)
    print(f"Таблица: {table_name}")
    print(f"Столбцы: {cols_str}")
    print(f"Количество записей: {len(table_data)}")


def print_records(table_data: list, columns: list) -> None:
    from prettytable import PrettyTable

    if not table_data:
        print("Записи не найдены.")
        return

    pt = PrettyTable()
    pt.field_names = [c["name"] for c in columns]
    for row in table_data:
        pt.add_row([row.get(c["name"]) for c in columns])
    print(pt)







