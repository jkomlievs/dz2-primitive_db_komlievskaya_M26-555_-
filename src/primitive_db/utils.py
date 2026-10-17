import json
import os


def load_metadata(filepath: str) -> dict:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


def save_metadata(filepath: str, data: dict) -> None:
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_db_path() -> str:
    home = os.path.expanduser("~")
    db_dir = os.path.join(home, ".primitive_db")
    os.makedirs(db_dir, exist_ok=True)
    return os.path.join(db_dir, "db_meta.json")


def get_data_dir() -> str:
    home = os.path.expanduser("~")
    data_dir = os.path.join(home, ".primitive_db", "data")
    os.makedirs(data_dir, exist_ok=True)
    return data_dir


def get_table_data_path(table_name: str) -> str:
    return os.path.join(get_data_dir(), f"{table_name}.json")


def load_table_data(table_name: str) -> list:
    filepath = get_table_data_path(table_name)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []


def save_table_data(table_name: str, data: list) -> None:
    filepath = get_table_data_path(table_name)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def delete_table_data(table_name: str) -> None:
    filepath = get_table_data_path(table_name)
    if os.path.exists(filepath):
        os.remove(filepath)