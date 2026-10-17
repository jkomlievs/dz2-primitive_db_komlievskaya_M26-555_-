import shlex


def parse_values(raw: str) -> list[str]:

    raw = raw.strip()
    if raw.startswith("(") and raw.endswith(")"):
        raw = raw[1:-1]

    lexer = shlex.shlex(raw, posix=True)
    lexer.whitespace = ","
    lexer.whitespace_split = True
    values = [token.strip() for token in lexer]
    return values

def parse_condition(raw: str) -> dict:

    if "=" not in raw:
        raise ValueError(raw)

    column, value = raw.split("=", 1)
    column = column.strip()
    value = value.strip()

    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        value = value[1:-1]

    if not column:
        raise ValueError(raw)

    return {column: value}

def parse_set_clause(raw: str) -> dict:

    return parse_condition(raw)
